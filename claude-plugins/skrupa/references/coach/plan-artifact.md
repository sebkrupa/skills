# Plan artifact (shared by coach-daily-planner and coach-weekly-planner)

One artifact per person: the page `${CLAUDE_PLUGIN_ROOT}/references/coach/templates/plan.html`. The plan data is not in the page. It lives in the artifact `db`, one document per day at `days/<yyyy-mm-dd>`.

## Day document
```json
{"date":"2026-10-26","items":[
 {"id":"a1","start":"09:00","end":"10:00","title":"…","type":"fixed|must|nice|suggestion",
  "source":"calendar|todo|goal: <name>|you","why":"…","notes":"…","done":false}]}
```
- `id` is unique inside the day and stable when the plan is rewritten.
- `fixed` = calendar or agreed meeting. No checkbox. Never move it.
- Times are local, `HH:MM`, 24 h, chronological, not overlapping.

## First plan (no artifact URL in `profil.md`)
1. Load the `artifact-capabilities` skill. Publish the template with `capabilities: {db: {}}`, title "Plan dnia".
2. Write day documents with `ArtifactData` `set` on `days/<date>` (use `batch` for several days).
3. End the answer with `## Do aktualizacji profilu`: the artifact URL, for the Notes section of `profil.md`.

## Later plans (URL in `profil.md` Notes)
1. Do not republish the page. Write `days/<date>` with `ArtifactData` `set` (replace the day) — the open page updates live.
2. To keep ticks, first `get` the old day and copy `done` for items with the same `id`.
3. Read `days/*` with `ArtifactData` `list` to see what was ticked (done / not done) and carry over unfinished `must` items.

## No Artifact tool (e.g. Claude Desktop Project without artifacts)
Show the plan as a markdown table (time | task | type | source). Tell the user ticks will not be saved. Ask on the next run which tasks were done.
