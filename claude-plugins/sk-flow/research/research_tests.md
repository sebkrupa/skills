# research: tests

## Summary

| | |
|---|---|
| Active version | v2 |
| Purpose | Writes failing tests that define done (TDD red). |
| External skills | `mattpocock-skills:tdd` (invoke: skill) |
| Time | estimate 3-15 min |
| Tokens | estimate 30-100k plus 20-40k context rebuild; S on Sonnet costs about half of Opus per token |
| Measured | not yet. Run `/sk-flow:eval compare tests` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v2 (2026-11-15)

**Origin**

- Article: "Which Claude model should you build with? Fable, Opus, Sonnet, or Haiku", Addy Osmani, claude.dev blog, https://claude.dev/blog/which-claude-model-should-you-build-with/, published 2026-11-09, read 2026-11-15. Evaluated with `/sk-flow:eval`; the user chose a fixed model table over the local decision model (`/sk-dev:decision-suggest-model`), so a v1 against v2 comparison measures the routing only.

**What changed compared with v1**

- Runs as a subagent: S on Sonnet medium, M on Opus medium, L on Opus high.
- Does not ask the user; ends with `STOP: <reason>` when the test list cannot be tested.

**Why**

Article table: "Well-scoped coding: bug fixes, feature iteration, spec-driven work → Sonnet 5.5, medium"; "Everyday engineering → Opus 5.5, medium, then high". S tasks are the well-scoped ones.

**Switch back**

Set `"version": "v1"` and `"model": "main"` for this step in `workflow/pipeline.json`, or run `/sk-flow:start tests=v1 tests.model=main <task>` once. v1 expects the main thread (it may ask the user), so it needs `main`.

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
