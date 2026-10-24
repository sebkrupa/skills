---
name: plan-and-run
description: Plan a task with a local decision model and run the plan with subagents. The decision model estimates the size (Fibonacci) to set the number of steps or milestones, and picks the model and effort of each step. Saves the plan and an execution summary to .claude/plans/. Use only when the user runs /decision-routing:plan-and-run.
argument-hint: [--decider <name>] <task>
disable-model-invocation: true
---

# Plan and run

Task from the user:

$ARGUMENTS

If the task is empty, ask the user for it and stop.

The script is `${CLAUDE_SKILL_DIR}/../../scripts/decision.py`. Run it with `python3`.
Pick the decision model by the rules in `${CLAUDE_SKILL_DIR}/../decision-models/SKILL.md` (section "Rules for skills"). Read that file first.
To pick a model and effort, this skill uses the steps in `${CLAUDE_SKILL_DIR}/../suggest-model/SKILL.md`. Read that file before step 2.
The script path in that file is the same script as above.

Write the plan file and all messages in the language of the task.
Record every decision model call for the plan file: what was asked, the text sent in each attempt, and the result with its probabilities.

## 1. Estimate and break down

Run `python3 <script> estimate "<task>"`. It prints `points`, `probability`, `split` and `probabilities`.
The points come from the level with the highest probability. The scale:

| Points | Meaning |
|---|---|
| 1 | one obvious change |
| 2 | a small change in one file |
| 3 | a clear change in a few files, or a short new script |
| 5 | a feature or a fix across several files, with a known solution |
| 8 | work across many files or layers, with some unknowns |
| 13 | a subsystem, several features or a codebase migration, with many unknowns |
| 21 | a whole new system or project |

Exit code 2 (decision model not reachable): tell the user "The decision model is not reachable. I estimate the size myself, and every step runs on the current model." Estimate with the scale above yourself and skip all decision model calls after this.

Break the task down:
- Less than 13 points: the task is one plan. Number of steps: 1 point → 1 step, 2 → 2, 3 → 3, 5 → 4 to 5, 8 → 6 to 8.
- 13 points or more (`split: true`): split the task into 2 or more milestones. Each milestone is one part of the goal with a clear result. Estimate each milestone again in the same way. Send the milestone text with enough scope to judge it alone. A milestone with less than 13 points gets steps by the table above. A milestone with 13 points or more is split again.
- Use at most 3 levels: the task, its milestones and their sub-milestones. If a part on level 3 still has 13 points or more, ask the user with AskUserQuestion:
  - "Plan it as it is": give it 6 to 8 steps.
  - "Stop": stop the workflow. The user changes the task.

Each step is one clear action with a clear result. Put the steps in the order to do them. Write each step so that a subagent can do it without this conversation.

## 2. Pick the model and effort of each step

For each step, do steps 1 and 2 of suggest-model with the step text in place of `$ARGUMENTS`. Do these things differently:
- Do not show the result of each step to the user. Keep it for the plan.
- A field has not passed after 4 attempts: use the most probable choice for now and add the step to the open questions.
- The final effort is `max`: add the step to the open questions.

## 3. Write the plan file

Path: `<working directory>/.claude/plans/<yyyymmdd>-<name>.md`.
- `<yyyymmdd>` is today's date.
- `<name>` comes from the task: lowercase ASCII letters, digits and hyphens, at most 5 words.
- If the file exists, add `-2`, `-3` and so on to the name.
- Create the folder if it is missing. Do not change `.gitignore`. Do not commit the file.

Statuses (write them in the language of the task; in Polish they are in brackets): waiting for approval (`czeka na zgodę`), approved (`zatwierdzony`), rejected (`odrzucony`), running (`w trakcie`), done (`udany`), partly done (`częściowo`), stopped (`przerwany`).

Write the file with status "waiting for approval". Use this structure, with the headings in the language of the task:

```markdown
# <plan title>

- Status: <status>
- Date: <yyyy-mm-dd>
- Working directory: <path>
- Decision model: <decider label>

## Task
<the original task text, word for word>

## Decision model calls
<for each decision model call: what was asked (estimate of X, model and effort of step N),
each attempt with the text sent, the result and the probabilities>

## Plan
### M1 <milestone> (<points> pts, p=<probability>)
- [ ] 1.1 <step> (<model>, <effort>; p model=<p>, p effort=<p>)

## Changes at approval

## Execution

## Summary
```

Without milestones, put the steps directly under "Plan" and number them 1, 2, 3.

## 4. Ask for approval

First, ask about the open questions from step 2. Use AskUserQuestion, with up to 4 questions in one call:
- A field below the threshold: "Use the most probable" or "Change the step" (the user gives new step text; do step 2 for it again).
- Effort `max`: "Split the step" (propose smaller steps and do step 2 for each) or "Continue with max".

Write the answers under "Changes at approval" and update the plan in the file.

Then show the plan in the chat: the milestones, the steps, the estimates, the model and effort of each step, and the path of the plan file.
Ask with AskUserQuestion:
- "Run the plan": set the status to "approved" and go to step 5.
- "Change the plan": the user says what to change. Change the plan, do step 2 again for new or changed steps, and write the change under "Changes at approval". Then ask again.
- "Reject": set the status to "rejected", write the summary (step 6) and stop.

## 5. Run the plan

Set the status to "running". Do the steps one by one, in order. For each step, call the Agent tool:
- `subagent_type`: `general-purpose`
- `model`: `haiku` for Haiku 5.5, `sonnet` for Sonnet 5.5, `opus` for Opus 5.5, `fable` for Fable 5.1
- `effort`: the chosen effort (`low`, `medium`, `high`, `xhigh` or `max`). This skill explicitly asks for it.
- If the decision model was not reachable, leave out `model` and `effort`.
- `prompt`:
  - The original task, word for word.
  - A short version of the plan: one line for each step, with this step marked.
  - The full text of this step.
  - The short reports of the steps that are done.
  - The working directory, and facts from the conversation that the step needs.
  - This instruction: "Do only this step. When you finish, reply with a short report: what you did, the files you changed, and anything that is still open. If you cannot finish the step, say what failed."

After each step, tick its checkbox in the plan file. Under "Execution", write the step number, the report, the changed files, and the tokens and time if the Agent tool result gives them.

If a subagent reports an error or does not finish its step, stop. Show the user what is done and the error. Ask with AskUserQuestion:
- "Retry the step": run the same step again.
- "Skip the step": go on with the next step.
- "Stop the workflow": go to step 6.

After each milestone (or after the last step when there are no milestones), check the work:
- Read the reports of the milestone.
- If the project has tests or a build (for example `package.json` scripts, a `*.sln` or `*.csproj` file, `pyproject.toml` or a `Makefile`), run them.
- If the check passes, go on without a question.
- If the check fails, ask with AskUserQuestion: "Fix it" (run a subagent with the failure output and the strongest model and effort of the milestone), "Skip the check" or "Stop the workflow".

Write each check, each failure and each decision of the user under "Execution".

## 6. Finish

Set the final status:
- "done": all steps are done and all checks passed.
- "partly done": a step or a check was skipped.
- "stopped": the user stopped the workflow or rejected the plan.

At the end of the plan file, under "Summary", write:
- The result, in one or two sentences.
- A table of the steps: number, status, model, effort, number of decision model attempts, number of retries.
- The problems, the errors and the decisions of the user during the run.
- The fit of each step: was the model and effort too weak, right or too strong? Give one reason. Signs: errors, retries, or simple work on a strong model.
- Lessons: what to improve in the planning and in the decision-routing plugin (criteria, scale, thresholds).

Write the summary also when the workflow stops early.

Show in the chat: the table of the steps, the open items from the reports, and the path of the plan file.
