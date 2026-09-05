#!/usr/bin/env python3
"""Read-only full-content audit of template infrastructure and recorded divergence."""

import argparse
import hashlib
import json
import stat
import subprocess
from pathlib import Path


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def in_scope(path):
    parts = Path(path).parts
    return (
        path in {"AGENTS.md", "CLAUDE.md", "COGNITIVE.md", ".codex/config.toml"}
        or path.startswith(".agents/skills/")
        or path.startswith("tests/")
        or (len(parts) == 3 and parts[:2] == (".claude", "commands") and path.endswith(".md"))
        or (len(parts) == 2 and parts[0] == "scripts")
        or (len(parts) == 2 and parts[0] == "knowledge" and path.endswith(".md"))
    )


def tree(repo, revision):
    result = {}
    for record in git(repo, "ls-tree", "-rz", revision).split(b"\0"):
        if not record:
            continue
        metadata, name = record.split(b"\t", 1)
        mode, kind, blob = metadata.decode().split()
        path = name.decode()
        if in_scope(path):
            if kind != "blob":
                raise ValueError(f"Unsupported infrastructure entry: {path}")
            result[path] = {"mode": mode, "sha256": hashlib.sha256(git(repo, "cat-file", "blob", blob)).hexdigest()}
    return result


def local_content(root, path):
    file = root / path
    # Do not dereference directory symlinks outside the candidate repository.
    if any(parent.is_symlink() for parent in file.parents if parent != root and root in parent.parents):
        return {"mode": "symlink-parent", "sha256": None}
    try:
        mode = file.lstat().st_mode
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(mode):
        return {"mode": "120000", "sha256": hashlib.sha256(str(file.readlink()).encode()).hexdigest()}
    if not stat.S_ISREG(mode):
        return {"mode": "non-file", "sha256": None}
    return {"mode": "100755" if mode & stat.S_IXUSR else "100644", "sha256": hashlib.sha256(file.read_bytes()).hexdigest()}


def audit(local, template, base=None, dispositions=None):
    target = git(template, "rev-parse", "HEAD").decode().strip()
    current = tree(template, target)
    if "COGNITIVE.md" not in current:
        raise ValueError("Selected repository is missing COGNITIVE.md; refusing an empty or wrong-template audit")
    previous = tree(template, base) if base else {}
    records = []
    for path in sorted(current.keys() | previous.keys()):
        upstream = current.get(path)
        actual = local_content(local, path)
        record = {"file": path, "templateCommit": target, "upstream": upstream, "local": actual}
        prior = (dispositions or {}).get(path, {})
        if actual == upstream:
            record["status"] = "matched"
        elif (prior.get("status") == "diverged-intentionally"
              and isinstance(prior.get("reason"), str) and prior["reason"].strip()
              and all(prior.get(key) == record[key] for key in ("templateCommit", "upstream", "local"))):
            record.update(status="diverged-intentionally", reason=prior["reason"])
        else:
            record["status"] = "unresolved"
        records.append(record)
    return {"templateCommit": target, "files": records,
            "complete": all(row["status"] != "unresolved" for row in records)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", type=Path, default=Path.cwd())
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--base", help="previous template commit, to include removed paths")
    parser.add_argument("--dispositions", type=Path, help="prior audit JSON with explicitly justified divergence")
    args = parser.parse_args()
    dispositions = {}
    if args.dispositions:
        dispositions = {row["file"]: row for row in json.loads(args.dispositions.read_text())["files"]}
    result = audit(args.local.resolve(), args.template.resolve(), args.base, dispositions)
    print(json.dumps(result, indent=2))
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
