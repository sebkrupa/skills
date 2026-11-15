# ship v2

Goal: open the PR and merge it only when it is safe.
Runs for: S, M, L.
External: `pr` (invoke: skill).
Output: the PR, merged or left open with a reason.

## 1. Open the PR

1. Push the task branch: `git push -u origin flow/<slug>`.
2. Call the `pr` skill to write the PR body. Include: what changed and why, the design doc link (M, L), the test list, the QA verdict and the remaining nits, and the egm gate decisions from `RUN/run.md`.
3. Open the PR to the default branch with `gh pr create`.

If `gh` does not work, stop and give the user the push and PR commands.

## 2. Decide whether to merge

Do not merge, and stop with the PR link and the reason, if any of these is true:

- `RUN/analysis.md` says `CI: no`, or the PR has no checks.
- The PR changes protected paths: `.github/`, CI config files, `**/migrations/**`, `*.env*`, secrets or key files, infrastructure code (`*.tf`, `bicep`, Helm charts, Kubernetes manifests).

## 3. Wait for CI

Run `gh pr checks <number> --watch --fail-fast`.

- Green: go to step 4.
- Red: send the log reading to a subagent on Haiku (Agent tool, `model: haiku`). Tell it: "Run `gh run view <run-id> --log-failed`. For each failure, report the job, the file, the test name and the first error line. Do not edit files." Write its report to `RUN/ci-failure.md`. Return to the orchestrator for a fix loop with that file as input.

## 4. Merge

Run `gh pr merge <number> --squash --delete-branch`. If the merge is refused (required reviews, branch protection), stop and report the PR link and the reason. Do not use `--admin`.

After the merge, switch to the default branch and pull.
