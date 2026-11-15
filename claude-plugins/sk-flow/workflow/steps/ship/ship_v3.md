# ship v3

Goal: open the PR and merge it only when it is safe.
Runs for: S, M, L.
External: `pr` (invoke: skill).
Output: the PR, merged or left open with a reason, and the risk tier in `RUN/run.md`.

## 1. Open the PR

1. Push the task branch: `git push -u origin flow/<slug>`.
2. Set the risk tier (section 2) first, then call the `pr` skill to write the PR body. Include: what changed and why, the design doc link (M, L), the test list, the QA verdict, the remaining NIT and PRE_EXISTING findings, the egm gate decisions from `RUN/run.md`, and these three sections:
   - `## Testing`: each command run and its result, from `RUN/qa.md`.
   - `## Risk`: the tier and the reason.
   - `## How to revert`: the exact steps (for a squash merge: `git revert <merge commit>`, plus any data or config to undo).
3. Open the PR to the default branch with `gh pr create`.

If `gh` does not work, stop and give the user the push and PR commands.

## 2. Risk tier

The change sets the tier, not the author or the agent. List the changed files with `git diff --name-only <base> HEAD`. Take the highest tier that matches:

- **High**: CI and workflow files (`.github/`, CI config), `**/migrations/**`, `*.env*`, secrets or key files, infrastructure code (`*.tf`, `bicep`, Helm charts, Kubernetes manifests), auth and access control, billing and payments, installers and auto-updaters.
- **Medium**: size L; paths that `CODEOWNERS` assigns to an owner, or that the target repo's `REVIEW.md` or `CLAUDE.md` marks as sensitive (caching, system prompts, public API contracts, data deletion).
- **Low**: everything else. For example docs, tests, additive changes, size S and M changes outside the paths above.

Write the tier and the matching files in `RUN/run.md`.

## 3. Decide whether to merge

Do not merge if any of these is true. For no CI, stop now. For Medium and High, first wait for CI (section 4), so a red check still starts a fix loop, then stop with the PR link and the reason.

- `RUN/analysis.md` says `CI: no`, or the PR has no checks.
- The tier is High: say "needs review by a person, and by two people if the repo asks for it".
- The tier is Medium: say "needs approval by one person". An agent's approval never counts as a person's.

Only Low changes merge without a person, after green CI.

## 4. Wait for CI

Run `gh pr checks <number> --watch --fail-fast`.

- Green: go to section 5 if the tier is Low. For Medium and High, report the green checks with the stop of section 3.
- Red: send the log reading to a subagent on Haiku (Agent tool, `model: haiku`). Tell it: "Run `gh run view <run-id> --log-failed`. For each failure, report the job, the file, the test name and the first error line. Do not edit files." Write its report to `RUN/ci-failure.md`. Return to the orchestrator for a fix loop with that file as input.

## 5. Merge

Run `gh pr merge <number> --squash --delete-branch`. If the merge is refused (required reviews, branch protection), stop and report the PR link and the reason. Do not use `--admin`.

After the merge, switch to the default branch and pull.
