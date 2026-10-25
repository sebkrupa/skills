# Decision skills

These skills ask a local decision model (a small model on a llama.cpp server) typed questions and use the answers. The model gives a calibrated probability for each answer. A skill uses an answer only when its probability reaches the threshold of that decision model.

All skills call the same script: `../../scripts/decision/decision.py`. The decision models are listed in `../../scripts/decision/models.json`.
Every skill runs only when the user types its command (`disable-model-invocation: true`). Add `--decider <name or alias>` to any command to pick a decision model.

## Skills

| Skill | What it does | Runs work? |
|---|---|---|
| `decision-models` | Lists the decision models, their status on the server, the default and the fallback order. Holds the "Rules for skills" that the other skills use to pick the decision model. | No |
| `decision-ask-question` | Asks any typed question about a text: a choice from a list, yes or no, or a level on a scale (for example a Fibonacci estimate or a 0-100 level). | No |
| `decision-suggest-model` | Finds the Claude model and reasoning effort that fit a task. Rewrites the task text up to 3 times when a field is below the threshold. Prints the answer only. | No |
| `decision-run-on-suggested-model` | Does what `decision-suggest-model` does, then runs the task in one subagent with that model and effort. | Yes, one task |
| `decision-plan-and-run` | Estimates the size of a task, splits it into milestones and steps, picks the model and effort of each step, writes a plan to `.claude/plans/`, asks for approval, runs the plan and writes a summary. | Yes, a plan |

## How `decision-plan-and-run` runs a plan

`decision-plan-and-run` follows the guideline [Building agents: when to fold subagents into your main agent loop](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop).

The guideline says: one agent loop with skills and tools often gives better quality, lower cost and lower latency than an orchestrator with a subagent for each part. Keep a subagent only for a specific problem.

How the skill applies it:

| Guideline | In the skill |
|---|---|
| One model and one context window do the work. | The main loop does each step itself (`inline`) by default. It sees every earlier result, so nothing is lost in handoffs. |
| Keep a subagent only for context bloat, parallel work, or tool and instruction conflicts. Verification is also a valid use. | A step runs in a subagent only for a written reason: `parallel` (independent steps run at the same time), `context` (a large read whose detail later steps do not need), or `model` (the decision model picked a different Claude model and the step is self-contained). One fresh-context review subagent runs at the end of plans with 5 points or more. |
| Merge specialists that are tightly coupled. | Steps that need each other's output or change the same files are merged into one step. |
| The planner and the executor are the same model. The plan changes as results come in. | The main loop writes the plan and runs it. After each step it changes, merges, adds or drops the remaining steps, and records why. Scope changes need the user's approval. |
| Remove rule-based plan code. | The Fibonacci estimate gives a guide for the number of steps, not a fixed number. Steps are cut at natural units of work. |
| Harness limits and a verifier check after the loop. | Tests and the build run after each milestone, with at most 2 fix rounds before the user is asked. The final review reports only real defects. |
| Verify subagent conclusions against real data. | After a subagent step, the main loop checks the changed files before it goes on. |
| Measure each change and keep what holds up. | The plan file records every decision model call, where each step ran and why, tokens and time, and the fit of each subagent step. The summary lists lessons for the plugin. |

The earlier version ran every step in its own subagent, one after another. The benchmark notes in `claude-plugins/work-in-progress/decision/hierarchy-workflow/` show the cost: about 207k subagent tokens for a 5-point task with every step on the session model (bench-s1), and manager checks that used 46% of the tokens and found nothing (bench-s2). Only the fresh-context architect found real defects. That is why the new version keeps a single review subagent.
