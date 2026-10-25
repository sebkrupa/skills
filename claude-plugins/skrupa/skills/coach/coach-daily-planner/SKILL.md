---
name: coach-daily-planner
description: Plans ONE day realistically. Reads the calendar if available, asks for the time window, priorities and nice-to-haves, checks that the load fits, builds a chronological schedule with breaks and buffer, fills spare time from the todo list and long-term goals, and publishes it as a checklist page with live progress. Use when the user asks "zaplanuj dzień", "plan dnia", "co mam dziś zrobić", "zaplanuj jutro", "planner", "daily plan".
argument-hint: "[date, default today; or 'jutro']"
---

# Coach daily planner

Start: follow `${CLAUDE_PLUGIN_ROOT}/references/coach/rules.md`. Plan page: `${CLAUDE_PLUGIN_ROOT}/references/coach/plan-artifact.md`. One day only; for a whole week use `coach-weekly-planner`.

## 1. Collect (one round, skip what is already known)
1. **Calendar** (optional): if a calendar tool exists, read the events of the day, read-only. They are fixed and immovable. Say "calendar data from <date>". No tool → ask for the fixed commitments.
2. **Seeded day**: if `days/<date>` already exists in the plan artifact (from `coach-weekly-planner`), read it and start from it. Also read unfinished `must` items of the previous day and offer them as carry-over.
3. Ask in one numbered message:
   1. Time window (e.g. 7:00–20:00).
   2. Must-do tasks, each with time estimate and deadline.
   3. Nice-to-have tasks.
   4. Energy or limits today.
   Missing estimate → mark "wymaga Twojej decyzji", never guess.

## 2. Math first
Sum the time of all tasks and fixed commitments. Compare with the window minus breaks and buffer. Defaults (override from `profil.md` Person): 10 min break after each 90 min of work, a 15 min lunch block when the window covers midday, buffer = about 15% of free time. Show the calculation in 2–3 lines. Over capacity → state the shortfall in minutes and list candidates to postpone, ranked by deadline and priority. Do not shorten tasks. Do not move fixed events.

## 3. Schedule
Chronological, with hours. Must-dos first in the best energy hours, nice-to-haves after, buffer visible. Never overlap. Ask nothing more; propose.

## 4. Fill spare time
If time remains, offer up to 3 suggestions, each with its source, reason and duration:
- open items from the todo source in `profil.md` (overdue and near deadlines first),
- one small step toward a long-term goal from `profil.md` (name the goal and its "Why"),
- optionally a health step as in `coach-fitness`, when health data exists.
Add nothing to the schedule until the user accepts. Accepted → type `suggestion`.

## 5. Publish and answer
Write the day as in `plan-artifact.md`. Answer with:
1. The calculation.
2. The schedule as a table (time | task | type).
3. `Do przełożenia / wymaga decyzji` — only if not empty.
4. The page link, and the question "OK, czy zmienić coś?"
Calendar write-back only when the user asks; never edit or delete existing events.
New task, postponed task or goal change → `## Do aktualizacji profilu`.
