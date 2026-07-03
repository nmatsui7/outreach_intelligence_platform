#!/usr/bin/env bash
# Export a clean copy of the project, excluding artifacts.
# Usage: bash scripts/export_clean.sh [output_dir]
# Default: creates ../outreach_intelligence_platform_clean/
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-"$SRC/../outreach_intelligence_platform_clean"}"

echo "Exporting clean project from $SRC"
echo "  to $DEST"

mkdir -p "$DEST"

# Use rsync to copy all files except excluded patterns
rsync -a --delete \
  --exclude='.venv/' \
  --exclude='.git/' \
  --exclude='.env' \
  --exclude='__MACOSX/' \
  --exclude='.DS_Store' \
  --exclude='backend/app/data/*.backup.json' \
  --exclude='__pycache__/' \
  --exclude='*.py[cod]' \
  --exclude='ai_note*.md' \
  --exclude='gemma4_official.jinja' \
  --exclude='phase4.md' \
  --exclude='Additional_UI_prompt.md' \
  "$SRC"/ "$DEST"

echo ""
echo "Done. Size:"
du -sh "$DEST"
echo ""
echo "Contents:"
ls -la "$DEST"
