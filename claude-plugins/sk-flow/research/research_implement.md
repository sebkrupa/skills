# research: implement

## Summary

| | |
|---|---|
| Active version | v3 |
| Purpose | Makes the tests pass with the smallest correct change. |
| External skills | `agent-skills:incremental-implementation` (invoke: skill) |
| Time | estimate 5-40 min |
| Tokens | estimate as v2 |
| Measured | not yet. Run `/sk-flow:eval compare implement` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v3 (2026-11-15)

**Origin**

- Article: "How the Claude Code team does code review", Addy Osmani, Morgan Westlee Lunt and Qing Wang, claude.dev blog, https://claude.dev/blog/solving-code-review-at-anthropic/, published 2026-10-15, read 2026-11-15. Evaluated with `/sk-flow:eval`; the user approved all six proposals.

**What changed compared with v2**

- In a fix loop: fixes the whole bug class, not only the listed line.
- Writes findings it thinks are wrong to `RUN/disputes.md` with evidence instead of fixing them; the next QA round lets fresh verifiers decide.
- Records `fixed` or `disputed` per finding in `RUN/run.md`.

**Why**

Article convergence controls: "Flag the class of bug, so the author fixes every instance", and "every finding must be answered: you either fix it or resolve the thread with a reason". Disputes also measure reviewer noise, like the team's sorting of comments by the author's response.

**Switch back**

Set `"version": "v2"` for this step in `workflow/pipeline.json`, or run `/sk-flow:start implement=v2 <task>` once.

### v2 (2026-11-15)

**Origin**

- Article: "Which Claude model should you build with? Fable, Opus, Sonnet, or Haiku", Addy Osmani, claude.dev blog, https://claude.dev/blog/which-claude-model-should-you-build-with/, published 2026-11-09, read 2026-11-15. Evaluated with `/sk-flow:eval`; the user chose a fixed model table over the local decision model (`/sk-dev:decision-suggest-model`), so a v1 against v2 comparison measures the routing only.

**What changed compared with v1**

- Runs as a subagent: S on Sonnet medium, M on Opus medium, L on Opus high.
- Fix loops escalate one rung each (orchestrator v2 ladder).
- Ends with `STOP: <gap>` instead of asking the user.
- In a fix loop, reads the previous attempt first, because a smaller model may have written it.

**Why**

Same table rows as `tests`. The ladder is the article's "Escalation ladder": verify (tests exist), raise effort, then move one model up at a lower effort.

**Switch back**

Set `"version": "v1"` and `"model": "main"` for this step in `workflow/pipeline.json`, or run `/sk-flow:start implement=v1 implement.model=main <task>` once. v1 expects the main thread (it may ask the user), so it needs `main`.

### v1 (2026-11-15)

**Origin**

- Own design, agreed in a grilling session with the user on 2026-11-15 (mattpocock-skills `grilling`).
- Addy Osmani agent-skills, `incremental-implementation`, plugin `agent-skills@addy-agent-skills` 0.6.13, read 2026-11-15.

**What it does**

- Thin slices; each slice is tested and committed.
- Never weakens a test to pass. Design gaps are logged; behavior changes the user agreed on stop the run.
- In a fix loop it fixes only critical and important QA findings or the CI failure.

**Why**

Small verified slices keep failures local and the history reviewable.
