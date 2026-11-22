#!/usr/bin/env bash
# AI Documentary Video-Making Studio Skill (v4.0) — macOS/Linux 1-Click Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/gmakercodeby-arch/ai-documentary-video-studio-skill/main/install.sh | bash

set -euo pipefail

REPO_URL="https://github.com/gmakercodeby-arch/ai-documentary-video-studio-skill.git"
SKILL_NAME="ai-documentary-studio"
PRIMARY="$HOME/.gemini/config/skills/$SKILL_NAME"

echo ""
echo "=== AI Documentary Video-Making Studio Skill (v4.0) — 1-Click Install ==="

command -v git >/dev/null 2>&1 || { echo "Error: git is required."; exit 1; }

mkdir -p "$(dirname "$PRIMARY")"
if [ -d "$PRIMARY/.git" ]; then
  echo "[1/3] Updating existing skill in $PRIMARY ..."
  git -C "$PRIMARY" pull --ff-only
else
  echo "[1/3] Cloning skill into $PRIMARY ..."
  git clone --depth 1 "$REPO_URL" "$PRIMARY"
fi

for EXTRA_ROOT in "$HOME/.claude" "$HOME/.cursor"; do
  if [ -d "$EXTRA_ROOT" ]; then
    mkdir -p "$EXTRA_ROOT/skills"
    rm -rf "$EXTRA_ROOT/skills/$SKILL_NAME"
    cp -R "$PRIMARY" "$EXTRA_ROOT/skills/$SKILL_NAME"
    echo "      Synced skill to $EXTRA_ROOT/skills/$SKILL_NAME"
  fi
done

echo "[2/3] Installing Python dependencies..."
PY_BIN=$(command -v python3 || command -v python)
"$PY_BIN" -m pip install --upgrade -r "$PRIMARY/requirements.txt"

echo "[3/3] Running Stage-0 Environment & GPU Doctor..."
"$PY_BIN" "$PRIMARY/scripts/check_setup.py"

echo ""
echo "DONE! Skill installed at: $PRIMARY"
echo "Now tell your AI Agent: 'Use ai-documentary-studio to set up my studio and make a documentary!'"
