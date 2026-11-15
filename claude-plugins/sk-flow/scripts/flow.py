#!/usr/bin/env python3
"""sk-flow helper: pipeline resolution, external skill healthchecks, step timing and token metrics.

Standard library only. Commands:
  root                                  definitions folder (repo source if found, else the installed plugin)
  pipeline [size] [step=vN ...] [step.model=m:effort] [step.effort=e]
                                        resolved steps with model and effort as JSON (size: S, M or L)
  health [step ...]                     check external skills used by these steps (default: all enabled steps)
  health-set <id> OK|FAIL [error]       record a check done by the model
  mark <run_dir> <step> <version> start|end [model] [effort]
  escalate <model> <effort>             next rung of the fix-loop ladder
  metrics <run_dir>                     tokens, time, estimated USD and QA counts per step, appended to the state log
  findings <run_dir> <repo>             record confirmed bug classes; print classes seen in 2+ runs of the repo
  --self-test
"""
import glob
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAUDE = os.path.expanduser("~/.claude")
STATE = os.environ.get("SK_FLOW_STATE", os.path.join(CLAUDE, "sk-flow", "state"))
MARKET = "skrupa-skills"  # "name" in claude-plugins/.claude-plugin/marketplace.json


def now():
    # millisecond ISO-8601 UTC, the transcript format, so timestamps compare as strings
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:23] + "Z"


def load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def root():
    """Repo source wins, so a version switch in the repo works without reinstalling the plugin."""
    env = os.environ.get("SK_FLOW_ROOT")
    if env:
        return env
    m = load(os.path.join(CLAUDE, "plugins", "known_marketplaces.json"), {}).get(MARKET) or {}
    src = os.path.join(m.get("installLocation", ""), "sk-flow")
    if os.path.isfile(os.path.join(src, "workflow", "pipeline.json")):
        return src
    return PLUGIN_DIR


def pipeline(args):
    r = root()
    p = load(os.path.join(r, "workflow", "pipeline.json"))
    size, over = None, {}
    for a in args:
        if "=" in a:
            k, v = a.split("=", 1)
            if k == "size":
                size = v.upper()
            else:
                over[k] = v
        else:
            size = a.upper()
    out = {"root": r, "size": size, "orchestrator": over.get("orchestrator", p["orchestrator"]), "steps": []}
    out["orchestrator_file"] = os.path.join(r, "workflow", "orchestrator", "orchestrator_%s.md" % out["orchestrator"])
    for s in p["steps"]:
        v = over.get(s["name"], s["version"])
        f = os.path.join(r, "workflow", "steps", s["name"], "%s_%s.md" % (s["name"], v))
        skip = None
        if not s.get("enabled", True):
            skip = "disabled"
        elif size and size not in s.get("run_for", ["S", "M", "L"]):
            skip = "size %s" % size
        if not os.path.isfile(f):
            raise SystemExit("missing step file: %s" % f)
        model, effort, inline = resolve_model(s, size, over, p.get("main_model", "opus:medium"))
        out["steps"].append({"name": s["name"], "version": v, "file": f, "skip": skip,
                             "external": s.get("external", []), "model": model, "effort": effort,
                             "inline": inline})
    return out


def resolve_model(step, size, over, main):
    """(model, effort, inline). "main" runs in the main thread; anything else runs in a subagent."""
    spec = over.get(step["name"] + ".model", step.get("model", "main"))
    inline = spec == "main"
    if inline:
        spec = main
    elif isinstance(spec, dict):
        spec = spec.get(size) if size else None  # unknown until analyze sets the size
    if spec is None:
        return None, None, inline
    model, _, effort = spec.partition(":")
    return model, over.get(step["name"] + ".effort", effort or "medium"), inline


MODELS = ["haiku", "sonnet", "opus", "fable"]
EFFORTS = ["low", "medium", "high", "xhigh", "max"]


def escalate(model, effort):
    """One rung of the ladder: raise effort up to high, past that move one model up at medium."""
    if EFFORTS.index(effort) < EFFORTS.index("high"):
        return model, EFFORTS[EFFORTS.index(effort) + 1]
    if model != MODELS[-1]:
        return MODELS[MODELS.index(model) + 1], "medium"
    return model, EFFORTS[min(EFFORTS.index(effort) + 1, EFFORTS.index("xhigh"))]


def plugin_install(name):
    """(version, installPath) of an installed plugin, matched by name in any marketplace."""
    d = load(os.path.join(CLAUDE, "plugins", "installed_plugins.json"), {}).get("plugins", {})
    for key, entries in sorted(d.items()):
        if key.split("@")[0] == name and entries:
            return entries[0].get("version"), entries[0].get("installPath")
    return None, None


def health(steps):
    reg = load(os.path.join(root(), "workflow", "external_skills.json"))["skills"]
    state_path = os.path.join(STATE, "health.json")
    st = load(state_path, {})
    want = set()
    if steps:
        want = {e for s in pipeline([])["steps"] if s["name"] in steps for e in s["external"]}
    else:
        want = {e for s in pipeline([])["steps"] if s["skip"] is None for e in s["external"]}
    rows = []
    for sk in reg:
        if sk["id"] not in want:
            continue
        ver, path = plugin_install(sk["plugin"])
        h = st.get(sk["id"], {})
        if h.get("plugin_version") != ver:  # plugin updated, removed or never checked: check again
            h = {"status": "", "plugin_version": ver}
        if ver is None:
            h.update(status="FAIL", checked_at=now(), error="plugin %s not installed" % sk["plugin"])
        elif sk["invoke"] == "read" and h.get("status") != "OK":
            f = os.path.join(path, sk["name"])
            ok = os.path.isfile(f) and os.access(f, os.R_OK)
            h.update(status="OK" if ok else "FAIL", checked_at=now(), error=None if ok else "missing %s" % f)
        st[sk["id"]] = h
        rows.append(dict(sk, status=h["status"], error=h.get("error"), plugin_version=ver,
                         path=os.path.join(path, sk["name"]) if path and sk["invoke"] == "read" else None))
    save(state_path, st)
    return rows


def health_set(sid, status, error=None):
    state_path = os.path.join(STATE, "health.json")
    st = load(state_path, {})
    reg = {s["id"]: s for s in load(os.path.join(root(), "workflow", "external_skills.json"))["skills"]}
    if sid not in reg:
        raise SystemExit("unknown skill id: %s" % sid)
    ver, _ = plugin_install(reg[sid]["plugin"])
    st[sid] = {"status": status, "checked_at": now(), "plugin_version": ver, "error": error}
    save(state_path, st)


def mark(run_dir, step, version, edge, model=None, effort=None):
    os.makedirs(run_dir, exist_ok=True)
    m = {"ts": now(), "step": step, "version": version, "edge": edge, "model": model, "effort": effort}
    with open(os.path.join(run_dir, "marks.jsonl"), "a") as f:
        f.write(json.dumps(m) + "\n")


def intervals(marks):
    """Pair start/end marks per step. Repeated steps (fix loops) give several intervals."""
    open_, out = {}, []
    for m in marks:
        if m["edge"] == "start":
            open_[m["step"]] = m
        elif m["step"] in open_:
            s = open_.pop(m["step"])
            out.append((m["step"], s["version"], s.get("model"), s.get("effort"), s["ts"], m["ts"]))
    return out


def usage_entries(files):
    seen = set()
    for fp in files:
        with open(fp, errors="replace") as f:
            for line in f:
                if '"usage"' not in line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                msg = e.get("message") or {}
                u = msg.get("usage")
                key = (fp, msg.get("id"))
                if not u or e.get("type") != "assistant" or key in seen:
                    continue  # one API message is logged once per content block with the same usage
                seen.add(key)
                yield e["timestamp"], msg.get("model"), u


def transcripts(run_dir):
    """Session transcript that ran this run (it contains the run_dir in a mark command), plus its subagents."""
    marks_ts = os.path.getmtime(os.path.join(run_dir, "marks.jsonl"))
    needle = os.path.basename(os.path.normpath(run_dir))
    hits = []
    for fp in glob.glob(os.path.join(CLAUDE, "projects", "*", "*.jsonl")):
        if os.path.getmtime(fp) < marks_ts - 86400 * 7:
            continue
        with open(fp, errors="replace") as f:
            if needle in f.read():
                hits.append(fp)
    if not hits:
        return []
    main = max(hits, key=os.path.getmtime)
    return [main] + glob.glob(os.path.join(main[:-6], "subagents", "*.jsonl"))


def cost(model_id, u, prices):
    """Estimated USD for one API message, or None for an unknown model (for example <synthetic>)."""
    fam = next((m for m in MODELS if m in (model_id or "")), None)
    pr = prices.get("models", {}).get(fam)
    if not pr:
        return None
    i, o = u.get("input_tokens", 0) or 0, u.get("output_tokens", 0) or 0
    cr, cw = u.get("cache_read_input_tokens", 0) or 0, u.get("cache_creation_input_tokens", 0) or 0
    if "long" in pr and i + cr + cw > pr["long_prompt"]:
        pr = dict(pr, **pr["long"])
    # shortcut: cache writes priced at 1.25 x input (5-minute cache); 1-hour writes cost more, split them if it matters
    return (i * pr["input"] + o * pr["output"] + cr * pr["cache_read"] + cw * pr["input"] * 1.25) / 1e6


def metrics(run_dir, files=None):
    marks = [json.loads(l) for l in open(os.path.join(run_dir, "marks.jsonl")) if l.strip()]
    files = transcripts(run_dir) if files is None else files
    entries = list(usage_entries(files))
    prices = load(os.path.join(root(), "workflow", "prices.json"), {})
    per = {}
    for step, ver, model, effort, a, b in intervals(marks):
        r = per.setdefault((step, ver, model, effort), {
            "step": step, "version": ver, "model": model, "effort": effort, "seconds": 0.0, "runs": 0,
            "input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "cost_usd": 0.0, "by_model": {}})
        r["runs"] += 1
        r["seconds"] += (parse(b) - parse(a)).total_seconds()
        for ts, mid, u in entries:
            if a <= ts <= b:  # same ISO-8601 UTC format, so string order is time order
                bm = r["by_model"].setdefault(mid or "unknown", {"tokens": 0, "cost_usd": 0.0})
                for k, uk in (("input", "input_tokens"), ("output", "output_tokens"),
                              ("cache_read", "cache_read_input_tokens"), ("cache_write", "cache_creation_input_tokens")):
                    n = u.get(uk, 0) or 0
                    r[k] += n
                    bm["tokens"] += n
                c = cost(mid, u, prices) or 0.0
                r["cost_usd"] += c
                bm["cost_usd"] += c
    rows = list(per.values())
    qa = qa_counts(run_dir)
    for r in rows:
        if r["step"] == "qa" and qa:
            r.update(qa)
            qa = None  # attach once, also when qa ran on several models
        r["cost_usd"] = round(r["cost_usd"], 4)
        for bm in r["by_model"].values():
            bm["cost_usd"] = round(bm["cost_usd"], 4)
    run = os.path.basename(os.path.normpath(run_dir))
    save(os.path.join(run_dir, "metrics.json"), {"run": run, "transcripts": files, "prices_as_of": prices.get("as_of"),
                                                 "total_cost_usd": round(sum(r["cost_usd"] for r in rows), 4),
                                                 "steps": rows})
    os.makedirs(STATE, exist_ok=True)
    with open(os.path.join(STATE, "log.jsonl"), "a") as f:
        for r in rows:
            f.write(json.dumps(dict(r, run=run, ts=now(), prices_as_of=prices.get("as_of"))) + "\n")
    return rows


QA_KEYS = ["raw", "confirmed", "important", "nit", "pre_existing", "security", "disputed_upheld", "disputed_dropped"]


def qa_counts(run_dir):
    """Sum of the QA rounds in RUN/qa.json (written by qa v3), or None."""
    rounds = (load(os.path.join(run_dir, "qa.json"), {}) or {}).get("rounds") or []
    if not rounds:
        return None
    out = {"qa_" + k: sum(int(r.get(k, 0) or 0) for r in rounds) for k in QA_KEYS}
    out["qa_rounds"] = len(rounds)
    return out


def findings(run_dir, repo):
    """Record this run's confirmed bug classes; return {class: [runs]} for classes seen in 2+ runs of the repo."""
    run = os.path.basename(os.path.normpath(run_dir))
    repo = os.path.realpath(repo)
    rounds = (load(os.path.join(run_dir, "qa.json"), {}) or {}).get("rounds") or []
    path = os.path.join(STATE, "findings.jsonl")
    old = []
    if os.path.isfile(path):
        old = [json.loads(l) for l in open(path) if l.strip()]
    old = [o for o in old if o["run"] != run]  # rerunning the command for one run does not double-count it
    new = [{"repo": repo, "run": run, "class": c, "ts": now()}
           for c in sorted({c for r in rounds for c in r.get("classes", [])})]
    os.makedirs(STATE, exist_ok=True)
    with open(path, "w") as f:
        f.write("".join(json.dumps(o) + "\n" for o in old + new))
    seen = {}
    for o in old + new:
        if o["repo"] == repo:
            seen.setdefault(o["class"], set()).add(o["run"])
    return {c: sorted(r) for c, r in sorted(seen.items()) if len(r) >= 2}


def parse(ts):
    return datetime.strptime(ts[:26].rstrip("Z"), "%Y-%m-%dT%H:%M:%S.%f")


def self_test():
    global STATE
    with tempfile.TemporaryDirectory() as t:
        STATE = os.path.join(t, "state")
        run = os.path.join(t, "run-x")
        marks = [{"ts": "2026-01-01T00:00:00.000Z", "step": "qa", "version": "v1", "edge": "start"},
                 {"ts": "2026-01-01T00:01:00.000Z", "step": "qa", "version": "v1", "edge": "end"},
                 {"ts": "2026-01-01T00:02:00.000Z", "step": "qa", "version": "v1", "edge": "start"},
                 {"ts": "2026-01-01T00:02:30.000Z", "step": "qa", "version": "v1", "edge": "end"}]
        os.makedirs(run)
        with open(os.path.join(run, "marks.jsonl"), "w") as f:
            f.write("".join(json.dumps(m) + "\n" for m in marks))
        tr = os.path.join(t, "s.jsonl")
        u = {"input_tokens": 10, "output_tokens": 5, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 1}
        lines = [{"type": "assistant", "timestamp": "2026-01-01T00:00:30.000Z",
                  "message": {"id": "a", "model": "claude-opus-5-5", "usage": u}},
                 {"type": "assistant", "timestamp": "2026-01-01T00:00:31.000Z", "message": {"id": "a", "usage": u}},
                 {"type": "assistant", "timestamp": "2026-01-01T00:02:10.000Z", "message": {"id": "b", "usage": u}},
                 {"type": "assistant", "timestamp": "2026-01-01T00:05:00.000Z", "message": {"id": "c", "usage": u}}]
        with open(tr, "w") as f:
            f.write("".join(json.dumps(l) + "\n" for l in lines))
        r = metrics(run, [tr])[0]
        assert (r["runs"], r["seconds"], r["input"], r["output"], r["cache_read"]) == (2, 90.0, 20, 10, 200), r
        assert len(open(os.path.join(STATE, "log.jsonl")).readlines()) == 1
        assert r["by_model"]["claude-opus-5-5"]["tokens"] == 116 and r["cost_usd"] > 0, r
        save(os.path.join(run, "qa.json"), {"rounds": [{"raw": 5, "confirmed": 2, "classes": ["null-check"]},
                                                        {"raw": 1, "confirmed": 0, "classes": []}]})
        r = metrics(run, [tr])[0]
        assert (r["qa_raw"], r["qa_confirmed"], r["qa_rounds"]) == (6, 2, 2), r
        assert findings(run, t) == {}
        assert findings(run, t) == {}, "same run twice must not count as recurring"
        run2 = os.path.join(t, "run-y")
        save(os.path.join(run2, "qa.json"), {"rounds": [{"classes": ["null-check", "sql-injection"]}]})
        assert findings(run2, t) == {"null-check": ["run-x", "run-y"]}
    # cost: opus 1M output = $20; haiku long tier when the prompt is over 100K
    pr = load(os.path.join(root(), "workflow", "prices.json"))
    assert abs(cost("claude-opus-5-5", {"output_tokens": 1000000}, pr) - 20.0) < 1e-9
    assert abs(cost("claude-haiku-5-5", {"input_tokens": 200000}, pr) - 0.1) < 1e-9
    assert cost("<synthetic>", {"output_tokens": 5}, pr) is None
    # escalation ladder from the article: effort up to high, then one model up at medium
    assert escalate("sonnet", "medium") == ("sonnet", "high")
    assert escalate("sonnet", "high") == ("opus", "medium")
    assert escalate("opus", "high") == ("fable", "medium")
    assert escalate("fable", "high") == ("fable", "xhigh")
    imp = {s["name"]: s for s in pipeline(["S", "implement.model=fable:high"])["steps"]}
    assert (imp["implement"]["model"], imp["implement"]["effort"], imp["implement"]["inline"]) == ("fable", "high", False)
    assert imp["tests"]["model"] == "sonnet" and imp["analyze"]["inline"]
    assert pipeline([])["steps"][4]["model"] is None, "size unknown: no model yet"
    p = pipeline(["S"])
    assert p["steps"] and all(os.path.isfile(s["file"]) for s in p["steps"])
    assert any(s["skip"] for s in p["steps"]), "S should skip some steps"
    assert os.path.isfile(p["orchestrator_file"])
    print("self-test OK")


def main(a):
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
    elif a[0] == "--self-test":
        self_test()
    elif a[0] == "root":
        print(root())
    elif a[0] == "pipeline":
        print(json.dumps(pipeline(a[1:]), indent=2))
    elif a[0] == "health":
        rows = health(a[1:])
        print(json.dumps(rows, indent=2))
        sys.exit(1 if any(r["status"] == "FAIL" for r in rows) else 2 if any(not r["status"] for r in rows) else 0)
    elif a[0] == "health-set" and len(a) >= 3:
        health_set(a[1], a[2].upper(), " ".join(a[3:]) or None)
    elif a[0] == "mark" and 5 <= len(a) <= 7:
        mark(*a[1:])
    elif a[0] == "findings" and len(a) == 3:
        print(json.dumps(findings(a[1], a[2]), indent=2))
    elif a[0] == "escalate" and len(a) == 3:
        print("%s:%s" % escalate(a[1], a[2]))
    elif a[0] == "metrics" and len(a) == 2:
        print(json.dumps(metrics(a[1]), indent=2))
    else:
        raise SystemExit("bad command, see --help")


if __name__ == "__main__":
    main(sys.argv[1:])
