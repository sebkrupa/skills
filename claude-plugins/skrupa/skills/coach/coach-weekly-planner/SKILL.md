---
name: coach-weekly-planner
description: Plans a whole week through a conversation about outcomes, priorities, deadlines and capacity per day, then distributes the work across days and seeds each day in the plan page. The daily plan is refined later by coach-daily-planner. Use when the user asks "zaplanuj tydzień", "plan tygodnia", "weekly plan", "co w tym tygodniu", "priorytety na tydzień".
argument-hint: "[week start date, default next Monday or current week]"
---

# Coach weekly planner

Start: follow `${CLAUDE_PLUGIN_ROOT}/references/coach/rules.md`. Plan page: `${CLAUDE_PLUGIN_ROOT}/references/coach/plan-artifact.md`. Per-day rules (math, breaks, buffer, no shortening, no moving fixed events, spare-time suggestions) are in `coach-daily-planner`; apply them, do not restate them.

## 1. Read
- Calendar for the week (optional, read-only). No tool → ask for the fixed commitments per day.
- `profil.md`: goals, todo source, rhythm of the day. Existing `days/*` in the plan artifact: unfinished `must` items go to the carry-over list.
- `coach-summary` style check if the last plan is older than 7 days: how did last week go (done vs open).

## 2. Conversation (rounds of numbered questions, recommended answer for each)
Ask only what is unknown. Cover:
1. Top 3 outcomes of the week, and why they matter (link to a long-term goal when it fits).
2. Deadlines and hard dates.
3. Time window per day (e.g. Mon–Fri 8:00–18:00, Sat shorter, Sun off) and days that must stay light.
4. Tasks with estimates: must-do, then nice-to-have. Missing estimate → "wymaga decyzji".
5. Recurring routines to protect (training, family, rest).
Wait for answers before the next round.

## 3. Capacity math
Per day: window − fixed events − breaks − buffer = free minutes. Week: total free vs total task time, 2–5 lines. Over capacity → shortfall in minutes and candidates to postpone (by deadline and priority). Do not shorten tasks. Keep one buffer slot or a light day.

## 4. Distribute
Put each task on a day: deadlines first, heavy work in high-energy days, no day above its free time. Show a table: day | fixed | planned tasks | free minutes left. Ask "OK, czy zmienić coś?" and iterate until accepted.

## 5. Seed and answer
Once accepted, write `days/<date>` for each planned day as in `plan-artifact.md`: fixed events with exact times, tasks as `must` / `nice` with rough slots inside the day window, no overlaps. Tell the user to run `coach-daily-planner` each morning to fix the exact hours and fill spare time. Send the page link.
New goal status or deadline → `## Do aktualizacji profilu`.
