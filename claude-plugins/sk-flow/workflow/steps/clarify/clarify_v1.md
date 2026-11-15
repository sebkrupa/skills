# clarify v1

Goal: agree with the user what to build, before any design. This is the one planned stop of the run.
Runs for: M, L.
External: `egm-brainstorm` (invoke: read).
Output: `RUN/concepts_brief.md`.

1. Follow `egm-brainstorm`. Give it the task text and `RUN/analysis.md` as the raw concept.
2. Write the brief to `RUN/concepts_brief.md` (tell egm: `EGM artifact directory: RUN`).
3. For a bug, the questions must settle: expected behavior, the scope of the fix, and whether related behavior may change.
4. Ask the user the clarifying questions in rounds, as egm says. This stop is expected; wait for the answers.
5. When the brief is final, stop egm before it starts `/egm-draft`. The orchestrator starts `plan` next.

Do not write the design doc in this step.
