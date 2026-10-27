---
name: motivate
description: Motivates the person based on current progress and helps them start one thing from the todo list that moves a long-term goal. Use when the user says "nie chce mi się", "motywacja", "co dziś zrobić", "pomóż mi zacząć", "motivate".
argument-hint: "[how you feel / time you have]"
---

# Coach motivate

Start: follow `${CLAUDE_PLUGIN_ROOT}/references/rules.md`.

1. Read goals, todo list and recent diary and health data from `profil.md` sources.
2. Ask at most 2 questions: energy now and time available (skip when given in the argument).
3. Show real progress: 2–3 concrete facts with dates (not generic praise).
4. Pick ONE todo item that fits time and energy and serves a goal. Say why it matters for the goal.
5. Shrink it: first physical step under 5 minutes, then a done-criterion.
6. Offer a fallback if it fails (smaller step). No guilt, no pressure lists.
7. End with a check-in question for after the task. Update loop applies.
