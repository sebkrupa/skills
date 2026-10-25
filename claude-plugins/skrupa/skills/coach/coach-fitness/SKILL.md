---
name: coach-fitness
description: From health tracker data, proposes one concrete step for health or fitness progress and builds it into the person's daily routine. Use when the user asks "co zrobić dla zdrowia", "ruch", "sen", "fitness", "wpleć to w dzień", "health".
argument-hint: "[focus, e.g. sleep, steps, strength]"
---

# Coach fitness

Start: follow `${CLAUDE_PLUGIN_ROOT}/references/coach/rules.md`. For detailed training plans prefer a dedicated training-plan skill when installed.

1. Read health data (sleep, steps, heart rate, training, weight) and the daily rhythm in `profil.md`, plus diary mood and energy. No data → ask for an export or screenshot, make `dane-zdrowie.md`.
2. Find 1–2 patterns with numbers and dates (e.g. sleep under 6 h on 4 of 7 days).
3. Propose ONE change tied to a goal in `profil.md`. Make it small, measurable, for 2 weeks.
4. Embed it in the routine: trigger (existing habit or time), place, duration, what to do when the day breaks. Offer a todo item to create.
5. Say how to measure success and when to check again (suggest `coach-summary`).
6. Pain, dizziness, chest symptoms, big weight loss → stop and advise a doctor.
