#!/usr/bin/env bash
# Build, hydrate, and publish dist/ to the gh-pages branch.
#
# Why this exists: `blogr deploy` (0.5.1) builds into a temp directory and pushes
# that — so any post-build patching of ./dist (e.g. inlining the JS-paginated
# posts via scripts/hydrate-index.py) is invisible to it. This script does the
# same job with the steps in the right order.
#
# Auth: relies on whatever credentials git already has for `origin`. Local devs
# get SSH; in GitHub Actions, actions/checkout@v4 + `permissions: contents: write`
# configures HTTPS auth via GITHUB_TOKEN automatically.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
REPO_ROOT=$(pwd)
BRANCH=${DEPLOY_BRANCH:-gh-pages}

echo "[1/3] Building site..."
blogr build

echo "[2/3] Hydrating home page (inlining JS-paginated posts)..."
python3 scripts/hydrate-index.py

echo "[3/3] Publishing dist/ to '$BRANCH'..."

WORKTREE=$(mktemp -d -t blogr-deploy.XXXXXX)
cleanup() {
    (cd "$REPO_ROOT" && git worktree remove --force "$WORKTREE" 2>/dev/null) || true
    rm -rf "$WORKTREE"
}
trap cleanup EXIT

git fetch origin "$BRANCH" --quiet
git worktree add --quiet -B "$BRANCH" "$WORKTREE" "origin/$BRANCH"

rsync -a --delete --exclude '.git' "$REPO_ROOT/dist/" "$WORKTREE/"

cd "$WORKTREE"
git add -A

if git diff --cached --quiet HEAD; then
    echo "No changes to deploy."
    exit 0
fi

COMMIT_AUTHOR_NAME=${DEPLOY_NAME:-blogr-deploy}
COMMIT_AUTHOR_EMAIL=${DEPLOY_EMAIL:-deploy@bahdotsh.users.noreply.github.com}
SOURCE_SHA=$(git -C "$REPO_ROOT" rev-parse --short HEAD)

git \
    -c user.name="$COMMIT_AUTHOR_NAME" \
    -c user.email="$COMMIT_AUTHOR_EMAIL" \
    -c commit.gpgsign=false \
    commit -m "Deploy site from $SOURCE_SHA"

git push origin "$BRANCH"
echo "Deployed."
