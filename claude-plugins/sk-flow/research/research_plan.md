# research: plan

## Summary

| | |
|---|---|
| Active version | v1 |
| Purpose | Writes the design doc that tests and code follow. |
| External skills | `egm-draft` (invoke: read) |
| Time | estimate 5-15 min |
| Tokens | estimate 50-120k |
| Measured | not yet. Run `/sk-flow:eval compare plan` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v1 (2026-11-15)

**Origin**

- Own design, agreed in a grilling session with the user on 2026-11-15 (mattpocock-skills `grilling`).
- Elephant-Goldfish Model (EGM) by Google, https://github.com/google/elephant-goldfish-model, plugin `egm@egm` 0.1.0, read 2026-11-15 (draft).

**What it does**

- Input: the concepts brief.
- The doc gets three extra sections the next steps need: `Files to change`, `Test list`, `Out of scope`.
- Saved to `docs/designs/<date>-<slug>.md` in the target repo and committed, so it is reviewable in the PR and `egm-drift-report` can check it later.

**Why**

A written plan with a test list gives TDD a scope and QA a reference.
