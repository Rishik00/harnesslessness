#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
default_roadmap="${script_dir}/../docs/issue-roadmap.md"
issues_file="${1:-$default_roadmap}"
gh_bin="${GH_BIN:-gh}"

if [[ -x "$gh_bin" ]]; then
  gh_cmd="$gh_bin"
elif command -v "$gh_bin" >/dev/null 2>&1; then
  gh_cmd="$gh_bin"
else
  printf 'error: gh not found. Set GH_BIN or install GitHub CLI.\n' >&2
  exit 1
fi

if [[ ! -f "$issues_file" ]]; then
  printf 'error: issues file not found: %s\n' "$issues_file" >&2
  exit 1
fi

create_issue() {
  local title="$1"
  local body="$2"
  local body_file
  body_file="$(mktemp)"
  printf '%s\n' "$body" >"$body_file"

  if [[ -n "${DRY_RUN:-}" ]]; then
    printf 'DRY_RUN: would create issue: %s\n' "$title"
    printf '%s\n' "---"
    printf '%s\n' "$body"
    printf '%s\n' "---"
    rm -f "$body_file"
    return 0
  fi

  "$gh_cmd" issue create --title "$title" --body-file "$body_file"
  printf 'created: %s\n' "$title"
  rm -f "$body_file"
}

title=""
body=""

while IFS= read -r line || [[ -n "$line" ]]; do
  case "$line" in
    '## '*)
      if [[ -n "$title" ]]; then
        create_issue "$title" "$body"
        body=""
      fi
      title="${line#'## '}"
      continue
      ;;
  esac

  if [[ -z "$title" ]]; then
    continue
  fi

  if [[ -z "$body" ]]; then
    body="$line"
  else
    body+=$'\n'"$line"
  fi
done <"$issues_file"

if [[ -n "$title" ]]; then
  create_issue "$title" "$body"
fi
