#!/usr/bin/env bash
# Installs or updates every plugin in this folder for Claude Code on this machine.
# Run manually: ./claude-plugins/setup.sh
# Needs: claude (Claude Code CLI).
set -u

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
market=skrupa-skills # "name" in .claude-plugin/marketplace.json
failed=()

# Local-path marketplace: a git pull in this repo is picked up by the update below.
claude plugin marketplace add "$dir" || echo "marketplace already added or failed, continuing"
claude plugin marketplace update "$market" || failed+=("marketplace $market")

for p in "$dir"/*/.claude-plugin/plugin.json; do
  [ -e "$p" ] || continue
  name="$(basename "$(dirname "$(dirname "$p")")")"
  # update fails when the plugin is not installed yet, so fall back to install
  claude plugin update "$name@$market" || claude plugin install "$name@$market" || failed+=("$name")
done

if ((${#failed[@]})); then
  echo "Failed: ${failed[*]}" >&2
  exit 1
fi
echo "Done. Restart Claude Code."
