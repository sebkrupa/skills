# qa v3

Goal: an independent check of the change. Several reviewers look for bugs in parallel, a separate group of verifiers votes on each finding, and only confirmed findings count.
Runs for: S, M, L.
External: `code-reviewer` (invoke: agent), `security-auditor` (invoke: agent), `egm-drift-report` (invoke: read, M and L only).
Input: the diff from the default branch, the design doc (M, L), `RUN/analysis.md`, `RUN/tests.md`, the target repo's `CLAUDE.md` and `REVIEW.md` if they exist. In a fix loop, also the previous `RUN/qa.md` and `RUN/disputes.md`.
Output: `RUN/qa.md` with the verdict PASS or FAIL, and one round appended to `RUN/qa.json`.
Runs as: a subagent on the step model (S: Sonnet medium, M and L: Opus medium). Every reviewer and verifier below runs on the same model and effort.

## 1. Depth

| Size | Depth | Reviewers | Verifiers per finding | Confirmed when |
|---|---|---|---|---|
| S | Quick | correctness | 1 | the verifier says real |
| M | Standard | correctness, system fit, security | 3 | 2 of 3 say real |
| L | Deep | correctness, system fit, security, tests | 3 | 2 of 3 say real |

For S, add the security reviewer only when the diff touches auth, input parsing, secrets, file or network I/O, shell commands, or SQL.

## 2. Scope of the review

- First QA round: the whole diff, `git merge-base <default> HEAD` to `HEAD`.
- Fix-loop rounds: only the diff since the commit of the last QA round (written in `RUN/qa.json`). Also check that each finding from the previous round is fixed.

## 3. Reviewers (in parallel, fresh subagents)

Start all reviewers in one message, so they run at the same time. None of them has chat history. Give each one in the prompt: the repo path, the base and head commits, the paths of the design doc, `RUN/analysis.md`, `RUN/tests.md`, `CLAUDE.md` and `REVIEW.md`, the commands, and the findings already reported in earlier rounds ("do not report these again").

Common instructions for every reviewer:
"Review only the given diff, against the whole repo and the task's intent. For each finding report: a bug class (a short reusable name, for example `missing-null-check`), every instance of that class in the diff as file:line, the evidence from the code (not a guess from a name), the problem, and the fix. Do not report findings that are only about style, formatting, naming, diagnostics or cleanup. Follow CLAUDE.md and REVIEW.md if given: flag code that breaks a convention in them, and lines in them that this change makes out of date. Do not edit files."

Lenses:

- **correctness** (`code-reviewer` agent): "Does the change solve its problem? For a bug fix, does it fix the root cause? Run the test, lint, type check and build commands and report each result. Check that the tests cover the test list and test behavior, not implementation details."
- **system fit** (`code-reviewer` agent): "Does the change fit the system, match the design doc, and leave other callers and features working? Look for broken callers, contracts and invariants outside the diff."
- **security** (`security-auditor` agent): "Find security problems introduced by this diff: injection, auth and access checks, secrets, unsafe deserialization, path traversal, unsafe shell or SQL, missing validation at trust boundaries."
- **tests** (`code-reviewer` agent, L only): "Find behavior in the diff that no test covers, and tests that would pass with a broken implementation."

Do not tell a reviewer what you think is wrong.

## 4. Verifiers (fresh subagents, per finding)

For each finding, start the verifiers of the depth table (`general-purpose`, same model). Batch findings so verifiers of different findings run in parallel. Give each verifier only the finding, the repo path and the commits, not the reviewer's reasoning beyond the evidence. Instructions:

"Try to prove this finding wrong. Read the code at the given lines and everything it depends on. Answer with one of: REAL, NOT_REAL, with the reason and file:line evidence. Then give the severity:
- IMPORTANT: a real bug or security problem introduced by this diff.
- NIT: real but minor, no wrong behavior.
- PRE_EXISTING: real, but the same code exists at the merge-base (check with `git show <base>:<file>`), so this diff did not introduce it.
Do not edit files."

A finding is confirmed when it reaches the vote of the depth table. Its severity is the most common severity among the REAL votes; on a tie, the lower one. Drop unconfirmed findings, but count them.

## 5. Disputes (fix-loop rounds)

`RUN/disputes.md` lists findings `implement` did not fix, with its reason. Give each disputed finding with the reason to 3 fresh verifiers (1 for S). If the vote stays REAL, it is still open. Otherwise it is dropped as `disputed_dropped`.

## 6. Drift check (M, L)

Follow `egm-drift-report` for the design doc of this task only, against the code on the task branch.

## 7. Verdict

FAIL if any of these is true:

- A command fails.
- A confirmed finding is IMPORTANT.
- A confirmed finding comes from the security reviewer and is not PRE_EXISTING.
- The drift report shows behavior in the design that is not built, or built behavior that is not in the design.

Otherwise PASS. NIT and PRE_EXISTING findings do not fail QA; they go into the PR body.

## 8. Output

Write `RUN/qa.md`: the verdict, the depth, the command results, a summary line that starts with a count ("3 confirmed findings: 1 important, 2 nits" or "No findings to fix"), then every confirmed finding sorted by severity, with its class, all instances, evidence and fix, then the drift result.

Append one round to `RUN/qa.json` (create `{"rounds": []}` first if it does not exist):

```json
{"head": "<commit>", "verdict": "PASS|FAIL", "depth": "quick|standard|deep",
 "raw": 0, "confirmed": 0, "important": 0, "nit": 0, "pre_existing": 0, "security": 0,
 "disputed_upheld": 0, "disputed_dropped": 0,
 "classes": ["<bug class of each confirmed IMPORTANT or security finding>"]}
```

`raw` counts all reviewer findings before the vote. On FAIL, the orchestrator starts a fix loop.
