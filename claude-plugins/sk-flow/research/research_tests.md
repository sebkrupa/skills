# research: tests

## Summary

| | |
|---|---|
| Active version | v1 |
| Purpose | Writes failing tests that define done (TDD red). |
| External skills | `mattpocock-skills:tdd` (invoke: skill) |
| Time | estimate 3-15 min |
| Tokens | estimate 30-100k |
| Measured | not yet. Run `/sk-flow:eval compare tests` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v1 (2026-11-15)

**Origin**

- Own design, agreed in a grilling session with the user on 2026-11-15 (mattpocock-skills `grilling`).
- Matt Pocock skills, `tdd`, https://github.com/mattpocock/skills, plugin 1.3.1, read 2026-11-15.

**What it does**

- M, L: one test per line of the design doc's test list. S: the smallest set; a bug gets one regression test.
- Each new test must fail for the expected reason; existing tests keep the baseline.
- Committed as `test: <task>` before any production code.

**Why**

Tests written before code test behavior, not the implementation, and give QA a hard pass/fail signal.
