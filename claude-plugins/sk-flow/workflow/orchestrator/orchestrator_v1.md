# Orchestrator v1

You run one task through the pipeline. You do the steps in the main thread, except where a step says to use a subagent.
`FLOW` is `python3 <plugin>/scripts/flow.py` (the path from `/sk-flow:start`).

## Stop rules

Stop and report to the user only in these cases. Otherwise continue without asking.

1. The `clarify` step (the user answers the brainstorm questions).
2. An egm gate with a high-severity finding or decision (see "egm gates").
3. A healthcheck FAIL, before or during the run.
4. The fix-loop limit is reached (see "Fix loops").
5. The `ship` step cannot merge safely (no CI, protected paths, failed merge).
6. The working tree has uncommitted changes at the start.

When you stop, say what happened, what you tried, the state of the branch, and the exact next action for the user.

## 1. Set up the run

1. Find the git root of the current project. If the current folder is not a git repo, stop.
2. If `git status --porcelain` is not empty, stop (rule 6). Do not stash or commit the user's work.
3. Make a slug from the task (lowercase, `-`, at most 40 characters). The run folder is `<git root>/.sk-flow/runs/<YYYY-MM-DD-HHMM>-<slug>/`. Call it `RUN`.
4. Add the line `.sk-flow/` to `<git root>/.git/info/exclude` if it is not there. Do not edit `.gitignore`.
5. Write `RUN/run.md`: the task, the overrides, the date, and a "Decisions" section. Append to it during the run.

## 2. Healthcheck external skills

Run `FLOW health`. It checks the external skills of every enabled step.

- Exit 0: all OK. Continue.
- Exit 1: a skill has status FAIL. Stop (rule 3). For each FAIL row, show the `id`, the `error` and the fix (the `install` command, then a restart of Claude Code).
- Exit 2: some rows have a blank status. Check each one yourself:
  - `invoke: skill`: the exact `name` is in this session's list of available skills.
  - `invoke: agent`: the exact `name` is in this session's list of agent types.
  - Found: run `FLOW health-set <id> OK`.
  - Not found: run `FLOW health-set <id> FAIL "<reason>"` and stop (rule 3). Propose the fix:
    - Plugin not installed: the `install` command.
    - Plugin installed but disabled: `claude plugin enable <plugin>@<marketplace>`.
    - Installed and enabled but not in the list: the skill probably has `disable-model-invocation: true`. Propose to change its entry to `invoke: read` with `/sk-flow:eval`.
  - Then run `FLOW health` again.

During the run, if a call to an external skill fails (the Skill tool refuses it, the agent type is unknown, the file is missing), run `FLOW health-set <id> FAIL "<exact error>"` and stop (rule 3).

## 3. How to use an external skill

The `external` list of a step names entries in `workflow/external_skills.json`.

- `invoke: skill`: call the Skill tool with `name`.
- `invoke: agent`: call the Agent tool with `subagent_type` = `name`.
- `invoke: read`: read the file at the `path` from `FLOW health` and follow it in this thread. In that file, replace `${CLAUDE_PLUGIN_ROOT}` with the plugin install path (the folder that contains `skills/`). For egm, also read `<plugin root>/docs/claude.md` first, as the skill says.

The step file says what input to give the skill and where its output goes. When the step file and the external skill disagree on an output path or a stop, the step file wins.

## egm gates

egm skills have human checkpoints (multiple-choice fix approvals, re-sync checkpoints). Run egm in its uninterrupted mode where it has one. At each gate:

- If the gate concerns a high-severity finding (egm labels such as blocking, critical, high, or a change to the problem statement or scope), stop (rule 2) and ask the user.
- Otherwise choose the recommended option. Append the gate, the options and your choice to the "Decisions" section of `RUN/run.md`.

## 4. Run the steps

1. Run `FLOW mark RUN analyze <version> start`, read the `analyze` step file from the `FLOW pipeline` output, do it, then run `FLOW mark RUN analyze <version> end`.
2. `analyze` sets the size (S, M or L) unless the user gave `size=`. Run `FLOW pipeline <size> <overrides>` again. Use this list for the rest of the run.
3. For each next step in order:
   - If `skip` is set, write `<step>: skipped (<reason>)` in `RUN/run.md` and go on.
   - Run `FLOW mark RUN <step> <version> start`.
   - Read the step file and do what it says.
   - Run `FLOW mark RUN <step> <version> end`.

Read each step file only when you reach it. Steps hand over work through files in `RUN` and the design doc, not through chat memory.

## Fix loops

- `qa` verdict FAIL: go back to `implement` with `RUN/qa.md` as input, then run `qa` again.
- `ship` CI red: go back to `implement` with the CI failure as input, then `qa`, then `ship`.

At most 2 loops per run, both kinds together. Count them in `RUN/run.md`. On the third failure, stop (rule 4) with what failed each time, what you changed, and the branch state.

## 5. Finish

1. Run `FLOW metrics RUN`. It writes `RUN/metrics.json` and appends to the per-machine log.
2. Report to the user, in the language of the task:
   - The PR link and whether it was merged.
   - Size, the steps that ran with their versions, and the steps that were skipped.
   - Time and tokens per step from the metrics.
   - The egm gate decisions taken without the user.
   - Anything the user must do.
