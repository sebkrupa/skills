# skills

Claude Code plugins by Sebastian Krupa.

> The details of every skill are inside its `SKILL.md`. You are more than welcome to read them.

Plugin: [`skrupa`](claude-plugins/skrupa). Every skill is called `/skrupa:<group>-<skill>`.

## Groups

### decision

Skills that let a small local model make quick decisions, so Claude does not have to guess.

| Skill | What it does |
|---|---|
| `/skrupa:decision-ask-question` | Answers any typed question about a text: pick from a list, yes or no, or a level. |
| `/skrupa:decision-suggest-model` | Tells you which Claude model and effort fit a task. |
| `/skrupa:decision-run-on-suggested-model` | Does the same, then runs the task on that model. |
| `/skrupa:decision-plan-and-run` | Splits a big task into steps, picks a model for each, and runs them in one main loop. |
| `/skrupa:decision-models` | Lists the local decision models and which one is used. |

### coach

A personal coach for Claude Desktop Projects. One project is one person, with its own `profil.md` and data. Start with `/skrupa:coach-setup`; replies follow the language set in `profil.md`.

| Skill | What it does |
|---|---|
| `/skrupa:coach-setup` | Interviews you and outputs the project instructions and `profil.md`. |
| `/skrupa:coach-summary` | Where you are and how it is going, from diary, health, todo and goals. |
| `/skrupa:coach-motivate` | Motivation and one next step from the todo list. |
| `/skrupa:coach-revise` | Reviews the todo list and goals. |
| `/skrupa:coach-fitness` | One health step built into the day. |
| `/skrupa:coach-daily-planner` | Plans one day (calendar, priorities, spare time) and publishes a checklist page with live progress. |
| `/skrupa:coach-weekly-planner` | Plans a week in conversation and seeds each day for the daily planner. |

---

# coach

A personal coach for [Claude Desktop](https://claude.ai/download) Projects. One project is one person. A plugin cannot edit a Project, so `/skrupa:coach-setup` interviews you (name, language, diary, health tracker, todo list, goals) and outputs two things: the text for "Set project instructions" and a `profil.md` for "Context". The other coach skills read `profil.md` and your data. Replies follow the language set in `profil.md`.

Order of use:

1. `/skrupa:coach-setup` once per person.
2. `/skrupa:coach-weekly-planner` once a week: plans the week and seeds each day.
3. `/skrupa:coach-daily-planner` each morning: calendar, priorities and spare time become a checklist page with live progress.
4. `/skrupa:coach-summary`, `/skrupa:coach-motivate`, `/skrupa:coach-revise`, `/skrupa:coach-fitness` whenever you need them.

Shared rules and the `profil.md` template are in [`references/coach`](claude-plugins/skrupa/references/coach).

---

# decision

A decision model does not write text. It reads a text (the *state*) and answers a typed question about it: a choice from a list, yes or no, or a level on a scale. It gives a probability for each allowed answer in one forward pass. This plugin uses such a model, running locally on llama.cpp, to make routing decisions for Claude Code:

- Is this task small (Haiku, low effort) or hard (Opus, high effort)?
- How big is this task in story points?
- Any custom question you ask about a text.

## Contents

1. [Requirements](#requirements)
2. [Setup](#setup)
3. [Commands](#commands)
4. [Decision models](#decision-models)
5. [How a decision is read](#how-a-decision-is-read)
6. [Benchmark](#benchmark)
7. [llama.cpp on a Mac: terminal and web](#llamacpp-on-a-mac-terminal-and-web)
8. [Troubleshooting](#troubleshooting)
9. [Limitations](#limitations)

## Requirements

- macOS on Apple Silicon. Other systems work with llama.cpp too, but the steps below are for a Mac.
- Memory for the model you use: about 24 GB free for `q4` (default), 12 GB for `nimble`, 70 GB for `bf16`.
- Disk: 19.5 GB for `q4`, 9.5 GB for `nimble`, 62.6 GB for `bf16`.
- [Homebrew](https://brew.sh), Python 3.9 or later (standard library only), [Claude Code](https://claude.com/claude-code).

## Setup

### 1. Install llama.cpp and the Llama app

```bash
brew install llama.cpp
brew install --cask llama-app
```

- `llama.cpp` gives the command-line tools: `llama`, `llama-server`, `llama-cli`.
- The **Llama app** (by the llama.cpp team and Hugging Face) is a menu bar app. It runs `llama-server` in router mode on `http://localhost:9931`: one server for all your models, each loaded on the first request.

Open the Llama app. Add it to **System Settings → General → Login Items**, so that the server starts when you log in.

### 2. Download the decision models

```bash
llama download -hf bartowski/Remek_basal-omni-1.0-ultra-GGUF:Q4_K_S
llama download -hf ggml-org/Bespoke-Nimble-9B-v3-GGUF:Q8_0
```

- The first model is the default (`q4`). The second one (`nimble`) is the fallback and the fast option.
- The files go to the Hugging Face cache, `~/.cache/huggingface/hub/`.
- **Restart the Llama app after a download** (quit it from the menu bar and open it again). The router reads the model list only at start.

`bf16` is optional. Download it only when you want to use it:

```bash
llama download -hf bartowski/Remek_basal-omni-1.0-ultra-GGUF:BF16
```

### 3. Check that the models are visible

```bash
git clone https://github.com/sebkrupa/skills.git
cd skills/claude-plugins/skrupa/scripts/decision
python3 decision.py --self-test
python3 decision.py models
```

`models` shows `"online": true` and the status `unloaded` or `loaded` for each downloaded model. `not downloaded` means step 2 or the app restart is missing.

Try one decision:

```bash
python3 decision.py model "Fix a typo in README.md"
```

### 4. Install the plugin in Claude Code

The marketplace file is in `claude-plugins/.claude-plugin/marketplace.json` of the clone:

```bash
claude plugin marketplace add /path/to/skills/claude-plugins
claude plugin install skrupa@skrupa-skills
```

Inside Claude Code you can do the same with `/plugin marketplace add <path>` and `/plugin install skrupa@skrupa-skills`. Restart Claude Code after the install.

## Commands

| Command | What it does | Runs work? |
|---|---|---|
| `/skrupa:decision-ask-question <question and text>` | Any typed question about a text: a choice from a list, yes or no, a level on a scale, or a Fibonacci size estimate. | No |
| `/skrupa:decision-suggest-model <task>` | Prints the Claude model and reasoning effort that fit the task. | No |
| `/skrupa:decision-run-on-suggested-model <task>` | Picks the model and effort, then runs the task in a subagent with them. | Yes, one task |
| `/skrupa:decision-plan-and-run <task>` | Estimates the size, splits the task into steps or milestones, picks the model and effort of each step, writes a plan to `.claude/plans/`, asks for approval, then runs the plan in the main loop (subagents only for parallel, large-context or different-model steps and a final review) and writes a summary. See [the decision skills README](claude-plugins/skrupa/skills/decision/README.md). | Yes, a plan |
| `/skrupa:decision-decision-models` | Lists the decision models, their status, the default and the fallback order. | No |

### Pick the decision model

Add `--decider <name or alias>` to any command:

```text
/skrupa:decision-plan-and-run --decider nimble Add an export to CSV button to the reports page
/skrupa:decision-suggest-model --decider bf16 Migrate the whole codebase from .NET 6 to .NET 9
```

- Without `--decider`, the default model (`q4`) is used. The skill tells you in one line: `Decision model: ... (default).`
- If the default model is not on the server, the fallback models are tried in order (`nimble`), and the skill tells you so.
- With an explicit `--decider` there is no fallback: you get an error with the download command.
- If the server does not answer, `ask-question` and `suggest-model` stop. `run-on-suggested-model` and `plan-and-run` continue on the current Claude model.
- One run uses one decision model for all its decisions. `plan-and-run` writes it in the plan file.

### Confidence threshold

Each `choice` and yes or no answer has `passed: true` when its probability is at least the threshold of the decision model (0.75 by default, set in `models.json`). When a field does not pass, the skill rewrites the question or the task more clearly and asks again, up to 4 attempts. Then it asks you what to do. Set `DECISION_MIN_CONFIDENCE` to override the threshold for all models.

### The script directly

```bash
python3 decision.py [--decider NAME] model "<task>" [--fields model,effort]
python3 decision.py [--decider NAME] estimate "<task>"
python3 decision.py [--decider NAME] ask request.json      # or JSON on stdin
python3 decision.py models
python3 decision.py [--decider NAME] --eval [tasks.json]
python3 decision.py [--decider NAME] --eval-estimate [tasks.json]
```

`ask` takes the request format of the TypeSafe System One API:

```json
{"state": "Customer: I cannot log in since yesterday, the system says the password is wrong.",
 "questions": {
   "dept":   {"type": "choice", "instructions": "Which team handles this?",
              "criteria": {"cards": "Card complaints", "online": "Online banking support", "loans": "Loans"}},
   "urgent": {"type": "noul", "instructions": "Is the customer unable to use the service?"},
   "mood":   {"type": "score", "instructions": "How frustrated is the customer?",
              "criteria": ["calm", "slightly annoyed", "annoyed", "very frustrated", "furious"]}}}
```

Exit codes: `0` success, `1` the request was rejected or the model name is unknown, `2` no decision model is reachable. `DECISION_URL` overrides the server address.

## Decision models

The models are in [`scripts/models.json`](claude-plugins/skrupa/scripts/decision/models.json):

| Name | Model | Backend | Notes |
|---|---|---|---|
| `q4` (default) | [basal-omni-1.0-ultra](https://huggingface.co/Remek/basal-omni-1.0-ultra) Q4_K_S, 31B, Gemma 4 | `prefill` | Best accuracy in the benchmark. |
| `bf16` | basal-omni-1.0-ultra BF16 | `prefill` | Same answers as `q4` in the benchmark, 3× larger. |
| `nimble` (fallback) | [Bespoke Nimble 9B v3](https://huggingface.co/bespokelabs/Bespoke-Nimble-9B-v3) Q8_0, Qwen 3.5 | `systemone` | Fastest. Weights are CC BY-NC 4.0 (non-commercial use only). |

### Add a model

Add one entry to `models` in `models.json`. No code change is needed.

```json
"my-model": {
  "label": "Short description shown to the user",
  "aliases": ["other-name"],
  "backend": "systemone",
  "id": "<user>/<repo>-GGUF:<quant>",
  "download": "llama download -hf <user>/<repo>-GGUF:<quant>",
  "threshold": 0.75
}
```

- `id`: the model id as `GET http://localhost:9931/models` lists it. Without the `:<quant>` tag, any quant of that repo matches.
- `backend`:
  - `systemone` for a native decision model of llama.cpp (the server lists `decisions` in its `output_modalities`). The server builds the prompt and returns the probabilities.
  - `prefill` for a basal model, or any chat model trained on the basal prompt format 2. Add `temperature` from the model's `CALIBRATION.json`, as in the `q4` entry.
- `default` and `fallback` at the top of the file set the model used without `--decider` and the order of the fallback.

## How a decision is read

### `systemone` backend

`decision.py` sends the request to `POST /v1/systemone` of llama-server. The server reads the probabilities of the option codes from the model and scales them with the temperatures stored in the model file.

### `prefill` backend (basal)

basal models are chat models trained to answer in one token. The plugin does what the basal engine (`basal-serve`) does, following its [prompt format 2](https://github.com/rkinas/basal/blob/v2.3.1/docs/FORMAT2.md):

1. It writes the prompt: a fixed system message, then `State:`, the state, `Question:`, and the options as lines `A. key: description`, `B. ...`. Polish templates are used when the state or the question has Polish letters.
2. `POST /apply-template` applies the model's own chat template (with thinking off). The plugin appends the prefill `{"answer": "`.
3. `POST /completion` with `n_predict: 1` and `n_probs: 50` returns the log-probabilities of the most likely next tokens.
4. The plugin keeps only the option codes (`A`, `B`, ...), divides each log-probability by the calibration temperature of the question type, and normalizes them (softmax). That gives the probability of each option. A code that is not in the top 50 gets 0.
5. The questions of one request are sent in parallel.

The temperatures come from the model's `CALIBRATION.json` (choice 1.044 for 2–10 options, 1.075 for 11–26; yes or no 0.944; score 1.242).

## Benchmark

### Method

- **Questions:** the `model` and `effort` questions of `suggest-model` (4 Claude models, 5 effort levels), and the 7-level Fibonacci size `estimate`.
- **Test sets:**
  - [`eval_model.json`](claude-plugins/skrupa/scripts/decision/eval_model.json): 21 tasks, from "Fix a typo" to "Invent and prove correct a new consensus algorithm".
  - [`eval_model_holdout.json`](claude-plugins/skrupa/scripts/decision/eval_model_holdout.json): 10 tasks not used to tune the question texts, including 2 in Polish.
  - 5 extra programming tasks (null check, CSV CLI with tests, a DbContext race in ASP.NET Core, splitting an Express.js monolith, a distributed CI system).
  - [`eval_estimate.json`](claude-plugins/skrupa/scripts/decision/eval_estimate.json): 11 tasks with a story-point size.
- **Score:** a field is correct when the top answer equals the expected label. The labels are set by hand, so a few of them can be argued (for example, "review a PR that changes 3 files in the payment flow": Opus or Sonnet).
- **Hardware:** Mac with Apple Silicon, 128 GB unified memory, Llama app 0.45.0, llama.cpp 0.7.0.

### Results

36 tasks, 72 decisions (model and effort), and 11 estimates:

| Decision model and server | model + effort | Estimate exact | Latency per task (2 fields) |
|---|---|---|---|
| `q4` on llama.cpp (`prefill`, exact probabilities) | **70/72** | **11/11** | ~3.2 s |
| `nimble` Q8_0 on llama.cpp (`systemone`) | 67/72 | 9/11 | ~2.1 s |
| nimble (MLX mxfp8) on Ollama `/v1/systemone` | 64/72 | – | ~0.9 s |
| `q4` on LM Studio / BIONIC, probabilities from sampling | 70/72 | – | ~4 s per field |
| `bf16` on LM Studio / BIONIC, probabilities from sampling (5 tasks only) | 10/10 | – | ~4 s per field |

- `q4` misses only the 2 arguable holdout tasks, where `nimble` misses too.
- The latency is for a loaded model. The first request after the model is loaded or wakes from idle takes longer (about 5–20 s).

### About the sampling runs

LM Studio and BIONIC do not return log-probabilities, and their `/v1/systemone` does not accept these GGUF files as decision models. For those two rows the probabilities were estimated:

- The decision was the greedy token (temperature 0) after the same basal prompt and prefill.
- The probability of each option was its share in 10 to 20 samples at the calibration temperature (1.044), with `top_p` 1, `top_k` 0 and `min_p` 0.
- With 20 samples the probability has an error of about ±0.1, and each decision takes N+1 requests.

This is why the plugin uses llama.cpp: `n_probs` gives the exact log-probabilities in one request, with the same accuracy.

## llama.cpp on a Mac: terminal and web

### Install and update

```bash
brew install llama.cpp               # CLI: llama, llama-server, llama-cli
brew install --cask llama-app        # menu bar app (GUI, server on :9931)
brew upgrade llama.cpp && brew upgrade --cask llama-app
```

### Download models from Hugging Face

A model is a GGUF repository plus a quantization after a colon. Without it, `Q4_K_M` is used.

```bash
llama download -hf ggml-org/gemma-3-4b-it-GGUF
llama download -hf bartowski/Remek_basal-omni-1.0-ultra-GGUF:Q4_K_S
```

- The files go to `~/.cache/huggingface/hub/`. A multimodal projector (`mmproj`, for images) is downloaded too.
- Find models at [huggingface.co/models?library=gguf](https://huggingface.co/models?library=gguf) and copy `user/repo`.
- Restart the server (or the Llama app) after a download.

### Run a server

```bash
llama serve                                   # router: all models from the cache, loaded on request
llama serve -hf <user>/<repo>:<quant>         # one model (downloads it if needed)
llama serve --port 9931 -c 16384 --models-max 1
```

The Llama app starts the same server for you. Do not start a second one on the same port.

### Web

- Chat and model picker: <http://localhost:9931>
- OpenAI-compatible API, for other apps (Obsidian, IDEs and so on): base URL `http://localhost:9931/v1`

### Manage models (router)

```bash
curl -s localhost:9931/models | jq '.data[] | {id, status: .status.value}'   # list and status
curl -s localhost:9931/models/load   -d '{"model": "<id>"}'                    # load
curl -s localhost:9931/models/unload -d '{"model": "<id>"}'                    # free the memory
```

To delete a model, delete its folder `~/.cache/huggingface/hub/models--<user>--<repo>`, then restart the server.

### Chat in the terminal

```bash
llama cli -hf ggml-org/gemma-3-4b-it-GGUF
```

### Ask a native decision model

```bash
curl -s localhost:9931/v1/systemone -H 'content-type: application/json' -d '{
  "model": "ggml-org/Bespoke-Nimble-9B-v3-GGUF:Q8_0",
  "state": "Fix a typo in README.md",
  "questions": {"effort": {"type": "choice", "instructions": "How much effort?",
    "criteria": {"low": "small edit", "high": "hard work"}}}}'
```

### Settings per model (optional)

Write an INI file and start the router with `llama serve --models-preset <file>`:

```ini
version = 1
[*]
c = 16384
[my-model]
model = /absolute/path/to/model.gguf
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Decision model not reachable: server not reachable` | Open the Llama app, or run `llama serve`. Check the port: `lsof -iTCP:9931 -sTCP:LISTEN`. |
| `decision model not available ... Download with: ...` | Run the download command, then restart the Llama app. |
| `unknown decision model` | Use a name or alias from `python3 decision.py models`. |
| The first decision is slow | The model is being loaded or woke from idle. The next ones are fast. |
| Not enough memory | Unload other models (`/models/unload`) or start the server with `--models-max 1`. |
| Full server logs | `llama serve --verbose` |

## Limitations

- The `prefill` backend supports up to 26 options per question (one-letter codes).
- basal is weak at exact arithmetic and dates. Compute those in code.
- The benchmark is small (36 tasks), and its labels are set by hand. Check the decisions on your own tasks before you rely on them.
- The calibration temperatures of basal were fitted on the BF16 model in its own engine. Q4_K_S in llama.cpp gave the same answers in the benchmark, but its probabilities can differ a little.

## License

The code is under the [MIT License](LICENSE). The models have their own licenses: see their model cards.
