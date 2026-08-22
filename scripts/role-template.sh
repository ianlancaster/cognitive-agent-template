#!/usr/bin/env bash
# Role-template primitives: read/write .template-sync.json fields, migrate a
# legacy instance to the role-aware schema, and leak-check a candidate artifact
# before it is contributed up to a template.
#
# Usage:
#   scripts/role-template.sh get <sync-json> <field>
#   scripts/role-template.sh set <sync-json> <field> <value>     # value "null" -> JSON null
#   scripts/role-template.sh migrate <sync-json>                  # idempotent; seeds safe defaults
#   scripts/role-template.sh leak-check <file> [extra-regex ...]  # exit 1 if potential history found
#   scripts/role-template.sh should-contribute <sync-json>        # exit 0 if this instance may contribute up
#   scripts/role-template.sh candidates [since-ref]               # portable-candidate files changed since ref
#
# leak-check / should-contribute exit codes: 0 = yes/clean, 1 = no/leak (reason printed), 2 = usage/error.

set -euo pipefail

die() { echo "role-template: $*" >&2; exit 2; }
need_jq() { command -v jq >/dev/null 2>&1 || die "jq is required but not installed"; }
need_git() { git rev-parse --git-dir >/dev/null 2>&1 || die "not inside a git repository"; }

atomic_write_json() {
  # $1 = destination, stdin = JSON content
  local dest="$1" tmp
  tmp="$(mktemp "${dest}.XXXXXX")"
  cat > "$tmp"
  mv -f "$tmp" "$dest"
}

cmd_get() {
  need_jq
  local file="${1:?usage: get <sync-json> <field>}" field="${2:?usage: get <sync-json> <field>}"
  [ -f "$file" ] || die "no such file: $file"
  jq -r --arg f "$field" 'if has($f) then .[$f] else "null" end | if . == null then "null" else . end' "$file"
}

cmd_set() {
  need_jq
  local file="${1:?usage: set <sync-json> <field> <value>}" field="${2:?}" value="${3-}"
  [ -f "$file" ] || die "no such file: $file"
  if [ "$value" = "null" ]; then
    jq --arg f "$field" '.[$f] = null' "$file" | atomic_write_json "$file"
  else
    jq --arg f "$field" --arg v "$value" '.[$f] = $v' "$file" | atomic_write_json "$file"
  fi
}

# Migrate a legacy instance's .template-sync.json to the role-aware schema.
# Conservative by design: a legacy agent has no defined role and no role
# template to receive contributions, so contributionMode defaults to "locked"
# (nothing flows up until deliberately enabled). Idempotent: a file that already
# has "kind" is left untouched.
cmd_migrate() {
  need_jq
  local file="${1:?usage: migrate <sync-json>}"
  [ -f "$file" ] || die "no such file: $file"
  if [ "$(jq 'has("kind")' "$file")" = "true" ]; then
    echo "already-migrated: $file"
    return 0
  fi
  jq '
    .kind = "instance"
    | .role = null
    | .contributionMode = "locked"
    | .lastContributedCommit = null
  ' "$file" | atomic_write_json "$file"
  echo "migrated: $file (kind=instance role=null contributionMode=locked)"
}

# Leak-check: scan a candidate artifact for coupling to a specific instance's
# history before it is contributed up. Deliberately over-broad — a false
# positive costs a glance, a false negative pollutes every future instance.
# Default patterns are structural (dates, session/event ids). Callers (e.g. the
# templatize ritual) pass instance-specific proper nouns as extra regexes.
cmd_leak_check() {
  local file="${1:?usage: leak-check <file> [extra-regex ...]}"
  shift || true
  [ -f "$file" ] || die "no such file: $file"

  local -a patterns=(
    '[0-9]{4}-[0-9]{2}-[0-9]{2}'      # ISO dates
    '\bsession[ -]?[0-9]+'            # session numbers
    '\bEV-[0-9]+'                     # event ids
    '\b[0-9]+/[0-9]+ (units|mutants|tests|seeds)\b'  # specific measurements
  )
  local p
  for p in "$@"; do patterns+=("$p"); done

  local alt found=0
  alt="$(IFS='|'; echo "${patterns[*]}")"
  # -n line numbers, -E extended, -i case-insensitive
  if grep -nEi "$alt" "$file" >/tmp/.rt-leak.$$ 2>/dev/null; then
    found=1
    echo "POTENTIAL LEAK in $file — review and clear each hit:"
    cat /tmp/.rt-leak.$$
  fi
  rm -f /tmp/.rt-leak.$$
  if [ "$found" -eq 1 ]; then
    return 1
  fi
  echo "clean: $file"
  return 0
}

# The gate the /deep-sleep up-contribution phase checks first. Exit 0 only if
# this repo is an instance with a role, a role-template remote, and a
# contributionMode that permits writing up. Anything else is a clean no-op.
cmd_should_contribute() {
  need_jq
  local file="${1:?usage: should-contribute <sync-json>}"
  [ -f "$file" ] || die "no such file: $file"
  local kind role mode remote
  kind="$(jq -r '.kind // "null"' "$file")"
  role="$(jq -r '.role // "null"' "$file")"
  mode="$(jq -r '.contributionMode // "null"' "$file")"
  remote="$(jq -r '.templateRemote // "null"' "$file")"
  if [ "$kind" != "instance" ]; then echo "no: kind is '$kind' (only instances contribute up)"; return 1; fi
  if [ "$role" = "null" ] || [ -z "$role" ]; then echo "no: no role assigned"; return 1; fi
  if [ "$remote" = "null" ] || [ -z "$remote" ]; then echo "no: no templateRemote"; return 1; fi
  case "$mode" in
    approve|auto) echo "yes: contributionMode=$mode"; return 0 ;;
    *)            echo "no: contributionMode is '$mode'"; return 1 ;;
  esac
}

# List portable-candidate files changed since <since-ref> (or all tracked
# candidates if no ref / "null"). Instance-only paths (journal, conversations,
# plans, project_/user_ memory, context state) are absent from the allowlist and
# so are never listed. Empty output = graceful no-op: nothing to contribute.
cmd_candidates() {
  need_git
  local since="${1-}" list
  if [ -z "$since" ] || [ "$since" = "null" ]; then
    list="$(git ls-files)"
  else
    list="$(git diff --name-only "$since" HEAD)"
  fi
  printf '%s\n' "$list" | grep -E \
    '^memory/(feedback|gotcha|domain|reference)_.*\.md$|^memory/cognition/(beliefs|insight-log|ideation)\.md$|^knowledge/.*|^scripts/.*' \
    || true
}

main() {
  local sub="${1-}"
  shift || true
  case "$sub" in
    get)               cmd_get "$@" ;;
    set)               cmd_set "$@" ;;
    migrate)           cmd_migrate "$@" ;;
    leak-check)        cmd_leak_check "$@" ;;
    should-contribute) cmd_should_contribute "$@" ;;
    candidates)        cmd_candidates "$@" ;;
    ""|-h|--help|help)
      grep -E '^#( |$)' "$0" | sed -E 's/^# ?//'
      ;;
    *) die "unknown subcommand: $sub (try --help)" ;;
  esac
}

main "$@"
