# design-review v1

Goal: find gaps in the design doc with zero-context reviewers before any code exists.
Runs for: M, L.
External: `egm-review`, then `egm-resolve` (invoke: read).
Input: the design doc from `plan`.
Output: `RUN/design-review.md`, and the fixed design doc committed on the task branch.

1. Follow `egm-review` on the design doc. Keep its stages sequential, as egm requires. Run the reviewers as fresh subagents, as egm says.
2. Follow `egm-resolve` on the findings. Apply the PROPOSE FIX items.
3. Gates: by the orchestrator rules. A finding that changes the scope or the problem statement is high severity: stop and ask the user.
4. Write `RUN/design-review.md`: each finding, its severity, and what was done (fixed, rejected with reason, asked the user).
5. Commit the updated doc: `docs: apply design review to <task>`.
