# research: simplify

## Summary

| | |
|---|---|
| Active version | v1 |
| Purpose | Makes the task's diff smaller and clearer before QA, with no change of behavior. |
| External skills | `agent-skills:code-simplification` (invoke: skill) |
| Time | estimate 3-8 min |
| Tokens | estimate 40-100k on Sonnet |
| Measured | not yet. Run `/sk-flow:eval compare simplify` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v1 (2026-11-15)

**Origin**

- Article: "How the Claude Code team does code review", Addy Osmani, Morgan Westlee Lunt and Qing Wang, claude.dev blog, https://claude.dev/blog/solving-code-review-at-anthropic/, published 2026-10-15, read 2026-11-15. Evaluated with `/sk-flow:eval`; the user approved all six proposals.

**What it does**

- Runs between `implement` and `qa`, for M and L, once per run (fix loops skip it).
- A Sonnet medium subagent follows `code-simplification` on the task's changed lines only: removes dead code and duplication the task added, reuses existing helpers, flattens needless abstraction.
- No behavior, interface, test or design changes, and no bug fixes.
- Runs every command afterwards; on any failure it discards its changes. At most one `refactor:` commit. Report in `RUN/simplify.md`.

**Why**

The article lists internal skills that run before a PR: "one hunts for bugs, one simplifies the diff, and one checks behavior end to end." A smaller diff gives QA less to review and the human a smaller PR. Sonnet because the article puts well-scoped, spec-driven code work on Sonnet 5.5, and QA runs after this step to catch any mistake.

**Switch off**

Set `"enabled": false` for `simplify` in `workflow/pipeline.json`.
