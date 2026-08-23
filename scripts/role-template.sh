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
#   scripts/role-template.sh should-contribute <sync-json> [class]  # exit 0 if this instance may contribute up (for class)
#   scripts/role-template.sh set-mode <sync-json> <class> <mode>     # set per-class contributionMode; auto on *-authority rejected
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
#
# contributionMode may be a scalar (legacy: one mode for everything) or a map
# {class: mode}. Classes are free-form names with one convention that carries
# the authority floor: a class name ending in "-authority" can NEVER be auto —
# set-mode rejects it and lookup clamps it (defense in depth). Map lookup for
# an absent class falls back to the map's "default" key, else locked.
cmd_should_contribute() {
  need_jq
  local file="${1:?usage: should-contribute <sync-json> [class]}" class="${2-}"
  [ -f "$file" ] || die "no such file: $file"
  local kind role remote mode_type mode
  kind="$(jq -r '.kind // "null"' "$file")"
  role="$(jq -r '.role // "null"' "$file")"
  remote="$(jq -r '.templateRemote // "null"' "$file")"
  if [ "$kind" != "instance" ]; then echo "no: kind is '$kind' (only instances contribute up)"; return 1; fi
  if [ "$role" = "null" ] || [ -z "$role" ]; then echo "no: no role assigned"; return 1; fi
  if [ "$remote" = "null" ] || [ -z "$remote" ]; then echo "no: no templateRemote"; return 1; fi
  mode_type="$(jq -r '.contributionMode | type' "$file")"
  if [ "$mode_type" = "object" ]; then
    [ -n "$class" ] || die "class required: contributionMode is per-class"
    mode="$(jq -r --arg c "$class" '.contributionMode[$c] // .contributionMode["default"] // "locked"' "$file")"
  else
    mode="$(jq -r '.contributionMode // "null"' "$file")"
  fi
  # Authority floor: an authority class is never auto, whatever the config says.
  if [ -n "$class" ] && [[ "$class" == *-authority ]] && [ "$mode" = "auto" ]; then
    mode="approve"
    echo "note: auto clamped to approve for authority class '$class'"
  fi
  case "$mode" in
    approve|auto) echo "yes: contributionMode=$mode${class:+ for $class}"; return 0 ;;
    *)            echo "no: contributionMode is '$mode'${class:+ for $class}"; return 1 ;;
  esac
}

# Set a per-class contribution mode. Converts a legacy scalar to a map on first
# use, preserving the scalar as the "default" key. Enforces the authority
# floor at write time: auto on *-authority is a configuration error.
cmd_set_mode() {
  need_jq
  local file="${1:?usage: set-mode <sync-json> <class> <mode>}" class="${2:?class required}" mode="${3:?mode required}"
  [ -f "$file" ] || die "no such file: $file"
  case "$mode" in approve|auto|locked) ;; *) die "invalid mode: $mode (approve|auto|locked)" ;; esac
  if [[ "$class" == *-authority ]] && [ "$mode" = "auto" ]; then
    die "refused: authority class '$class' can never be auto"
  fi
  jq --arg c "$class" --arg m "$mode" '
    .contributionMode = (if (.contributionMode | type) == "object"
      then .contributionMode
      else {"default": (.contributionMode // "locked")} end)
    | .contributionMode[$c] = $m
  ' "$file" | atomic_write_json "$file"
  echo "set: $class=$mode"
}

# List portable-candidate files changed since <since-ref> (or all tracked
# candidates if no ref / "null"). Instance-only paths (journal, conversations,
# plans, project_/user_ memory, context state) are absent from the allowlist and
# so are never listed. Empty output = graceful no-op: nothing to contribute.
#
# Extension seam: a derived template may ship a .template-candidates file at the
# repo root — one extended regex per line (blank lines and #-comments ignored)
# — to add portable paths WITHOUT forking this script. Data, not code.
cmd_candidates() {
  need_git
  local since="${1-}" list base_re extra_re
  if [ -z "$since" ] || [ "$since" = "null" ]; then
    list="$(git ls-files)"
  else
    list="$(git diff --name-only "$since" HEAD)"
  fi
  base_re='^memory/(feedback|gotcha|domain|reference)_.*\.md$|^memory/cognition/(beliefs|insight-log|ideation)\.md$|^knowledge/.*|^scripts/.*'
  {
    printf '%s\n' "$list" | grep -E "$base_re" || true
    if [ -f .template-candidates ]; then
      while IFS= read -r extra_re; do
        case "$extra_re" in ''|'#'*) continue ;; esac
        printf '%s\n' "$list" | grep -E "$extra_re" || true
      done < .template-candidates
    fi
  } | sort -u
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
    set-mode)          cmd_set_mode "$@" ;;
    candidates)        cmd_candidates "$@" ;;
    ""|-h|--help|help)
      grep -E '^#( |$)' "$0" | sed -E 's/^# ?//'
      ;;
    *) die "unknown subcommand: $sub (try --help)" ;;
  esac
}

main "$@"
