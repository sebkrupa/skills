# research: analyze

## Summary

| | |
|---|---|
| Active version | v1 |
| Purpose | Reads the task and the repo, records commands, CI and EGM doc state, sets the size, creates the task branch. |
| External skills | `egm-bootstrap` (M, L, only when EGM READMEs are missing; separate PR) |
| Time | estimate 2-5 min; plus 10-30 min when bootstrap runs |
| Tokens | estimate 20-60k; bootstrap adds 100k+ |
| Measured | not yet. Run `/sk-flow:eval compare analyze` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v1 (2026-11-15)

**Origin**

- Own design, agreed in a grilling session with the user on 2026-11-15 (mattpocock-skills `grilling`).
- Elephant-Goldfish Model (EGM) by Google, https://github.com/google/elephant-goldfish-model, plugin `egm@egm` 0.1.0, read 2026-11-15 (bootstrap).

**What it does**

- Facts come from the repo, never from the user: default branch, stack, test/lint/type check/build commands, CI presence, `gh` auth, touched files.
- Runs the test command once for a baseline.
- Size S/M/L with a one-line reason. The user can override with `size=`.
- egm-bootstrap writes EGM READMEs for the touched folders as a separate PR, so the task diff stays small and later Goldfish reviewers get codebase context.

**Why**

Later steps need exact commands and the size. Bootstrap is a separate PR because it can be a big unrelated diff.
