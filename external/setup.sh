#!/usr/bin/env bash
# Installs the notable external plugins and skills listed in README.md.
# Run manually: ./external/setup.sh
# Needs: claude (Claude Code CLI), npx (Node.js).
set -u

failed=()

plugin() { # plugin <github owner/repo> <plugin@marketplace>
  claude plugin marketplace add "$1" || echo "marketplace $1 already added or failed, continuing"
  claude plugin install "$2" || failed+=("$2")
}

skills() { # skills <github owner/repo> [skill]: repos without a Claude Code plugin; no skill = all skills
  npx -y skills@latest add "$1" -g -a claude-code -s "${2:-*}" -y || failed+=("$1${2:+ $2}")
}

# Coding
plugin google/elephant-goldfish-model egm@egm
plugin daveebbelaar/bama bama@bama
plugin Egonex-AI/Understand-Anything understand-anything@understand-anything
plugin mattpocock/skills mattpocock-skills@mattpocock
plugin JuliusBrussee/caveman caveman@caveman
plugin DietrichGebert/ponytail ponytail@ponytail
skills thesysdev/skills openui
plugin morluto/rea rea@rea
plugin microsoft/TokenEconomizer tokeneconomizer@tokeneconomizer

# Design
skills MengTo/Skills
plugin dembrandt/dembrandt-skills dembrandt@dembrandt
skills emilkowalski/skills

# Writing
skills Benjamin-Connelly/cursor-plugins unslop

if ((${#failed[@]})); then
  echo "Failed: ${failed[*]}" >&2
  exit 1
fi
echo "Done. Restart Claude Code."
