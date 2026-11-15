# implement v1

Goal: make the failing tests pass with the smallest correct change.
Runs for: S, M, L.
External: `incremental-implementation` (invoke: skill).
Input: `RUN/tests.md`, the design doc (M, L), `RUN/analysis.md`. In a fix loop, also `RUN/qa.md` or the CI failure.
Output: commits on the task branch.

1. Call the `incremental-implementation` skill and follow it: thin slices, each one verified.
2. For each slice: change the code, run the tests, commit with a conventional message (`feat:`, `fix:`, `refactor:`).
3. Follow the design doc. If the design is wrong or incomplete, do not change scope silently: write the gap in `RUN/run.md`. If the gap changes behavior the user agreed on, stop and ask.
4. Do not weaken or delete a test to make it pass. If a test is wrong, fix the test and write why in `RUN/run.md`.
5. At the end, run all commands from `RUN/analysis.md` (test, lint, type check, build). All must pass.

In a fix loop: fix only the findings in `RUN/qa.md` with severity critical or important, or the CI failure. Then append to `RUN/run.md` what you changed.
