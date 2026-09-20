#!/usr/bin/env bash
# EAS 510 - Project 1
# Run this ONCE on day one in your Codio box, after you have forked the
# starter repo on GitHub. It points this box at YOUR fork and does the
# first push so every later submit.sh is silent.

set -euo pipefail

REPO_OWNER="delveccj"
REPO_NAME="EAS510_Assignment1_starter"
MAIN_BRANCH="main"

echo "== EAS 510 Project 1: git setup =="

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "No repo here yet. Are you in the right folder? (run from the project root)"
  exit 1
fi

read -rp "Your GitHub username: " USER
FORK_URL="https://github.com/${USER}/${REPO_NAME}.git"

git config user.name "$(git config user.name 2>/dev/null || git config --global user.name || echo '')"
if [ -z "$(git config user.name)" ]; then
  read -rp "Your full name (for commits): " NAME
  git config user.name "$NAME"
fi
if [ -z "$(git config user.email)" ]; then
  read -rp "Your @buffalo.edu email: " EMAIL
  git config user.email "$EMAIL"
fi

git config --global credential.helper store

git remote remove origin >/dev/null 2>&1 || true
git remote add origin "$FORK_URL"

git add -A
if git diff --cached --quiet; then
  echo "Nothing new to commit."
else
  git commit -m "setup: first push from Codio box ($(date +%F))"
fi

if ! git rev-parse -q --verify "refs/heads/${MAIN_BRANCH}" >/dev/null; then
  git branch -m "${MAIN_BRANCH}"
fi

git push -u origin "${MAIN_BRANCH}"

echo
echo "Linked this box to your fork:"
echo "  https://github.com/${USER}/${REPO_NAME}"
echo "Next push will not ask for a token again."
echo "Use ./submit.sh every time you finish work."