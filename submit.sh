#!/usr/bin/env bash
# EAS 510 - Project 1
# Stage everything, commit, and push to your fork on GitHub.
# Usage: ./submit.sh "<your commit message>"

set -euo pipefail

MSG="${1:-update (submitted from Codio)}"

git add -A
if git diff --cached --quiet; then
  echo "Nothing to commit or push."
  exit 0
fi

git commit -m "$MSG"
git push origin "$(git symbolic-ref --short HEAD)"

echo "Pushed. Refresh your fork on GitHub to see your commit."