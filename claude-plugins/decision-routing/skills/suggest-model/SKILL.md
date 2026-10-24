---
name: suggest-model
description: Ask a local decision model which Claude model and reasoning effort fit a task. It only prints the answer and does not run the task. Use only when the user runs /decision-routing:suggest-model.
argument-hint: [--decider <name>] <task or question>
disable-model-invocation: true
---

# Suggest a model

Task from the user:

$ARGUMENTS

If the task is empty, ask the user for it and stop.

Do not do the task. This skill only finds the model and the effort for it.

The script is `${CLAUDE_SKILL_DIR}/../../scripts/decision.py`. Run it with `python3`.
Pick the decision model by the rules in `${CLAUDE_SKILL_DIR}/../decision-models/SKILL.md` (section "Rules for skills"). Read that file first.
`python3 <script> model "<task>"` prints JSON. For each field (`model`, `effort`) it gives `choice`, `probability`, `confidence`, `passed` and `probabilities`.
`passed` is true when `probability` >= the threshold (`threshold` in the script output; each decision model has its own).
Use only `probability` for the threshold. Show `confidence` for information only.

## 1. Ask with up to 4 attempts

1. Attempt 1: run `python3 <script> model "<original task>"`.
2. Exit code 2 (decision model not reachable): tell the user "The decision model is not reachable." with the error from the output, and stop.
3. Keep each field that has `passed: true`. Do not ask the decision model about it again.
4. For each field that has not passed, rewrite the task text and run again with `--fields <failing fields>`.
   - Keep the goal of the task exactly the same.
   - Make it clearer: state the scope, the type of work, the size and the expected output.
   - Do not add requirements the user did not give. Do not hint which model or effort to pick.
   - Each attempt uses a new rewrite.
5. Stop after 4 attempts in total (the original plus 3 rewrites).

Record every attempt: the text sent and the result of each field.

## 2. Pick the result

- A field that passed: use its choice.
- A field that did not pass after 4 attempts: use the choice with the highest `probability` across all attempts. Mark it "below threshold".

## 3. Show the result

Print in one line: `Model: <model>, effort: <effort>`.
Under it, for each field, show the probability of each option and the confidence. Show "below threshold" where it applies.
If there was more than 1 attempt, show a table of all attempts: the text sent, then for each field the choice, probability and confidence.
