# research: qa

## Summary

| | |
|---|---|
| Active version | v3 |
| Purpose | Independent check of the change by a reviewer that did not write it. |
| External skills | `agent-skills:code-reviewer`, `agent-skills:security-auditor` (invoke: agent), `egm-drift-report` (invoke: read, M and L) |
| Time | estimate 3-10 min |
| Tokens | estimate S +20-40k, M +80-150k, L +150-300k over v2 (reviewers and verifiers); fewer false FAIL loops should pay part of it back |
| Measured | not yet. Run `/sk-flow:eval compare qa` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v3 (2026-11-15)

**Origin**

- Article: "How the Claude Code team does code review", Addy Osmani, Morgan Westlee Lunt and Qing Wang, claude.dev blog, https://claude.dev/blog/solving-code-review-at-anthropic/, published 2026-10-15, read 2026-11-15. Evaluated with `/sk-flow:eval`; the user approved all six proposals.

**What changed compared with v2**

- Depth by size: S Quick (1 correctness reviewer, 1 verifier per finding), M Standard (correctness, system fit, security reviewers; 3 verifiers, 2 of 3), L Deep (plus a tests reviewer).
- Reviewers run in parallel as fresh subagents; verifiers are separate fresh subagents that try to prove each finding wrong.
- Style, formatting, naming, diagnostics and cleanup findings are dropped.
- Severity IMPORTANT, NIT, PRE_EXISTING (checked against the merge-base). Only IMPORTANT and non-pre-existing security findings fail QA.
- New security reviewer (`agent-skills:security-auditor`): always on M and L, on S only for sensitive diffs. A confirmed security finding blocks.
- Reviewers load the target repo's `CLAUDE.md` and `REVIEW.md`, flag broken conventions and out-of-date lines, and need file:line evidence.
- Convergence: fix-loop rounds review only the diff since the last QA round, never repeat a reported finding, and name a bug class with every instance.
- Disputes from `implement` go to fresh verifiers.
- `RUN/qa.json` records raw, confirmed, disputed and per-severity counts per round, and the bug classes, for `flow.py metrics` and `flow.py findings`.

**Why**

The article: "Several agents look for bugs at the same time. Then a separate group votes on each finding, and it only gets posted if enough of them agree it's real." Style-only filters were A/B tested by the team before they kept them. Labels: "so a bug the PR didn't introduce doesn't look like the author's fault". Security: "A PR can't merge while any finding from the bug review or the security review is still open." Convergence controls moved pass-after-one-round from 65% to 78% and mean reviews to pass from 2.08 to 1.32. In this pipeline a false FAIL costs an escalated `implement` loop, so verification saves money as well as time. Depth by size follows "Deep is worth it where one missed bug costs more than the extra review time".

**Switch back**

Set `"version": "v2"` for this step in `workflow/pipeline.json`, or run `/sk-flow:start qa=v2 <task>` once.

### v2 (2026-11-15)

**Origin**

- Article: "Which Claude model should you build with? Fable, Opus, Sonnet, or Haiku", Addy Osmani, claude.dev blog, https://claude.dev/blog/which-claude-model-should-you-build-with/, published 2026-11-09, read 2026-11-15. Evaluated with `/sk-flow:eval`; the user chose a fixed model table over the local decision model (`/sk-dev:decision-suggest-model`), so a v1 against v2 comparison measures the routing only.

**What changed compared with v1**

- Runs as a subagent: S on Sonnet medium, M and L on Opus medium. The `code-reviewer` agent gets the same model and effort.

**Why**

Article table: "Repeated agent tasks: investigation, review, drafting → Sonnet 5.5, medium". M and L keep Opus, because QA is the gate before an automatic merge and bigger changes carry more risk.

**Switch back**

Set `"version": "v1"` and `"model": "main"` for this step in `workflow/pipeline.json`, or run `/sk-flow:start qa=v1 qa.model=main <task>` once. v1 expects the main thread (it may ask the user), so it needs `main`.

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
