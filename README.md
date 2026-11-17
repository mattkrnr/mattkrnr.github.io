# mattkrnr.github.io

Central dashboard for my apps.

## How apps get listed

A GitHub Action (`.github/workflows/update-apps.yml`) runs daily and rebuilds `apps.json` from my repos.
A repo is listed when it:

1. has **GitHub Pages** turned on, and
2. has the **`app` topic** (repo page → ⚙️ next to "About" → Topics).

Archived repos, forks and this repo are skipped.
For an instant refresh: **Actions → Update app list → Run workflow**.

## Customizing (`apps.manual.json`)

- `overrides.<repo>`: set `name`, `emoji`, `description`, `url`, or `"hidden": true`
- `coming_soon`: cards for apps that don't have a repo yet

Edits to this file trigger the Action automatically.

## apps.json shape

```json
{ "apps": [ { "repo", "name", "description", "emoji", "url", "source", "status": "live|coming_soon", "created" } ] }
```
