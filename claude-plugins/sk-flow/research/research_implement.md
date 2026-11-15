# research: implement

## Summary

| | |
|---|---|
| Active version | v1 |
| Purpose | Makes the tests pass with the smallest correct change. |
| External skills | `agent-skills:incremental-implementation` (invoke: skill) |
| Time | estimate 5-40 min |
| Tokens | estimate 50-300k |
| Measured | not yet. Run `/sk-flow:eval compare implement` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v1 (2026-11-15)

**Origin**

- Own design, agreed in a grilling session with the user on 2026-11-15 (mattpocock-skills `grilling`).
- Addy Osmani agent-skills, `incremental-implementation`, plugin `agent-skills@addy-agent-skills` 0.6.13, read 2026-11-15.

**What it does**

- Thin slices; each slice is tested and committed.
- Never weakens a test to pass. Design gaps are logged; behavior changes the user agreed on stop the run.
- In a fix loop it fixes only critical and important QA findings or the CI failure.

**Why**

Small verified slices keep failures local and the history reviewable.
