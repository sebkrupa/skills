# research: clarify

## Summary

| | |
|---|---|
| Active version | v1 |
| Purpose | Agrees with the user what to build. The one planned stop. |
| External skills | `egm-brainstorm` (invoke: read) |
| Time | depends on the user; estimate 5-20 min |
| Tokens | estimate 30-80k (includes a Goldfish review of the brief) |
| Measured | not yet. Run `/sk-flow:eval compare clarify` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v1 (2026-11-15)

**Origin**

- Own design, agreed in a grilling session with the user on 2026-11-15 (mattpocock-skills `grilling`).
- Elephant-Goldfish Model (EGM) by Google, https://github.com/google/elephant-goldfish-model, plugin `egm@egm` 0.1.0, read 2026-11-15 (brainstorm).

**What it does**

- egm-brainstorm asks clarifying questions in rounds and runs a zero-context Goldfish review of the concept.
- Output: `RUN/concepts_brief.md`.
- egm-brainstorm would offer `/egm-draft` next; the step stops it there because `plan` owns drafting.

**Why**

Wrong requirements are the most expensive error. One early stop replaces many later ones.
