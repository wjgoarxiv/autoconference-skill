#!/usr/bin/env bash
set -euo pipefail

# release.sh — bump version, tag, and generate changelog
# Usage: ./scripts/release.sh <version>   e.g.  ./scripts/release.sh 2.1.0

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ── helpers ──────────────────────────────────────────────────────────────────

die() { echo "ERROR: $*" >&2; exit 1; }

usage() {
  echo "Usage: $0 <semver>"
  echo "  e.g. $0 2.1.0"
  exit 1
}

validate_semver() {
  local version="$1"
  if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$ ]]; then
    die "\"$version\" is not valid semver (expected X.Y.Z or X.Y.Z-pre)"
  fi
}

require_clean_git() {
  if ! git -C "$REPO_ROOT" diff --quiet || ! git -C "$REPO_ROOT" diff --cached --quiet; then
    die "Working tree has uncommitted changes. Commit or stash them first."
  fi
}

last_tag() {
  git -C "$REPO_ROOT" describe --tags --abbrev=0 2>/dev/null || echo ""
}

# ── args ─────────────────────────────────────────────────────────────────────

[[ $# -eq 1 ]] || usage
VERSION="$1"
validate_semver "$VERSION"
TAG="v${VERSION}"

echo "Preparing release $TAG …"

# ── pre-flight ────────────────────────────────────────────────────────────────

require_clean_git

if git -C "$REPO_ROOT" rev-parse "$TAG" &>/dev/null; then
  die "Tag $TAG already exists. Choose a different version."
fi

# ── update version fields ─────────────────────────────────────────────────────

PLUGIN_JSON="$REPO_ROOT/.claude-plugin/plugin.json"
GEMINI_JSON="$REPO_ROOT/gemini-extension.json"

update_version() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo "  SKIP  $file (not found)"
    return
  fi
  # Replace "version": "<anything>" with the new version
  local tmp
  tmp="$(mktemp)"
  sed 's/"version": "[^"]*"/"version": "'"$VERSION"'"/' "$file" > "$tmp"
  mv "$tmp" "$file"
  echo "  UPDATED  $file  → $VERSION"
}

update_version "$PLUGIN_JSON"
update_version "$GEMINI_JSON"

# ── changelog entry ───────────────────────────────────────────────────────────

CHANGELOG="$REPO_ROOT/CHANGELOG.md"
PREV_TAG="$(last_tag)"

if [[ -n "$PREV_TAG" ]]; then
  LOG_RANGE="${PREV_TAG}..HEAD"
  echo "Generating changelog from $PREV_TAG → HEAD …"
else
  LOG_RANGE="HEAD"
  echo "No previous tag found — generating changelog from entire history …"
fi

COMMITS="$(git -C "$REPO_ROOT" log "$LOG_RANGE" --oneline --no-decorate 2>/dev/null || true)"

DATE="$(date +%Y-%m-%d)"
ENTRY="## [$VERSION] — $DATE

### Changes since ${PREV_TAG:-initial commit}

$( [[ -n "$COMMITS" ]] && echo "$COMMITS" | sed 's/^/- /' || echo "- (no commits)" )

"

if [[ -f "$CHANGELOG" ]]; then
  # Prepend after the first line (assumed to be the title)
  tmp="$(mktemp)"
  head -n1 "$CHANGELOG" > "$tmp"
  echo "" >> "$tmp"
  echo "$ENTRY" >> "$tmp"
  tail -n +2 "$CHANGELOG" >> "$tmp"
  mv "$tmp" "$CHANGELOG"
else
  printf "# Changelog\n\n%s" "$ENTRY" > "$CHANGELOG"
fi

echo "  CHANGELOG  $CHANGELOG  updated"

# ── commit version bump ───────────────────────────────────────────────────────

git -C "$REPO_ROOT" add "$PLUGIN_JSON" "$GEMINI_JSON" "$CHANGELOG"
git -C "$REPO_ROOT" commit -m "chore(release): bump version to $VERSION"
echo "  COMMIT  version bump committed"

# ── create tag ────────────────────────────────────────────────────────────────

git -C "$REPO_ROOT" tag -a "$TAG" -m "Release $TAG"
echo "  TAG  $TAG created"

# ── done ─────────────────────────────────────────────────────────────────────

echo ""
echo "Release $TAG is ready locally."
echo ""
echo "To publish:"
echo "  git push origin main && git push origin $TAG"
