---
name: decision-models
description: List the local decision models of the sk-dev plugin, their status on the llama.cpp server and the default one. Also holds the rules the other decision skills use to pick the decision model. Use only when the user runs /sk-dev:decision-models.
argument-hint: (no arguments)
disable-model-invocation: true
---

# Decision models

The script is `${CLAUDE_SKILL_DIR}/../../../scripts/decision/decision.py`. Run it with `python3`.
The models are in `${CLAUDE_SKILL_DIR}/../../../scripts/decision/models.json`. To add a model, add one entry there.

## List the models

Run `python3 <script> models`. Show:
- The server address and if it is online. If it is offline, tell the user to start the Llama app (or `llama serve`).
- A table: name, label, aliases, status, threshold. Mark the default model.
- The fallback order (used only when no model is given).
- For each model with status "not downloaded": its `download` command. Tell the user that the server must be restarted after a download (quit and open the Llama app again).
- How to pick a model: add `--decider <name or alias>` to any sk-dev command, for example `/sk-dev:decision-plan-and-run --decider nimble <task>`.

## Rules for skills

The other decision skills read this section. Follow it in every skill that runs the script.

1. **Read the choice.** If the user text has `--decider <name>`, take the name and remove `--decider <name>` from the text. The rest is the task or the request.
2. **Pass the choice.** Add `--decider <name>` before the mode in every script call, for example `python3 <script> --decider nimble model "<task>"`. Without a name, do not add it.
3. **Say which model decides.** Every script result has a `decider` object: `name`, `label` and `selected`. After the first call, tell the user in one line:
   - `selected` is `default`: "Decision model: <label> (default)."
   - `selected` is `explicit`: "Decision model: <label>."
   - `selected` starts with `fallback`: "Decision model: <label> (<selected>)."
4. **Keep one model per run.** After the first call, add `--decider <decider.name>` to all later calls of the same run, so that all decisions come from one model.
5. **Errors.**
   - Exit code 1 with "unknown decision model": show the known models from the message and stop.
   - Exit code 2: no decision model is available. The message says why (server offline, or model not downloaded with its download command). Show the message. Then follow the skill's own rule for "decision model not reachable".
