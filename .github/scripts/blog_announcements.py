"""Turn blog posts with an `announcement` front matter block into announcements.

Writes `entries` (a JSON array of {name, content}) to GITHUB_OUTPUT. Front matter
is read with yq, which is preinstalled on GitHub-hosted Ubuntu runners.
"""

import json
import os
from pathlib import PurePosixPath
import re
import subprocess
import sys


BLOG = "content/en/blog/"
# Lowercase names keep the derived URL identical to Hugo's.
SEGMENTS = re.compile(r"[a-z0-9][a-z0-9-]*(?:/[a-z0-9][a-z0-9-]*)*")
BUFFER_CHANNELS = {"linkedin", "bluesky", "mastodon"}


class PostError(Exception):
    pass


def front_matter(path):
    result = subprocess.run(
        [os.environ.get("YQ", "yq"), "--front-matter=extract", "-o=json", ".", path],
        capture_output=True, text=True,
    )
    if result.returncode:
        raise PostError(f"{path}: cannot read front matter: {result.stderr.strip()}")
    data = json.loads(result.stdout or "null")
    if not isinstance(data, dict):
        raise PostError(f"{path}: front matter must be a mapping")
    return data


def post_path(path):
    """content/en/blog/2026/slug/index.md and content/en/blog/2026/slug.md -> 2026/slug"""
    relative = path.removeprefix(BLOG).removesuffix(".md").removesuffix("/index")
    return relative if SEGMENTS.fullmatch(relative) else None


def announcement(path, site_url):
    """Return the announcement for a post, or a reason why it is not announced."""
    data = front_matter(path)
    if data.get("draft") is True:
        return "draft"
    if "announcement" not in data:
        return "no announcement block"
    relative = post_path(path)
    if relative is None:
        raise PostError(f"{path}: use lowercase letters, digits, and hyphens in blog paths")
    for key in ("url", "slug"):
        if key in data:
            raise PostError(f"{path}: announced posts cannot set `{key}`; the URL comes from the path")
    block = data["announcement"]
    if not isinstance(block, dict) or set(block) != {"text"} or not isinstance(block["text"], str):
        raise PostError(f"{path}: `announcement` must contain only a `text` string")
    if not isinstance(data.get("title"), str):
        raise PostError(f"{path}: a `title` is required")
    if not re.fullmatch(r"https://[a-z0-9.-]+/?", site_url):
        raise PostError("Set the SITE_URL variable to the site's https:// address")
    return {
        "title": data["title"].strip(),
        "text": block["text"].strip(),
        "url": f"{site_url.rstrip('/')}/blog/{relative}/",
    }


def changed_posts(base, head, diff_filter):
    if set(base) == {"0"}:
        # A new branch has no previous commit to compare against. Announcing every
        # post would repeat old announcements, so announce nothing.
        print("::warning::No previous commit; no posts are announced.")
        return []
    output = subprocess.check_output([
        "git", "diff", "--name-only", "-z", "--find-renames", f"--diff-filter={diff_filter}",
        base, head, "--", f"{BLOG}*.md",
    ])
    paths = [path for path in output.decode().split("\0") if path]
    return [path for path in paths if PurePosixPath(path).name != "_index.md"]


def main():
    event = os.environ["EVENT_NAME"]
    site_url = os.environ.get("SITE_URL", "")
    if event == "workflow_dispatch":
        paths = [os.environ["POST"]]
    elif event == "pull_request":
        paths = changed_posts(os.environ["BASE"], "HEAD", "AM")
    else:
        paths = changed_posts(os.environ["BASE"], os.environ["GITHUB_SHA"], "A")

    mode = os.environ.get("MODE", "check")
    buffer = BUFFER_CHANNELS & set(json.loads(os.environ.get("CHANNELS") or "[]"))
    if mode == "publish" and buffer:
        # Buffer is drafts-only in this playground until draft behavior is verified.
        raise SystemExit(f"publish is not allowed for Buffer channels: {sorted(buffer)}")

    entries, errors = [], []
    for path in paths:
        if not path.startswith(BLOG) or not path.endswith(".md") or ".." in path.split("/"):
            errors.append(f"{path}: not a blog post")
            continue
        try:
            content = announcement(path, site_url)
        except PostError as exc:
            errors.append(str(exc))
            continue
        if isinstance(content, str):
            print(f"{path}: {content}; skipped.", file=sys.stderr)
            continue
        print(f"{path}: announcing {content['url']}", file=sys.stderr)
        entries.append({"name": f"post-{len(entries)}", "path": path, "content": content})
    for error in errors:
        print(f"::error::{error}")
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write("entries=" + json.dumps(entries) + "\n")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
