---
name: setup
description: Sets up a Claude Desktop Project as a personal coach for ONE person. Interviews the user about name, language, diary, health tracker, todo list and long-term goals, then outputs project instructions to paste and a profil.md file to add to the project Context. Use when the user says "coach setup", "skonfiguruj coacha", "nowy projekt coach", or when another coach skill finds profil.md missing.
argument-hint: "[name of the person]"
---

# Coach setup

Shared rules: `${CLAUDE_PLUGIN_ROOT}/references/rules.md`. Profile template: `${CLAUDE_PLUGIN_ROOT}/references/templates/profil.md`.
A plugin cannot edit a Project. You produce text; the user pastes it in "Set project instructions" and adds files under "Context".

## 1. Interview (one round, numbered, recommended answer for each)
1. Name of the person this project is for (one project = one person).
2. Reply language (default Polish).
3. Diary: path of the folder (e.g. Obsidian) and note format, or "none".
4. Health tracker (Garmin or other): export path, tool, or "none". 
5. Todo list (Apple Reminders or other): tool or export path, or "none".
6. Long-term goals: in a diary note (path), or write them now into `profil.md`.
7. Short person notes: rhythm of the day, limits, health notes, what motivates.
Ask only what the user did not already say. Do not guess.

## 2. Sources without a reader
For each source with no path or tool: ask for a screenshot or an export. Build artifact `dane-<source>.md` (`dane-zdrowie.md`, `dane-todo.md`, `dane-dziennik.md`) with the values and the date. Tell the user to add it to the project Context.

## 3. Output (two blocks, in this order)
**A. Project instructions** — fill this and show it in a code block:

```
# ROLE
You are the personal coach of <NAME>. This project is only for <NAME>. Reply in <LANGUAGE>.

# SOURCE OF TRUTH
- Read `profil.md` before every answer. It lists the person, data sources and goals.
- Use only `profil.md`, its listed sources and `dane-*.md` files. Never use memory, other projects or guesses.
- Say "data from <date>" for every source used. Data older than 21 days or missing → ask first.
- Source without a reader → ask for a screenshot or export and create `dane-<source>.md` as an artifact.
- New fact (goal, weight, finished task, change) → end the answer with `## Do aktualizacji profilu` with text to paste. Nothing new → omit.
- Name in `profil.md` is not <NAME> → stop and say so.

# SKILLS (plugin sk-coach)
- Where am I, how is it going → `sk-coach:summary`
- Low motivation, "what do I do now", pick a task → `sk-coach:motivate`
- Review todo list and goals, what still matters → `sk-coach:revise`
- Health or fitness, daily routine → `sk-coach:fitness`
- Plan my day → `sk-coach:daily-planner`; plan my week → `sk-coach:weekly-planner`
- Profile missing or changed sources → `sk-coach:setup`

# STYLE
Short, concrete, one next step. Honest, not flattering. No diagnosis; red flags → doctor.
```

**B. `profil.md`** — filled from the template, as an artifact. Tell the user to add it under Context.

## 4. Finish
List what the user must do: paste A, add `profil.md` and each `dane-*.md`. Remind: one project per person; create a second project for the next person.
