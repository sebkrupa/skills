---
name: start
description: Run one development task (feature or bug fix) through the versioned sk-flow pipeline - analyze, clarify, plan, design review, TDD tests, implement, QA, ship (PR and merge). Use only when the user runs /sk-flow:start.
argument-hint: "[size=S|M|L] [<step>=vN ...] [orchestrator=vN] <task>"
disable-model-invocation: true
---

# sk-flow start

Arguments from the user:

$ARGUMENTS

If there is no task text, ask the user for it and stop.

The helper script is `${CLAUDE_SKILL_DIR}/../../scripts/flow.py`. Run it with `python3`. Call it `FLOW` below.

1. Split the arguments. Words of the form `key=value` at the start are overrides: `size=S|M|L`, `orchestrator=vN`, or `<step>=vN` (for example `qa=v1`). The rest is the task.
2. Run `python3 FLOW pipeline <overrides>`. It prints the definitions root, the orchestrator file and every step with its version and file. The root is the repo source when the plugin was installed from a local repo, so a version switch in the repo works without a reinstall.
3. Read the orchestrator file and follow it exactly. Pass it the task and the overrides.

Do not read step files before the orchestrator tells you to.
