#!/usr/bin/env python3
"""Copy upstream files into sources/ and record them in sources/sources.lock.json.

Every template under sources/ is a byte-for-byte copy of a path in a public
GitHub repository at one pinned commit. The lock file records, for each copied
file, the git blob hash GitHub reports at that commit, so check.py can prove
offline that nothing under sources/ was edited.

Usage:
    python sources.py add OWNER/REPO PATH [PATH ...] [--ref REF] [--kind KIND]

PATH is a folder or file in the upstream repository. It lands at
sources/OWNER/<last part of PATH>, or at sources/OWNER/LICENSE.REPO for
--kind license. Set GITHUB_TOKEN (or GH_TOKEN) to avoid the anonymous API
rate limit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources"
LOCK = SOURCES / "sources.lock.json"
KINDS = ("skill", "license", "extra")


def blob_sha(data: bytes) -> str:
    """The git blob hash of data, as `git hash-object` computes it."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _token() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def _get(url: str, *, api: bool) -> bytes:
    headers = {"User-Agent": "ai-workflow-sources"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
    token = _token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def resolve_commit(repo: str, ref: str) -> str:
    data = json.loads(_get(f"https://api.github.com/repos/{repo}/commits/{ref}", api=True))
    return data["sha"]


def upstream_tree(repo: str, commit: str) -> dict[str, dict]:
    """Map every path in repo at commit to its tree entry."""
    url = f"https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1"
    data = json.loads(_get(url, api=True))
    if data.get("truncated"):
        raise SystemExit(f"{repo}: tree listing is truncated; cannot verify it")
    return {entry["path"]: entry for entry in data["tree"]}


def files_under(tree: dict[str, dict], path: str) -> dict[str, dict]:
    """Blob entries at path (a file) or below it (a folder), keyed relative to path."""
    if path in tree and tree[path]["type"] == "blob":
        return {"": tree[path]}
    prefix = path.rstrip("/") + "/"
    found = {
        name[len(prefix):]: entry
        for name, entry in tree.items()
        if name.startswith(prefix) and entry["type"] == "blob"
    }
    if not found:
        raise SystemExit(f"{path}: not found upstream")
    return found


def load_lock() -> dict:
    if LOCK.is_file():
        return json.loads(LOCK.read_text(encoding="utf-8"))
    return {"entries": {}}


def save_lock(lock: dict) -> None:
    lock["entries"] = dict(sorted(lock["entries"].items()))
    LOCK.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")


def local_name(repo: str, path: str, kind: str) -> str:
    owner, name = repo.split("/")
    if kind == "license":
        return f"{owner}/LICENSE.{name}"
    return f"{owner}/{PurePosixPath(path).name}"


def add(repo: str, paths: list[str], ref: str, kind: str) -> None:
    commit = resolve_commit(repo, ref)
    tree = upstream_tree(repo, commit)
    lock = load_lock()
    for path in paths:
        name = local_name(repo, path, kind)
        owned = lock["entries"].get(name)
        if owned and owned["repo"] != repo:
            raise SystemExit(f"sources/{name} already comes from {owned['repo']}")
        blobs = files_under(tree, path)
        target = SOURCES / name
        recorded: dict[str, str] = {}
        for relative, entry in sorted(blobs.items()):
            if entry["mode"] == "120000":
                raise SystemExit(f"{path}/{relative}: symlinks are not supported")
            upstream_path = f"{path}/{relative}" if relative else path
            quoted = urllib.parse.quote(upstream_path)
            data = _get(
                f"https://raw.githubusercontent.com/{repo}/{commit}/{quoted}", api=False
            )
            if blob_sha(data) != entry["sha"]:
                raise SystemExit(f"{upstream_path}: download does not match upstream hash")
            destination = target / relative if relative else target
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            if entry["mode"] == "100755":
                destination.chmod(0o755)
            recorded[relative] = entry["sha"]
        lock["entries"][name] = {
            "kind": kind,
            "repo": repo,
            "commit": commit,
            "path": path,
            "files": recorded,
        }
        print(f"sources/{name} <- {repo}@{commit[:7]}:{path} ({len(recorded)} files)")
    save_lock(lock)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    add_parser = commands.add_parser("add", help="copy upstream paths into sources/")
    add_parser.add_argument("repo", help="OWNER/REPO on GitHub")
    add_parser.add_argument("paths", nargs="+", help="folders or files in that repo")
    add_parser.add_argument("--ref", default="HEAD", help="branch, tag, or commit (default: HEAD)")
    add_parser.add_argument("--kind", choices=KINDS, default="skill")
    args = parser.parse_args()
    if args.command == "add":
        add(args.repo, args.paths, args.ref, args.kind)
    return 0


if __name__ == "__main__":
    sys.exit(main())
