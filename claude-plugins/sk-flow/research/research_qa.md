# research: qa

## Summary

| | |
|---|---|
| Active version | v1 |
| Purpose | Independent check of the change by a reviewer that did not write it. |
| External skills | `agent-skills:code-reviewer` (invoke: agent), `egm-drift-report` (invoke: read, M and L) |
| Time | estimate 3-10 min |
| Tokens | estimate 60-150k (fresh subagent rebuilds context) |
| Measured | not yet. Run `/sk-flow:eval compare qa` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v1 (2026-11-15)

**Origin**

- Own design, agreed in a grilling session with the user on 2026-11-15 (mattpocock-skills `grilling`).
- Addy Osmani agent-skills, `code-reviewer` agent, read 2026-11-15.
- Elephant-Goldfish Model (EGM) by Google, https://github.com/google/elephant-goldfish-model, plugin `egm@egm` 0.1.0, read 2026-11-15 (drift report).

**What it does**

- The reviewer is a fresh subagent: it gets the base and head commits, the design doc, analysis and test notes, and runs every command itself. It is not told what the main thread suspects.
- egm-drift-report compares the design doc with the built code.
- Verdict FAIL on a failing command, a critical or important finding, or drift. Nits do not fail QA.

**Why**

A model grading its own work misses its own blind spots. Drift check catches 'built something other than designed'.
