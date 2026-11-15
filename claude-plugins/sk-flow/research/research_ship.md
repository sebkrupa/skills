# research: ship

## Summary

| | |
|---|---|
| Active version | v3 |
| Purpose | Opens the PR and merges only when it is safe. |
| External skills | `mattpocock-skills:pr` (invoke: skill) |
| Time | estimate 2 min plus CI time |
| Tokens | estimate as v2 |
| Measured | not yet. Run `/sk-flow:eval compare ship` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v3 (2026-11-15)

**Origin**

- Article: "How the Claude Code team does code review", Addy Osmani, Morgan Westlee Lunt and Qing Wang, claude.dev blog, https://claude.dev/blog/solving-code-review-at-anthropic/, published 2026-10-15, read 2026-11-15. Evaluated with `/sk-flow:eval`; the user approved all six proposals.

**What changed compared with v2**

- Risk tier set from the changed files: High (CI, migrations, secrets, infra, auth, billing, installers), Medium (size L, `CODEOWNERS` paths, paths `REVIEW.md` or `CLAUDE.md` mark sensitive), Low (the rest).
- Only Low auto-merges after green CI. Medium and High wait for CI, then stop for a person.
- PR body gets `## Testing`, `## Risk` and `## How to revert`.

**Why**

The article's approval table (Low: none once automated checks are green, Medium: one person, High: two) and "An agent's approval never counts as a person's". "The change sets the tier, not the author." PR template: "Testing", "Risk" and "How to revert". This changes the original design decision that only `clarify` stops: L and sensitive changes now also stop at merge.

**Switch back**

Set `"version": "v2"` for this step in `workflow/pipeline.json`, or run `/sk-flow:start ship=v2 <task>` once.

### v2 (2026-11-15)

**Origin**

- Article: "Which Claude model should you build with? Fable, Opus, Sonnet, or Haiku", Addy Osmani, claude.dev blog, https://claude.dev/blog/which-claude-model-should-you-build-with/, published 2026-11-09, read 2026-11-15. Evaluated with `/sk-flow:eval`; the user chose a fixed model table over the local decision model (`/sk-dev:decision-suggest-model`), so a v1 against v2 comparison measures the routing only.

**What changed compared with v1**

- A red CI log is read by a Haiku subagent that reports job, file, test name and first error line to `RUN/ci-failure.md`.

**Why**

Article: the `log-reader` subagent example on `model: haiku`, and "keep small models on work where mistakes are cheap to spot (finding files, running tests, reading logs)".

**Switch back**

Set `"version": "v1"` for this step in `workflow/pipeline.json`, or run `/sk-flow:start ship=v1 <task>` once.

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
