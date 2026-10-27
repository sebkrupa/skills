---
name: revise
description: Revises the whole todo list and the long-term goals: where things stand, what is still important, what to drop, merge, postpone or add. Use when the user says "przejrzyj listę", "zrewiduj cele", "co jest jeszcze ważne", "porządki", "revise".
argument-hint: "[goals | todo | all]"
---

# Coach revise

Start: follow `${CLAUDE_PLUGIN_ROOT}/references/rules.md`.

1. Read goals (profile or diary note), the full todo list, and recent summary data. Todo list missing → ask for a screenshot, make `dane-todo.md`.
2. Goals: for each → still wanted? progress since last revision, deadline realistic? Mark keep / change / drop / pause.
3. Todo: sort each item → serves which goal (or none). Mark do now / schedule / delegate / drop. Flag items older than 30 days with no progress.
4. Missing: goals without any todo item, and todo items without a goal.
5. Output a table of proposals with a one-line reason each. Max 5 questions for the person on unclear items; do not decide for them.
6. After confirmation, give the updated goals table and todo list as `## Do aktualizacji profilu` text.
