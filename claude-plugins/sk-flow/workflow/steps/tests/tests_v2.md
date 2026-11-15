# tests v2

Goal: failing tests that define "done" before any production code changes.
Runs for: S, M, L.
External: `tdd` (invoke: skill).
Input: the `## Test list` of the design doc (M, L), or `RUN/analysis.md` (S).
Output: test files committed on the task branch, and `RUN/tests.md`.
Runs as: a subagent on the step model (S: Sonnet medium, M: Opus medium, L: Opus high). You have no chat history: everything you need is in the files above.

1. Call the `tdd` skill and follow its rules for good tests. Use the test command from `RUN/analysis.md`.
2. S size: write the smallest set of tests for the task. For a bug, write one regression test that reproduces the bug.
3. M and L size: write one test per line of the test list. Follow the repo's existing test layout and style.
4. Run the tests. Each new test must fail, and fail for the expected reason (an assertion, not a compile error or a missing import, except a missing symbol the task adds). Fix any test that fails for a wrong reason.
5. Existing tests must still pass, as in the baseline.
6. Commit: `test: <task>` (failing tests).
7. Write `RUN/tests.md`: each test, the behavior it covers, and its failure message.

Do not change production code in this step, except empty stubs that a test needs to compile.
Do not ask the user anything. If the test list cannot be tested as written, write why in `RUN/run.md` and end with `STOP: <reason>`.
