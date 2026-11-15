# plan v1

Goal: a design doc that the tests and the code can follow.
Runs for: M, L.
External: `egm-draft` (invoke: read).
Input: `RUN/concepts_brief.md`, `RUN/analysis.md`.
Output: `docs/designs/<YYYY-MM-DD>-<slug>.md` in the target repo, committed on the task branch.

1. Follow `egm-draft` with the concepts brief as input.
2. Handle its gates by the orchestrator rules (auto-accept the recommended option, stop only on high severity).
3. The doc must also have these sections, for the next steps. Add them if egm's template does not:
   - `## Files to change`: each file and what changes.
   - `## Test list`: each behavior to test, one line each, with the test level (unit, integration).
   - `## Out of scope`.
4. Save the doc to `docs/designs/<YYYY-MM-DD>-<slug>.md`. Create the folder if it does not exist.
5. Commit it: `docs: design for <task>`.
6. Write the doc path in `RUN/run.md`.
