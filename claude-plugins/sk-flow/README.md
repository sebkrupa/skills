# sk-flow

A versioned development workflow for Claude Code. One command runs a task (feature or bug fix) from analysis to a merged PR. A second command checks new ideas against the workflow and adds them as new step versions.

| Command | What it does |
|---|---|
| `/sk-flow:start [size=S\|M\|L] [<step>=vN ...] [orchestrator=vN] <task>` | Runs the task through the pipeline. |
| `/sk-flow:eval <url \| file \| text> [question]` | Evaluates an idea: modify a step, add a step, replace a step, change the orchestrator, or reject. Applies it after your approval. |
| `/sk-flow:eval compare <step>` | Compares measured time and tokens of the versions of a step. |

## Pipeline

| # | Step | Active | Sizes | External skills | Output |
|---|---|---|---|---|---|
| 1 | analyze | v1 | S M L | egm-bootstrap (only M/L without EGM READMEs, separate PR) | `analysis.md`, size, task branch |
| 2 | clarify | v1 | M L | egm-brainstorm | `concepts_brief.md` (the one planned stop) |
| 3 | plan | v1 | M L | egm-draft | `docs/designs/<date>-<slug>.md` |
| 4 | design-review | v1 | M L | egm-review, egm-resolve | fixed design doc |
| 5 | tests | v1 | S M L | mattpocock-skills:tdd | failing tests |
| 6 | implement | v1 | S M L | agent-skills:incremental-implementation | passing code |
| 7 | qa | v1 | S M L | agent-skills:code-reviewer (fresh subagent), egm-drift-report (M/L) | `qa.md` PASS/FAIL |
| 8 | ship | v1 | S M L | mattpocock-skills:pr | PR, merged when CI is green |

Orchestrator: v1. Details of every step, its origin and its cost are in [`research`](research).

## Rules of a run

- **Stops**: only at `clarify`, at high-severity egm gates, on a healthcheck FAIL, after 2 fix loops, and before a merge that is not safe. A run also refuses a dirty working tree.
- **Size**: `analyze` sets S, M or L. S (1-2 files, clear intent) skips clarify, plan and design-review. Bug fixes use the same pipeline.
- **egm gates**: the recommended option is taken and logged in `run.md`, unless the finding is high severity or changes scope.
- **Fix loops**: QA FAIL or red CI go back to `implement`. At most 2 loops per run.
- **Merge**: only with CI and green checks, and not when the PR changes `.github/`, CI config, migrations, env or secret files, or infrastructure code. Otherwise the PR stays open and the run reports why.
- **Run files**: `.sk-flow/runs/<date>-<slug>/` in the target repo, hidden with `.git/info/exclude`. The design doc is committed in `docs/designs/`.

## Versions

```
workflow/
  pipeline.json                     step order, active version, enabled, run_for, external skills
  external_skills.json              every external skill and how to call it
  orchestrator/orchestrator_v1.md
  steps/<step>/<step>_v1.md, <step>_v2.md, ...
research/research_<step>.md          summary, then one section per version
scripts/flow.py                      pipeline, healthcheck, marks, metrics
```

- A change never edits a version file. `eval` copies `qa_v1.md` to `qa_v2.md`, changes the copy, and sets `"version": "v2"` in `pipeline.json`.
- Switch back for good: set the old version in `pipeline.json`.
- Switch back for one run: `/sk-flow:start qa=v1 <task>`.
- A step added by `eval` is turned off with `"enabled": false`.
- Delete old version files by hand when you no longer need them.
- `start` reads the definitions from the repo folder of the `skrupa-skills` marketplace when it has `sk-flow`, so a switch in the repo works without reinstalling. Otherwise it uses the installed plugin.

## External skills and healthcheck

`workflow/external_skills.json` lists every external skill. `invoke` says how it is called:

- `skill`: the Skill tool.
- `agent`: a subagent type.
- `read`: the workflow reads the skill's `SKILL.md` from the plugin folder and follows it. egm skills need this, because they set `disable-model-invocation: true` and the Skill tool refuses them.

Health status is per machine, in `~/.claude/sk-flow/state/health.json`:

- Blank: never checked. The next run checks it before step 1.
- OK: checked. Not checked again until the plugin version changes.
- FAIL: the run stops and prints the error and the fix (install, enable, or switch to `invoke: read`). A skill that fails during a run is set to FAIL with the exact error.

Check by hand:

```bash
python3 claude-plugins/sk-flow/scripts/flow.py health
python3 claude-plugins/sk-flow/scripts/flow.py pipeline S
python3 claude-plugins/sk-flow/scripts/flow.py --self-test
```

Required plugins: `egm@egm`, `mattpocock-skills`, `agent-skills@addy-agent-skills`. The install commands are in `external_skills.json`. The `gh` CLI must be logged in for `ship`.

## Metrics

Each step writes start and end marks to `run/marks.jsonl`. At the end, `flow.py metrics` finds the session transcript in `~/.claude/projects/` (and its subagent transcripts) and sums input, output and cache tokens and the wall time per step and version. The result is in `run/metrics.json` and appended to `~/.claude/sk-flow/state/log.jsonl`. `/sk-flow:eval compare <step>` reads this log.

Limits: tokens of a step include everything in that time window. Steps in parallel would be counted twice; v1 runs them in sequence.
