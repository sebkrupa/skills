# simplify v1

Goal: make the task's diff smaller and clearer before QA, with no change of behavior.
Runs for: M, L.
External: `code-simplification` (invoke: skill).
Input: the diff from the default branch, `RUN/analysis.md`, the design doc.
Output: at most one commit on the task branch, and `RUN/simplify.md`.
Runs as: a subagent on Sonnet medium. You have no chat history: everything you need is in the files above.

1. Call the `code-simplification` skill and follow it, on the lines this task changed only. Do not touch code outside the diff.
2. Allowed: remove dead code and duplication the task added, reuse an existing helper instead of new code, flatten needless abstraction, make names and control flow clearer.
3. Not allowed: change behavior, public interfaces, tests, or the design. Do not fix bugs here; QA finds them.
4. Run every command from `RUN/analysis.md` (test, lint, type check, build).
   - All pass: commit as `refactor: simplify <task>`.
   - Any fails: discard your changes (`git checkout -- .` for the files you changed) and commit nothing.
5. Write `RUN/simplify.md`: each change and why, the lines removed and added, and the command results. If you changed nothing, write why.

This step runs once per run. Fix loops go from `implement` straight to `qa`.
