# qa v1

Goal: an independent check of the change by a reviewer that did not write it.
Runs for: S, M, L.
External: `code-reviewer` (invoke: agent), `egm-drift-report` (invoke: read, M and L only).
Input: the diff from the default branch, the design doc, `RUN/analysis.md`, `RUN/tests.md`.
Output: `RUN/qa.md` with the verdict PASS or FAIL.

## 1. Code review in a fresh subagent

Start the `code-reviewer` agent. It has no chat history, so give it everything in the prompt:

- The repo path and the base and head commits (`git merge-base <default> HEAD` and `HEAD`).
- The paths of the design doc (M, L), `RUN/analysis.md` and `RUN/tests.md`.
- The commands to run.
- These instructions: "Run the test, lint, type check and build commands and report each result. Review the diff for correctness, security, readability, architecture and performance. Check that the tests cover the test list and test behavior, not implementation details. Check the change against the design doc. Report each finding with severity critical, important or nit, file:line, the problem and the fix. Do not edit files."

Do not tell the reviewer what you think is wrong.

## 2. Drift check (M, L)

Follow `egm-drift-report` for the design doc of this task only, against the code on the task branch.

## 3. Verdict

FAIL if any of these is true:

- A command fails.
- A finding is critical or important.
- The drift report shows behavior in the design that is not built, or built behavior that is not in the design.

Otherwise PASS. Nits do not fail QA.

Write `RUN/qa.md`: the verdict, the command results, every finding with its severity, and the drift result. On FAIL, the orchestrator starts a fix loop.
