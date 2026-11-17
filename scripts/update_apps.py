#!/usr/bin/env python3
"""Rebuild apps.json from GitHub repos tagged with the `app` topic.

A repo shows up on the dashboard when it:
  - belongs to OWNER,
  - has GitHub Pages turned on,
  - has the topic TOPIC (default "app"),
  - is not archived and is not the homepage repo itself.

Optional: apps.manual.json lets you rename apps, add an emoji, hide one,
or add "coming soon" entries that have no repo yet. See README.
"""
import json
import os
import sys
import urllib.request

OWNER = os.environ.get("APPS_OWNER", "mattkrnr")
TOPIC = os.environ.get("APPS_TOPIC", "app")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.environ.get("APPS_OUT", "apps.json")
MANUAL = os.environ.get("APPS_MANUAL", "apps.manual.json")
HOME_REPO = f"{OWNER}.github.io".lower()


def fetch_repos():
    """All public repos for OWNER (paginated). APPS_FIXTURE overrides for testing."""
    fixture = os.environ.get("APPS_FIXTURE")
    if fixture:
        with open(fixture) as f:
            return json.load(f)
    repos, page = [], 1
    while True:
        url = f"https://api.github.com/users/{OWNER}/repos?per_page=100&page={page}&type=owner"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        if TOKEN:
            req.add_header("Authorization", f"Bearer {TOKEN}")
        with urllib.request.urlopen(req) as r:
            batch = json.load(r)
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def pretty(name):
    return name.replace("-", " ").replace("_", " ").title()


def main():
    manual = {}
    if os.path.exists(MANUAL):
        with open(MANUAL) as f:
            manual = json.load(f)
    overrides = manual.get("overrides", {})

    apps = []
    for r in fetch_repos():
        name = r["name"]
        if name.lower() == HOME_REPO or r.get("archived") or r.get("fork"):
            continue
        if not r.get("has_pages") or TOPIC not in (r.get("topics") or []):
            continue
        o = overrides.get(name, {})
        if o.get("hidden"):
            continue
        apps.append({
            "repo": name,
            "name": o.get("name") or pretty(name),
            "description": o.get("description") or r.get("description") or "",
            "emoji": o.get("emoji", ""),
            "url": o.get("url") or r.get("homepage") or f"https://{OWNER}.github.io/{name}/",
            "source": r["html_url"],
            "status": "live",
            "created": r.get("created_at", ""),
        })

    apps.sort(key=lambda a: a["created"], reverse=True)

    for c in manual.get("coming_soon", []):
        apps.append({"repo": "", "url": "", "source": "", "created": "",
                     "description": "", "emoji": "", **c, "status": "coming_soon"})

    new = json.dumps({"generated_by": "scripts/update_apps.py", "apps": apps}, indent=2, ensure_ascii=False) + "\n"
    old = open(OUT).read() if os.path.exists(OUT) else ""
    if new != old:
        with open(OUT, "w") as f:
            f.write(new)
        print(f"Updated {OUT}: {len(apps)} apps")
    else:
        print(f"{OUT} unchanged ({len(apps)} apps)")


if __name__ == "__main__":
    sys.exit(main())
