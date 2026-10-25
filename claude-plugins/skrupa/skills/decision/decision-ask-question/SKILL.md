---
name: decision-ask-question
description: Ask a local decision model any typed question about a text - a choice from a list, a yes or no question, or a rating on a scale (for example a Fibonacci estimate of a task or a 0-100 level). Use only when the user runs /skrupa:decision-ask-question.
argument-hint: [--decider <name>] <question and the text to judge>
disable-model-invocation: true
---

# Ask a question

Request from the user:

$ARGUMENTS

If the request is empty, ask the user for it and stop.

The script is `${CLAUDE_SKILL_DIR}/../../../scripts/decision/decision.py`. Run it with `python3`.
Pick the decision model by the rules in `${CLAUDE_SKILL_DIR}/../decision-models/SKILL.md` (section "Rules for skills"). Read that file first.
The decision model judges a text (the `state`) with typed questions. It cannot write text. It only picks from the answers you give it.
Send the request at once. Do not ask the user to confirm it first.

## 1. Build the request

Split the user request into:
- The question to answer.
- The text to judge (the `state`). If the user gives only a task or a topic (for example "Estimate the database architecture for project X"), the state is that task. Add facts from the conversation that the question needs. Do not change the meaning of the text to judge.

Pick one type:
- **Estimate** of the size or complexity of a task (story points, Fibonacci): use the fixed scale. Run `python3 <script> estimate "<state>"` and go to step 3.
- **`score`** for an ordered scale (a level, an intensity, 0-100). `criteria` is an array of 2 to 10 short level descriptions, lowest first. For a 0-100 scale use 5 levels for 0, 25, 50, 75 and 100. The script gives `percent`, the expected value on 0-100.
- **`choice`** for categories with no order. `criteria` is an object: option name to a short description. Up to 26 options. If it is possible that no option fits, add a "None of these" option.
- **`noul`** for a yes or no question. It has only `instructions`, no `criteria`.

`instructions` is one clear question. Use one field. Use more fields only when the user asks more than one question. The decision model judges each field separately.

Run:

```bash
python3 <script> ask <<'DECISION_EOF'
{"state": "<text to judge>", "questions": {"<field name>": {"type": "...", "instructions": "...", "criteria": ...}}}
DECISION_EOF
```

- Exit code 2 (decision model not reachable): tell the user "The decision model is not reachable." with the error from the output, and stop. Do not guess an answer.
- Exit code 1 (the server rejected the request): fix the JSON from the error message and run again.

## 2. Threshold for `choice` and `noul`

`passed` is true when `probability` >= the threshold (`threshold` in the script output; each decision model has its own).
For each `choice` or `noul` field that has not passed:
- Rewrite only `instructions` and the option descriptions. Make them clearer and more distinct.
- Do not change the state. Do not change the meaning of the question or the set of options.
- Run again with only the failing fields. Stop after 4 attempts in total.

If a field still has not passed after 4 attempts, show a table of all attempts: the instructions, choice, probability and confidence.
Ask the user with AskUserQuestion:
- "Change the question": the user gives a new question. Start again at step 1.
- "Use the most probable": use the choice with the highest `probability` across all attempts. Mark it "below threshold".

A `score` field and an estimate have no threshold. Ask them once.

## 3. Show the result

Show:
- The question, the type and the options or levels.
- The answer: the choice (`choice`, `noul`), the level and `percent` (`score`), or the points (estimate).
- The probability of each option, and the confidence.
- The table of attempts, if there was more than 1.

For an estimate with `split: true` (13 points or more), say that the task is big and is better split into milestones.
