# research: orchestrator

## Summary

| | |
|---|---|
| Active version | v3 |
| Purpose | Runs the steps in order, enforces stops, healthchecks, fix loops and metrics. |
| External skills | none |
| Time | seconds of overhead per step (script calls) |
| Tokens | estimate as v2, plus about 5k for the findings report |
| Measured | not yet. Run `/sk-flow:eval compare orchestrator` after some runs. |

Time and token values marked "estimate" are guesses before any run. Replace them with measured medians from `~/.claude/sk-flow/state/log.jsonl`.

## Versions

### v3 (2026-11-15)

**Origin**

- Article: "How the Claude Code team does code review", Addy Osmani, Morgan Westlee Lunt and Qing Wang, claude.dev blog, https://claude.dev/blog/solving-code-review-at-anthropic/, published 2026-10-15, read 2026-11-15. Evaluated with `/sk-flow:eval`; the user approved all six proposals.

**What changed compared with v2**

- Stop rule 5 adds Medium and High risk tiers.
- Fix loops pass `RUN/disputes.md` to `qa` and skip the new `simplify` step.
- Finish runs `flow.py findings`: confirmed bug classes go to `~/.claude/sk-flow/state/findings.jsonl`; classes seen in 2 or more runs of the same repo get a proposed `REVIEW.md`, `CLAUDE.md` or lint rule in the report. Nothing is edited automatically.
- The report adds QA counts and the risk tier.

**Why**

Article: "Fix recurring findings at the source: in the skill, with a lint rule, or in instruction files", and "move repeated review comments into" `REVIEW.md`.

**Switch back**

Set `"orchestrator": "v2"` in `workflow/pipeline.json`, or run `/sk-flow:start orchestrator=v2 <task>` once.

### v2 (2026-11-15)

**Origin**

- Article: "Which Claude model should you build with? Fable, Opus, Sonnet, or Haiku", Addy Osmani, claude.dev blog, https://claude.dev/blog/which-claude-model-should-you-build-with/, published 2026-11-09, read 2026-11-15. Evaluated with `/sk-flow:eval`; the user chose a fixed model table over the local decision model (`/sk-dev:decision-suggest-model`), so a v1 against v2 comparison measures the routing only.

**What changed compared with v1**

- Every step has a model and effort in `pipeline.json` (`model`: `main`, `<model>:<effort>`, or one per size). `main` steps run inline on the main thread, pinned to Opus medium by `/sk-flow:start` frontmatter. Other steps run as a `general-purpose` subagent with the Agent tool's `model` and `effort`.
- Models switch only at step boundaries, because the prompt cache belongs to the model that wrote it (article: "Mixing models").
- Subagent steps get the step file, paths and rules in the prompt, and return `STOP: <reason>` instead of asking the user.
- Fix loops follow the article's escalation ladder for `implement`: effort one level up while below `high`, then the next model up at `medium` (`flow.py escalate`). S: sonnet medium, sonnet high, opus medium. L: opus high, fable medium, fable high.
- Marks record model and effort; metrics add tokens and estimated USD per model, from `workflow/prices.json` (article list prices, 2026-11-09).
- Per-run overrides: `<step>.model=<model>:<effort>`, `<step>.effort=<effort>`.

**Why**

The article's default is Opus 5.5 at medium for unsure and everyday work, Sonnet 5.5 for well-scoped coding and repeated review, and Haiku 5.5 for reading and searching. v1 ran everything on the session model. The ladder replaces plain retries: the article reports Opus low with failures rerun at high passing about 97% of tasks for $0.17 each, against 95.3% for $0.29 with every task at high. The cost metric follows the article's "measure on your own work" method: per-task cost from the `usage` field.

**Switch back**

Set `"version": "v1"` for this step in `workflow/pipeline.json` and `"orchestrator": "v1"`, or run `/sk-flow:start orchestrator=v1 <task>` once.

### v1 (2026-11-15)

**Origin**

- Own design, agreed in a grilling session with the user on 2026-11-15 (mattpocock-skills `grilling`).

**What it does**

- Setup: refuses a dirty working tree, creates `.sk-flow/runs/<date>-<slug>/` and hides it with `.git/info/exclude`.
- Healthcheck: `flow.py health` checks every external skill of enabled steps. Status is blank, OK or FAIL per machine in `~/.claude/sk-flow/state/health.json`. A plugin version change resets the status to blank. `read` skills are checked by the script (file exists). `skill` and `agent` skills are checked by the model against the session's lists. FAIL stops the run with the install or enable command.
- Autonomy: the only planned stop is `clarify`. egm gates are auto-accepted with the recommended option and logged, unless high severity.
- Size: `analyze` sets S, M or L. S skips `clarify`, `plan` and `design-review` (`run_for` in `pipeline.json`).
- Fix loops: QA FAIL or red CI go back to `implement`. At most 2 loops per run.
- Metrics: `flow.py mark` writes start and end marks; `flow.py metrics` sums tokens from the session transcript (and its subagents) between the marks.

**Why**

One pipeline for features and bug fixes. Size rules keep small fixes cheap. Per-step marks make versions comparable.
