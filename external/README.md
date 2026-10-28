# external

Notable plugins and skills from other repositories. They are not part of this repository's plugins.

Install all of them:

```bash
./external/setup.sh
```

The script needs the `claude` CLI and `npx`. Restart Claude Code after it runs.

## How setup.sh works

The script does not read this README. Each install is one hard-coded line in `setup.sh`. When you add a plugin, add it in both files.

1. `set -u` stops the script on an unset variable. There is no `set -e`, so one failed install does not stop the others.
2. Two helpers do the installs:
   - `plugin <owner/repo> <plugin@marketplace>` is for repositories with a Claude Code marketplace. It runs `claude plugin marketplace add`, then `claude plugin install`. A failed marketplace add (for example, already added) only prints a message. A failed install is added to the `failed` list.
   - `skills <owner/repo> [skill]` is for repositories without a plugin. It runs `npx -y skills@latest add <repo> -g -a claude-code -s <skill> -y`: user level (`~/.claude/skills/`), Claude Code only, no prompts. Without `[skill]` it installs every skill (`-s '*'`). A failure is added to the `failed` list.
3. One line per entry, grouped by the same categories as this README:
   ```bash
   plugin google/elephant-goldfish-model egm@egm
   skills thesysdev/skills openui
   skills MengTo/Skills
   ```
4. At the end the script prints the `failed` list and exits with code 1, or prints "Done. Restart Claude Code."

Known limits:

- A plugin that is already installed can show as failed if `claude plugin install` returns an error for it.
- A real `marketplace add` error, such as a network error, is only printed. It shows up as a failed install.

## Coding

### egm (Elephant Goldfish Model)

- Author: Google
- Repository: [google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model)
- Install: `claude plugin marketplace add google/elephant-goldfish-model`, then `claude plugin install egm@egm`
- Use: draft specs with deep-context agents and stress-test them with zero-context reviewer subagents before you write code.

| Skill | What it is for |
|---|---|
| `/egm:egm-brainstorm` | Explores an idea with fresh reviewers and saves the agreed direction in `concepts_brief.md`. |
| `/egm:egm-draft` | Writes a design document from the brief. |
| `/egm:egm-review` | Runs zero-context reviewers against a design document. |
| `/egm:egm-review-loop` | Repeats review and fixes until the reviewers stop finding problems. |
| `/egm:egm-resolve` | Works through the review findings one by one. |
| `/egm:egm-drift-report` | Checks where the code no longer matches the design. |
| `/egm:egm-bootstrap` | Writes README documentation for the directories of an existing codebase. |

### bama (Build Any Mac App)

- Author: Dave Ebbelaar
- Repository: [daveebbelaar/bama](https://github.com/daveebbelaar/bama)
- Install: `claude plugin marketplace add daveebbelaar/bama`, then `claude plugin install bama@bama`
- Use: take a native macOS app in Swift and SwiftUI from idea or a cloned app to a tested build, one user story per commit.

| Skill | What it is for |
|---|---|
| `bama` | Router: finds where you are and calls the right skill. |
| `app-brief` | Turns an idea into a one-page brief. |
| `new-mac-app` | Creates a working app from a template (Swift package, SwiftData, build script, snapshot mode). |
| `research` | Researches market, users, features, design and macOS APIs with parallel agents. |
| `clone` | Screenshots every screen of an app and writes a screen index. |
| `user-stories` | Writes a backlog with checkable acceptance criteria, in milestones. |
| `swift-swiftui` | Swift 6 concurrency, state, SwiftData, AppKit bridges and compiler errors. |
| `os-integrations` | Hotkeys, menu bar, panels, window control, screen capture, Shortcuts and permissions. |
| `performance` | Measures, then fixes main thread, GPU and image problems. |
| `improve-architecture` | Refactors hot spots one step per commit, with behavior proven unchanged. |
| `agent-cli` | Adds a command line and MCP server so agents can drive your app. |
| `ux-design` | Names, flow, words and accessibility, before code. |
| `mac-design` | Liquid Glass, layout, toolbars, menus, keyboard, type and dark mode. |
| `design-system` | Native look with a user-picked accent color and one set of tokens. |
| `layout-grid` | A 4 pt grid with checks that fail on misalignment. |
| `design-kit` | Your own design parts: tokens, type, icons, every part in every state. |
| `design-from-app` | Rebuilds the look of an app from its screenshots, pixel by pixel. |
| `app-icon` | A Liquid Glass icon as an Icon Composer file. |
| `build-and-verify` | Builds, installs and snapshots every page in light and dark mode. |
| `test-mac-app` | Swift Testing, an in-app self-test and a debug bridge for agents. |
| `improve-loop` | Works through the backlog one story per commit until a milestone is done. |

### Understand Anything

- Author: Egonex AI
- Repository: [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)
- Install: `claude plugin marketplace add Egonex-AI/Understand-Anything`, then `claude plugin install understand-anything@understand-anything`
- Use: turn a codebase into an interactive knowledge graph and dashboard, so you can learn how the parts fit together before you change them.

| Skill | What it is for |
|---|---|
| `understand` | Analyzes a codebase and builds the knowledge graph. |
| `understand-dashboard` | Opens the interactive dashboard of the graph. |
| `understand-chat` | Answers questions about the codebase from the graph. |
| `understand-explain` | Deep-dive explanation of one file, function or module. |
| `understand-diff` | Explains what a diff or PR changes, what it affects and its risks. |
| `understand-domain` | Extracts the business domain and builds a domain flow graph. |
| `understand-onboard` | Writes an onboarding guide for new team members. |
| `understand-figma` | Builds a design knowledge graph from a Figma file. |
| `understand-knowledge` | Builds a graph from an LLM wiki knowledge base. |

### mattpocock-skills

- Author: Matt Pocock
- Repository: [mattpocock/skills](https://github.com/mattpocock/skills)
- Install: `claude plugin marketplace add mattpocock/skills`, then `claude plugin install mattpocock-skills@mattpocock`. Run `/setup-matt-pocock-skills` once per repository.
- Use: engineering habits as skills, so the agent asks the right questions, writes specs and tickets, and works test-first.

| Group | What it is for |
|---|---|
| `grilling`, `grill-with-docs`, `wizard` | Question you hard about a plan before any code. |
| `to-spec`, `to-tickets`, `implement`, `implement-spec`, `triage` | Spec and ticket flow, from an idea to implemented work. |
| `tdd`, `diagnosing-bugs`, `prototype` | Test-first work, root-cause debugging, throwaway prototypes. |
| `code-review`, `pr`, `retro` | Review a change, open a PR, look back at the work. |
| `domain-modeling`, `codebase-design`, `improve-codebase-architecture`, `research` | Design the domain and the module structure. |
| `handoff`, `teach`, `wait-what`, `writing-for-agents` | Hand over context, teach a topic, re-explain, write prompts for agents. |

### caveman

- Author: Julius Brussee
- Repository: [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)
- Install: `claude plugin marketplace add JuliusBrussee/caveman`, then `claude plugin install caveman@caveman`
- Use: makes the agent answer in short, plain sentences, which cuts output tokens and keeps code, commands and errors exact. It turns on in every session through a hook.

| Group | What it is for |
|---|---|
| `caveman`, `ultracave`, `megacave` | The terse voice at three levels. |
| `caveman-commit`, `caveman-review`, `caveman-compress` | Short commit messages, one-line review findings, compressed memory files. |
| `cavecrew` | Small subagents for search, one-file edits and review. |
| `investigate-first`, `surgical-patch`, `safe-refactor`, `lean-build`, `migration`, `verify-and-stop` | Work habits: read before you edit, small diffs, verify and stop. |
| `caveman-stats`, `caveman-setup`, `caveman-help` | Token savings, setup and a help card. |

### ponytail

- Author: Dietrich Gebert
- Repository: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)
- Install: `claude plugin marketplace add DietrichGebert/ponytail`, then `claude plugin install ponytail@ponytail`
- Use: makes the agent pick the smallest change that works (reuse, standard library, one line) and shows task cost and tests in a band above the prompt.

| Skill | What it is for |
|---|---|
| `ponytail` | The "lazy senior developer" mode, with levels lite, full and ultra. |
| `ponytail-review` | Reviews a change for logic, safety, load, tests and unneeded code. |
| `ponytail-audit` | One-shot audit of a whole repository. |
| `ponytail-debt` | Lists the shortcuts and their limits left in the code. |
| `ponytail-gain` | Shows what the mode saved. |
| `ponytail-help` | Quick reference. |

### OpenUI

- Author: Thesys
- Repository: [thesysdev/openui](https://github.com/thesysdev/openui) (the skill is in [thesysdev/skills](https://github.com/thesysdev/skills/tree/main/skills/openui))
- Install: `npx skills@latest add thesysdev/skills -g -a claude-code -s openui -y` (no Claude Code plugin)
- Use: helps build Generative UI apps where the LLM answers with UI in OpenUI Lang, not plain text.

| Skill | What it is for |
|---|---|
| `openui` | Component library design, OpenUI Lang syntax, system prompts, the Renderer, SDK packages and debugging bad LLM output. |

### REA (Reverse Engineer Anything)

- Author: morluto
- Repository: [morluto/rea](https://github.com/morluto/rea) ([site](https://rea.tools/))
- Install: `claude plugin marketplace add morluto/rea`, then `claude plugin install rea@rea`. It also adds the REA MCP server. Needs Node.js 22 or later. Native binaries need Hopper, Ghidra or IDA.
- Use: one MCP server to reverse engineer native binaries, JavaScript and Electron apps, .NET assemblies and websites, with the evidence behind each finding.

| Skill | What it is for |
|---|---|
| `reverse-engineer-anything` | Explains how a feature of an app works from its shipped files or runtime, decompiles code, compares versions and guides a rebuild in your project. |

## Design

### Agent Skills

- Author: Meng To
- Repository: [MengTo/Skills](https://github.com/MengTo/Skills)
- Install: `npx skills@latest add MengTo/Skills -g -a claude-code -s '*' -y` (the repository has no Claude Code plugin, so the skills go to `~/.claude/skills/`)
- Use: turn design references into prompts and build rich UI, 3D scenes, illustrations and Three.js games.

| Group | What it is for |
|---|---|
| `web-design`, `ui` | Landing pages, UI styles and interaction details. |
| `codex` | Workflows such as video to super prompt, HTML to interaction prompts and full-page capture. |
| `3d` | Realistic water, sky, materials, textures and virtual tours in WebGL. |
| `illustration` | 14 hand-written SVG illustration styles with palettes and a render-and-lint loop. |
| `game-development`, `game-combat` | Three.js game systems, levels, combat and VFX. |
| `media`, `workflow` | Media generation and reusable agent loops. |

### Dembrandt

- Author: Dembrandt
- Repository: [dembrandt/dembrandt-skills](https://github.com/dembrandt/dembrandt-skills) ([site](https://www.dembrandt.com/skills))
- Install: `claude plugin marketplace add dembrandt/dembrandt-skills`, then `claude plugin install dembrandt@dembrandt`. It also adds the Dembrandt MCP server.
- Use: extract the real design system (colors, type, spacing, components) from a live URL and apply around 40 UX rules to your UI.

| Group | What it is for |
|---|---|
| `dembrandt`, `extract-design`, `generate-ui-from-brand`, `clone-website` | Pipeline: from a URL or `DESIGN.md` to tokens, UX decisions and a UI spec. |
| `wcag-accessibility`, `nielsen-usability-heuristics`, `gestalt-ui-organisation` | Accessibility and usability checks. |
| `modular-scale-typography`, `algorithmic-color-palette`, `elevation-and-depth`, `color-mode-and-theme` | Tokens: type scale, colors, shadows, themes. |
| `form-design`, `button-states`, `tab-navigation`, `modal-and-overlay-patterns`, `data-display-and-selection` | Component patterns. |
| `layout-paradigms-and-consistency`, `responsive-paradigms`, `ui-density`, `app-shell` | Layout and structure. |
| `loading-states-and-perceived-performance`, `performance-and-web-vitals`, `micro-interactions` | Speed and feedback. |

### emilkowalski/skills

- Author: Emil Kowalski
- Repository: [emilkowalski/skills](https://github.com/emilkowalski/skills)
- Install: `npx skills@latest add emilkowalski/skills -g -a claude-code -s '*' -y` (no Claude Code plugin)
- Use: design engineering taste for the agent: animations that feel right, UI polish and native-feeling interactions.

| Skill | What it is for |
|---|---|
| `animate`, `animate-expo` | Builds an animation on the web or in Expo, decision by decision. |
| `review-animations`, `improve-animations`, `find-animation-opportunities` | Reviews existing motion, plans fixes, finds where motion is missing. |
| `animation-performance`, `animation-vocabulary` | Keeps animations in the frame budget; names an effect you can only describe. |
| `emil-design-eng`, `apple-design`, `mobile-native` | UI polish and Apple-style interaction rules. |
| `break-ui` | Stress-tests a component with worst-case data. |
| `prototype`, `pick-ui-library`, `ask-sonner`, `write-swift` | UI variants behind a picker, library choice, Sonner toasts, Swift code. |

## Writing

### unslop

- Author: Benjamin Connelly
- Repository: [Benjamin-Connelly/cursor-plugins](https://github.com/Benjamin-Connelly/cursor-plugins/blob/main/pstack/skills/unslop/SKILL.md) (part of the `pstack` Cursor plugin)
- Install: `npx skills@latest add Benjamin-Connelly/cursor-plugins -g -a claude-code -s unslop -y` (only this skill)
- Use: removes AI tells from text and adds a human voice, for docs, posts and messages.

| Skill | What it is for |
|---|---|
| `unslop` | Finds AI writing patterns, rewrites them and self-checks the result. |

The repository has no license file.
