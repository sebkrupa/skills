# implement v3

Goal: make the failing tests pass with the smallest correct change.
Runs for: S, M, L.
External: `incremental-implementation` (invoke: skill).
Input: `RUN/tests.md`, the design doc (M, L), `RUN/analysis.md`. In a fix loop, also `RUN/qa.md` or the CI failure.
Output: commits on the task branch. In a fix loop, also `RUN/disputes.md`.
Runs as: a subagent on the step model (S: Sonnet medium, M: Opus medium, L: Opus high). In a fix loop the orchestrator raises the model or effort one rung (escalation ladder). You have no chat history: everything you need is in the files above.

1. Call the `incremental-implementation` skill and follow it: thin slices, each one verified.
2. For each slice: change the code, run the tests, commit with a conventional message (`feat:`, `fix:`, `refactor:`).
3. Follow the design doc. If the design is wrong or incomplete, do not change scope silently: write the gap in `RUN/run.md`. If the gap changes behavior the user agreed on, do not ask: end with `STOP: <the gap>`. The orchestrator asks the user.
4. Do not weaken or delete a test to make it pass. If a test is wrong, fix the test and write why in `RUN/run.md`.
5. At the end, run all commands from `RUN/analysis.md` (test, lint, type check, build). All must pass.

In a fix loop: first read what the previous attempt changed (`git log` and `RUN/run.md`), because a smaller model may have made it. Fix the open IMPORTANT and security findings in `RUN/qa.md`, or the CI failure. Do not fix NIT or PRE_EXISTING findings.

- Fix the whole bug class: every instance the finding lists, and any other instance of the same class you find in the diff.
- If you think a finding is wrong, do not fix it. Append it to `RUN/disputes.md` with the finding, your reason and file:line evidence. The next QA round lets fresh verifiers decide.
- Append to `RUN/run.md` what you changed, per finding: `fixed` or `disputed`.
