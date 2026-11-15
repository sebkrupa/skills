# research: design-review

## Summary

| | |
|---|---|
| Active version | v1 |
| Purpose | Zero-context reviewers find gaps in the design doc before code exists. |
| External skills | `egm-review`, `egm-resolve` (invoke: read) |
| Time | estimate 10-25 min |
| Tokens | estimate 150-400k (several fresh-context reviewer subagents) |
| Measured | not yet. Run `/sk-flow:eval compare design-review` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v1 (2026-11-15)

**Origin**

- Own design, agreed in a grilling session with the user on 2026-11-15 (mattpocock-skills `grilling`).
- Elephant-Goldfish Model (EGM) by Google, https://github.com/google/elephant-goldfish-model, plugin `egm@egm` 0.1.0, read 2026-11-15 (Goldfish review protocol: zoom out, comprehension, design critique, implementation readiness).

**What it does**

- egm-review runs five sequential review stages with fresh subagents that see only the doc.
- egm-resolve applies PROPOSE FIX items. Gates are auto-accepted unless high severity; scope changes always stop.
- Output: `RUN/design-review.md` and the fixed doc, committed.

**Why**

Fixing a design gap costs minutes; fixing it after implementation costs a rewrite. Reviewers without context catch unstated assumptions.
