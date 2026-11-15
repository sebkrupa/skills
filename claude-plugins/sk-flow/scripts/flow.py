#!/usr/bin/env python3
"""sk-flow helper: pipeline resolution, external skill healthchecks, step timing and token metrics.

Standard library only. Commands:
  root                                  definitions folder (repo source if found, else the installed plugin)
  pipeline [size] [step=vN ...]         resolved steps as JSON (size: S, M or L)
  health [step ...]                     check external skills used by these steps (default: all enabled steps)
  health-set <id> OK|FAIL [error]       record a check done by the model
  mark <run_dir> <step> <version> start|end
  metrics <run_dir>                     tokens and time per step, appended to the state log
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
        out["steps"].append({"name": s["name"], "version": v, "file": f, "skip": skip,
                             "external": s.get("external", [])})
    return out


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


def mark(run_dir, step, version, edge):
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, "marks.jsonl"), "a") as f:
        f.write(json.dumps({"ts": now(), "step": step, "version": version, "edge": edge}) + "\n")


def intervals(marks):
    """Pair start/end marks per step. Repeated steps (fix loops) give several intervals."""
    open_, out = {}, []
    for m in marks:
        if m["edge"] == "start":
            open_[m["step"]] = m
        elif m["step"] in open_:
            s = open_.pop(m["step"])
            out.append((m["step"], s["version"], s["ts"], m["ts"]))
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
                yield e["timestamp"], u


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


def metrics(run_dir, files=None):
    marks = [json.loads(l) for l in open(os.path.join(run_dir, "marks.jsonl")) if l.strip()]
    files = transcripts(run_dir) if files is None else files
    entries = list(usage_entries(files))
    per = {}
    for step, ver, a, b in intervals(marks):
        r = per.setdefault((step, ver), {"step": step, "version": ver, "seconds": 0.0, "runs": 0, "input": 0,
                                         "output": 0, "cache_read": 0, "cache_write": 0})
        r["runs"] += 1
        r["seconds"] += (parse(b) - parse(a)).total_seconds()
        for ts, u in entries:
            if a <= ts <= b:  # same ISO-8601 UTC format, so string order is time order
                r["input"] += u.get("input_tokens", 0) or 0
                r["output"] += u.get("output_tokens", 0) or 0
                r["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
                r["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0
    rows = list(per.values())
    run = os.path.basename(os.path.normpath(run_dir))
    save(os.path.join(run_dir, "metrics.json"), {"run": run, "transcripts": files, "steps": rows})
    os.makedirs(STATE, exist_ok=True)
    with open(os.path.join(STATE, "log.jsonl"), "a") as f:
        for r in rows:
            f.write(json.dumps(dict(r, run=run, ts=now())) + "\n")
    return rows


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
        lines = [{"type": "assistant", "timestamp": "2026-01-01T00:00:30.000Z", "message": {"id": "a", "usage": u}},
                 {"type": "assistant", "timestamp": "2026-01-01T00:00:31.000Z", "message": {"id": "a", "usage": u}},
                 {"type": "assistant", "timestamp": "2026-01-01T00:02:10.000Z", "message": {"id": "b", "usage": u}},
                 {"type": "assistant", "timestamp": "2026-01-01T00:05:00.000Z", "message": {"id": "c", "usage": u}}]
        with open(tr, "w") as f:
            f.write("".join(json.dumps(l) + "\n" for l in lines))
        r = metrics(run, [tr])[0]
        assert (r["runs"], r["seconds"], r["input"], r["output"], r["cache_read"]) == (2, 90.0, 20, 10, 200), r
        assert len(open(os.path.join(STATE, "log.jsonl")).readlines()) == 1
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
    elif a[0] == "mark" and len(a) == 5:
        mark(*a[1:])
    elif a[0] == "metrics" and len(a) == 2:
        print(json.dumps(metrics(a[1]), indent=2))
    else:
        raise SystemExit("bad command, see --help")


if __name__ == "__main__":
    main(sys.argv[1:])
