# analyze v1

Goal: understand the task and the repo, set the size, and create the task branch.
Output: `RUN/analysis.md`.

## 1. Read the task

Decide the kind: `feature` or `bug`. For a bug, write the symptom, the expected behavior and how to reproduce it, if the task says so.

## 2. Read the repo

Find these facts. Look them up; do not ask the user.

- The default branch (`git symbolic-ref refs/remotes/origin/HEAD`, else `main`) and the remote.
- The stack and the exact commands for test, lint, type check and build (from `package.json`, `*.csproj`/`*.sln`, `pyproject.toml`, `Package.swift`, `Makefile`, `Cargo.toml`, `go.mod`, ...). Run the test command once to confirm it works and to record the baseline (pass/fail count).
- CI: files in `.github/workflows/`, `azure-pipelines.yml`, `.gitlab-ci.yml` or similar. Record `CI: yes` or `CI: no`.
- `gh auth status` works: yes or no.
- The files and modules the task touches.
- EGM docs: do the source folders the task touches have EGM `README.md` files (interface and contract sections)? Record `EGM docs: yes` or `EGM docs: no`.

## 3. Set the size

If the user gave `size=`, use it. Otherwise:

- `S`: 1 to 2 files, clear intent, no new interface. Most small bug fixes.
- `M`: a feature or fix across several files, with a known approach.
- `L`: new subsystem, new public interface, data changes, or many unknowns.

Write the size and a one-line reason in `analysis.md` and in `RUN/run.md`.

## 4. EGM docs bootstrap (M and L only)

If the size is M or L and `EGM docs: no`, run `egm-bootstrap` as a separate PR before the task:

1. Create the branch `flow/<slug>-egm-docs` from the default branch.
2. Follow `egm-bootstrap` for the folders the task touches only. Do not bootstrap the whole repo.
3. Commit, push, and open a PR titled `docs: EGM READMEs for <area>`.
4. Merge it with the rules of the `ship` step (CI green, squash merge). If it cannot be merged by those rules, stop and report the PR link.
5. Update the default branch locally.

## 5. Create the task branch

Create `flow/<slug>` from the up-to-date default branch.

## analysis.md format

```
# Analysis: <task>
Kind: feature | bug
Size: S | M | L - <reason>
Default branch: <name>   CI: yes | no   gh: yes | no   EGM docs: yes | no
Commands: test=<cmd> lint=<cmd> typecheck=<cmd> build=<cmd>
Baseline: <test result>
Touches: <files and modules>
Bug: <symptom / expected / reproduction>   (bug only)
Notes: <risks, unknowns>
```
