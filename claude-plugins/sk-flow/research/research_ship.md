# research: ship

## Summary

| | |
|---|---|
| Active version | v1 |
| Purpose | Opens the PR and merges only when it is safe. |
| External skills | `mattpocock-skills:pr` (invoke: skill) |
| Time | estimate 2 min plus CI time |
| Tokens | estimate 10-30k |
| Measured | not yet. Run `/sk-flow:eval compare ship` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v1 (2026-11-15)

**Origin**

- Own design, agreed in a grilling session with the user on 2026-11-15 (mattpocock-skills `grilling`).
- Matt Pocock skills, `pr`, read 2026-11-15.

**What it does**

- PR body includes the design doc link, the test list, the QA verdict, remaining nits and the egm gate decisions.
- No merge without CI, without checks, or when protected paths change (`.github/`, CI config, migrations, env and secret files, infrastructure code). Then it stops with the PR link.
- Waits for checks; red CI starts a fix loop. Squash merge, branch deleted. Never `--admin`.

**Why**

Auto-merge is safe only when CI is the gate. Without CI a human is the gate.
