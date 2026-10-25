this is proposed update for 'decision-plan-and-run' workflow skill. idea is to have FLAT workflow (decision-plan-and-run) and add additional one that will include hierarchy (top and low level managers + executors). benchmark gave 2,6 times more token consumption while developing the same topic. the main difference was introduction of architect agent - we might focus mainly on that for the future. right now base decision workflow seems to be good enough. 

attached benchmark 1 = base workflow. benchmark 2 = workflow with top and low level managers.

below is condensed draft of hierarchy workflow skill:



Management layers, BA, the manager checks and the TOP string-check agent are gone. All of them found 0 issues in S2. The Architect stays and is expanded, because both real catches came from it. Replacement for the "Hierarchy mode" section:

# Hierarchy mode

Three roles, no managers. TOP briefs the executors directly and checks their evidence itself.

| Role | Does |

|---|---|

| ARCHITECT | Reads the code, writes the contract, finds design risks before any code exists |

| DEV | Implements the contract |

| TEST | Writes offline tests from the contract, in parallel with DEV |

TOP writes no feature code. TOP spawns ARCHITECT first, waits for the contract, then spawns DEV and TEST in parallel.

## Models

Run the decision model for each agent separately. Record model, effort, probability. Do not preassign tiers and do not force a spread. For below-threshold picks, take the most probable and mark it in the ledger. ARCHITECT usually deserves a higher effort than DEV: its decisions are cheap to make and expensive to get wrong.

## ARCHITECT

\*\*Inputs:\*\* the request, plus paths to the code it touches (paths, not summaries). It must read that code itself.

\*\*Deliverable: [`contract.md`](http://contract.md)\*\*, with these sections:

1. \*\*Requirements:\*\* numbered, each with one acceptance check that is a runnable command or a test name.

2. \*\*Interface:\*\* every name that will appear in more than one place: subcommands, flags, files, env vars, exit codes, and the exact text of each user-facing message. One line each, final wording.

3. \*\*Module layout:\*\* which file owns what, which existing functions are reused or changed, and the signature of each change.

4. \*\*Test seams:\*\* where tests substitute the network or filesystem. For each seam, confirm by reading the code that patching it actually takes effect. Look for default arguments bound at definition time, imports done at module top, and global state.

5. \*\*Risks:\*\* the cases where the change could destroy or corrupt existing data, or break existing callers. Cover:

   - writes that replace stored rows or files (`INSERT OR REPLACE`, truncate, overwrite)

   - retries and re-runs: what a second run does to the state of the first

   - input that is accepted but nonsensical (future dates, empty lists, huge ranges)

   - credentials: where they are stored, file mode, and shell history

   - callers and entry points that already exist and must keep working

   For each risk: the decision (guard, reject, or accept) and its acceptance check.

6. \*\*Out of scope:\*\* what is deliberately not done, so DEV and TEST do not add it.

\*\*Rules:\*\*

- Resolve every ambiguity in the request here, as a decision with a reason. Do not pass open questions to DEV.

- Exit codes and error wording are decided once and used everywhere. No "non-zero" or "an error".

- Reuse existing helpers and file formats. A new dependency or config format needs a written justification, or it is rejected.

- The contract is the only shared document. DEV and TEST must not need to ask each other anything.

\*\*Self-check before returning:\*\* list every name in sections 1-3 and confirm each is spelled identically in every section. Confirm every requirement has a check, and every risk has a decision.

## DEV and TEST

Each receives the request and [`contract.md`](http://contract.md), and nothing else. They must follow the contract exactly. If the contract is wrong or incomplete, they report the problem and do not improvise.

- TEST does not read DEV's code before writing tests. It also adds one contract test per name in section 2, so spelling drift fails a test instead of needing a separate review pass.

- Both report evidence: files changed and command output.

## TOP check

1. Run the full test suite and the README commands that need no network.

2. Compare DEV's changed files against the contract's out-of-scope list.

On failure, send the exact failing output to the agent that owns it. Max 2 correction rounds. If the contract itself was wrong, re-run ARCHITECT with the failure.

## Ledger (`bench=true`)

One row per agent: role, model, effort, why, tokens, duration, tool calls, outcome. Add correction rounds and which checks caught a real problem. Write `n/a` for anything not shown. Never estimate.

Removed and why:

- BA manager and analyst: the Architect's requirements section replaces them. The BA manager's check found nothing.

- DEV and QA managers: their checks found nothing, and in S2 they didn't verify messages or README.

- Separate TOP string-check step: found nothing. The contract test per name replaces it.

Open risk: this is still based on one run per mode. It is untested without the S0 baseline.