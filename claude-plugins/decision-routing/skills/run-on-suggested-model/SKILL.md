---
name: run-on-suggested-model
description: Ask a local decision model which Claude model and reasoning effort fit a task, then run the task in a subagent with that model and effort. Use only when the user runs /decision-routing:run-on-suggested-model.
argument-hint: [--decider <name>] <task or question>
disable-model-invocation: true
---

# Run on the suggested model

Task from the user:

$ARGUMENTS

If the task is empty, ask the user for it and stop.

## 1. Find the model and effort

Pick the decision model by the rules in `${CLAUDE_SKILL_DIR}/../decision-models/SKILL.md` (section "Rules for skills"). Read that file first.
Read `${CLAUDE_SKILL_DIR}/../suggest-model/SKILL.md` and do its steps 1 to 3 for this task.
Use the task above in place of `$ARGUMENTS`. The script path in that file is `${CLAUDE_SKILL_DIR}/../../scripts/decision.py`.
Do these steps differently:
- Exit code 2 (decision model not reachable): tell the user "The decision model is not reachable, running with the current model." Then do the task yourself and stop here.
- A field has not passed after 4 attempts: show the table of all attempts. Ask the user with AskUserQuestion:
  - "Change the task": the user gives new task text. Start again at step 1 with it.
  - "Use the most probable": use the choice with the highest `probability` across all attempts.

## 2. If the final effort is `max`

Always ask the user with AskUserQuestion:
- "Split the task": propose a list of smaller tasks. After the user accepts it, route each smaller task separately (steps 1 to 3 for each). Run them one by one in order.
- "Continue with max": go to step 3.

## 3. Run the task

Before you start, tell the user in one line:
`Model: <model>, effort: <effort>` with the probability of each choice.

Then call the Agent tool:
- `subagent_type`: `general-purpose`
- `model`: `haiku` for Haiku 5.5, `sonnet` for Sonnet 5.5, `opus` for Opus 5.5, `fable` for Fable 5.1
- `effort`: the chosen effort (`low`, `medium`, `high`, `xhigh` or `max`). This skill explicitly asks for it.
- `prompt`: the ORIGINAL task text from the user, not a rewrite. Add the working directory. The subagent does not see this conversation, so add any facts from the conversation that the task needs.

When the subagent finishes, give its result to the user.
