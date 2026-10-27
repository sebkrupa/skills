---
name: decision-plan-and-run
description: Plan a task with a local decision model and run it in one main agent loop. The decision model estimates the size (Fibonacci) and picks the model and effort of each step. The main loop does the steps itself and uses a subagent only when a step runs in parallel, would bloat the context, needs a different model, or is the final review. Saves the plan and an execution summary to .claude/plans/. Use only when the user runs /sk-dev:decision-plan-and-run.
argument-hint: [--decider <name>] <task>
disable-model-invocation: true
---

# Plan and run

Task from the user:

$ARGUMENTS

If the task is empty, ask the user for it and stop.

The script is `${CLAUDE_SKILL_DIR}/../../../scripts/decision/decision.py`. Run it with `python3`.
Pick the decision model by the rules in `${CLAUDE_SKILL_DIR}/../decision-models/SKILL.md` (section "Rules for skills"). Read that file first.
To pick a model and effort, this skill uses the steps in `${CLAUDE_SKILL_DIR}/../decision-suggest-model/SKILL.md`. Read that file before step 2.
The script path in that file is the same script as above.

Write the plan file and all messages in the language of the task.
Record every decision model call for the plan file: what was asked, the text sent in each attempt, and the result with its probabilities.

Why one loop: you see every earlier result, so nothing is lost in handoffs, and you do not pay for a new context window on each step. A subagent costs a full context rebuild and a nested loop. Use one only for a reason from step 2.

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
- Less than 13 points: the task is one plan.
- 13 points or more (`split: true`): split the task into 2 or more milestones. Each milestone is one part of the goal with a clear result. Estimate each milestone again in the same way. Send the milestone text with enough scope to judge it alone. A milestone with 13 points or more is split again.
- Use at most 3 levels: the task, its milestones and their sub-milestones. If a part on level 3 still has 13 points or more, ask the user with AskUserQuestion:
  - "Plan it as it is": plan it as one part.
  - "Stop": stop the workflow. The user changes the task.

Steps:
- Each step is one clear action with a clear result, in the order to do it.
- Cut steps at natural units of work, not to reach a number. As a guide, a part with 1 to 3 points has 1 to 3 steps, 5 points has about 3 to 5, and 8 points has about 4 to 8.
- Merge steps that are tightly coupled: one step needs the exact output of the other, or both change the same files. A chain of small dependent steps is one step.
- Mark steps that do not depend on each other and do not change the same files as a parallel group (`[parallel A]`, `[parallel B]`).
- Write each step so that it can be done from its text and the files it names.

## 2. Pick the model, the effort and where each step runs

For each step, do steps 1 and 2 of decision-suggest-model with the step text in place of `$ARGUMENTS`. Do these things differently:
- Do not show the result of each step to the user. Keep it for the plan.
- A field has not passed after 4 attempts: use the most probable choice for now and add the step to the open questions.
- The final effort is `max`: add the step to the open questions.

Then decide where the step runs. The default is `inline`: you do the step yourself in this conversation, on the session model.
Use `subagent` only when at least one of these reasons applies. Write the reason in the plan.
- `parallel`: the step is in a parallel group with at least one other subagent step.
- `context`: the step must read or search a large amount of material (many files, logs, docs), and later steps need only its conclusion.
- `model`: the picked model is not the session model, and the step is self-contained (its text and named files are enough).

A different effort alone is not a reason. An inline step runs at the session effort.
If the decision model was not reachable, only `parallel` and `context` apply.

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
- Session model: <the model you run on>

## Task
<the original task text, word for word>

## Decision model calls
<for each decision model call: what was asked (estimate of X, model and effort of step N),
each attempt with the text sent, the result and the probabilities>

## Plan
### M1 <milestone> (<points> pts, p=<probability>)
- [ ] 1.1 <step> (<model>, <effort>; p model=<p>, p effort=<p>; inline)
- [ ] 1.2 <step> [parallel A] (<model>, <effort>; p model=<p>, p effort=<p>; subagent: parallel)

## Changes at approval

## Changes during the run

## Execution

## Summary
```

Without milestones, put the steps directly under "Plan" and number them 1, 2, 3.

## 4. Ask for approval

First, ask about the open questions from step 2. Use AskUserQuestion, with up to 4 questions in one call:
- A field below the threshold: "Use the most probable" or "Change the step" (the user gives new step text; do step 2 for it again).
- Effort `max`: "Split the step" (propose smaller steps and do step 2 for each) or "Continue with max".

Write the answers under "Changes at approval" and update the plan in the file.

Then show the plan in the chat: the milestones, the steps, the estimates, the model and effort of each step, where each step runs and why, and the path of the plan file.
Ask with AskUserQuestion:
- "Run the plan": set the status to "approved" and go to step 5.
- "Change the plan": the user says what to change. Change the plan, do step 2 again for new or changed steps, and write the change under "Changes at approval". Then ask again.
- "Reject": set the status to "rejected", write the summary (step 6) and stop.

## 5. Run the plan

Set the status to "running". Do the steps in order.

Inline steps: do the step yourself.

Subagent steps: call the Agent tool. Start all subagent steps of one parallel group in one message, so that they run at the same time.
- `subagent_type`: `general-purpose`
- `model`: only for reason `model`: `haiku` for Haiku 5.5, `sonnet` for Sonnet 5.5, `opus` for Opus 5.5, `fable` for Fable 5.1. Otherwise leave it out.
- `effort`: only for reason `model`: the chosen effort (`low`, `medium`, `high`, `xhigh` or `max`). This skill explicitly asks for it. Otherwise leave it out.
- `prompt`:
  - The original task, word for word.
  - A short version of the plan: one line for each step, with this step marked.
  - The full text of this step.
  - The results of the earlier steps that this step needs: file paths, names, decisions. Give facts, not a summary of a summary.
  - The working directory, and facts from the conversation that the step needs.
  - This instruction: "Do only this step. When you finish, reply with: what you did, the files you changed, the facts the next steps need, and anything that is still open. If you cannot finish the step, say what failed."
- Before you go on, check the report against the real files: the changed files exist and contain the change.

After each step, tick its checkbox in the plan file. Under "Execution", write the step number, inline or subagent, what was done, the changed files, and the tokens and time if the Agent tool result gives them.

After each step, look at the remaining steps again with what you now know:
- Change, merge, add or drop steps when the result makes the plan wrong. Keep the goal of the task the same. Write each change and its reason under "Changes during the run".
- A change that adds scope the user did not ask for, or drops a part of the goal: ask the user first with AskUserQuestion.
- A new step gets step 2 (model, effort, where it runs) before it runs.

If a step fails or you cannot finish it, stop. Show the user what is done and the error. Ask with AskUserQuestion:
- "Retry the step": do the same step again.
- "Skip the step": go on with the next step.
- "Stop the workflow": go to step 6.

After each milestone (or after the last step when there are no milestones), run the checks:
- If the project has tests or a build (for example `package.json` scripts, a `*.sln` or `*.csproj` file, `pyproject.toml` or a `Makefile`), run them.
- If the check passes, go on without a question.
- If the check fails, fix it yourself and run the check again. After 2 failed fix rounds, ask with AskUserQuestion: "Keep fixing", "Skip the check" or "Stop the workflow".

After the last check, if the plan has 5 points or more, run one final review in a subagent. A reviewer with a fresh context finds what the author does not see.
- `subagent_type`: `general-purpose`. Leave out `model` and `effort`.
- `prompt`: the original task word for word, the plan, the list of changed files, and this instruction: "Review the changes for this task. Read the changed files and the code they touch. Report only real defects: wrong behavior, a missed part of the task, data loss, security. For each defect give the file, the line, the problem and the fix. If you find none, say so. Do not change files."
- No defects: go on.
- Defects: show them and ask with AskUserQuestion: "Fix them" (fix them yourself, then run the checks again), "Skip" or "Stop the workflow".

Write each check, each failure, the review result and each decision of the user under "Execution".

## 6. Finish

Set the final status:
- "done": all steps are done and all checks passed.
- "partly done": a step, a check or a review finding was skipped.
- "stopped": the user stopped the workflow or rejected the plan.

At the end of the plan file, under "Summary", write:
- The result, in one or two sentences.
- A table of the steps: number, status, inline or subagent with the reason, model, effort, number of decision model attempts, number of retries.
- The plan changes during the run and why.
- The problems, the errors and the decisions of the user during the run.
- The fit of each subagent step: was the reason real, and was the model and effort too weak, right or too strong? Give one reason. Signs: errors, retries, simple work on a strong model, or a report that was not enough for the next step.
- Lessons: what to improve in the planning and in the sk-dev plugin (criteria, scale, thresholds, the subagent reasons).

Write the summary also when the workflow stops early.

Show in the chat: the table of the steps, the open items, and the path of the plan file.
