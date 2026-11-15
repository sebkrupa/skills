# research: orchestrator

## Summary

| | |
|---|---|
| Active version | v1 |
| Purpose | Runs the steps in order, enforces stops, healthchecks, fix loops and metrics. |
| External skills | none |
| Time | seconds of overhead per step (script calls) |
| Tokens | about 3k input tokens to read the orchestrator file |
| Measured | not yet. Run `/sk-flow:eval compare orchestrator` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v1 (2026-11-15)

**Origin**

- Own design, agreed in a grilling session with the user on 2026-11-15 (mattpocock-skills `grilling`).

**What it does**

- Setup: refuses a dirty working tree, creates `.sk-flow/runs/<date>-<slug>/` and hides it with `.git/info/exclude`.
- Healthcheck: `flow.py health` checks every external skill of enabled steps. Status is blank, OK or FAIL per machine in `~/.claude/sk-flow/state/health.json`. A plugin version change resets the status to blank. `read` skills are checked by the script (file exists). `skill` and `agent` skills are checked by the model against the session's lists. FAIL stops the run with the install or enable command.
- Autonomy: the only planned stop is `clarify`. egm gates are auto-accepted with the recommended option and logged, unless high severity.
- Size: `analyze` sets S, M or L. S skips `clarify`, `plan` and `design-review` (`run_for` in `pipeline.json`).
- Fix loops: QA FAIL or red CI go back to `implement`. At most 2 loops per run.
- Metrics: `flow.py mark` writes start and end marks; `flow.py metrics` sums tokens from the session transcript (and its subagents) between the marks.

**Why**

One pipeline for features and bug fixes. Size rules keep small fixes cheap. Per-step marks make versions comparable.
