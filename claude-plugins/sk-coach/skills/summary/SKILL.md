---
name: summary
description: Summarizes all data in the coach project (diary, health tracker, todo list, long-term goals) and tells where the person is and how they are going. Use when the user asks "jak mi idzie", "gdzie jestem", "podsumuj", "co się zmieniło", "summary".
argument-hint: "[period, e.g. last month]"
---

# Coach summary

Start: follow `${CLAUDE_PLUGIN_ROOT}/references/rules.md` (profile, source of truth, update loop).

1. Read every source in `profil.md` for the period (default: last 30 days). Many files → extract, do not read all.
2. Answer in 6–10 lines:
   - **Goals**: each long-term goal → status, evidence (date), trend (up / flat / down).
   - **Todo**: done vs open, overdue, what stalls.
   - **Diary**: mood, energy, recurring themes.
   - **Health**: 2–3 key numbers, first → last (sleep, steps, weight, training), with data date.
   - **Gaps**: sources missing or stale.
3. One honest verdict: on track or not, and the one thing that matters most now. Suggest `sk-coach:motivate`, `sk-coach:revise` or `sk-coach:fitness` when it fits.
