# Announcements playground

Test caller for the reusable
[announcements workflow](https://github.com/svrnm/shared-workflows/tree/feat/announcement-workflow/announcements)
in `shared-workflows`. Every destination configured here is a test account.
Nothing here posts to real OpenTelemetry channels.

This repository is public on purpose. It shows exactly what a public caller,
such as `opentelemetry.io`, exposes in its logs, job summaries, and artifacts.

## Blog flow

The playground is a minimal Hugo site with the same content layout as
`opentelemetry.io` (`content/en/blog/YYYY/slug/index.md` served at
`/blog/YYYY/slug/`), deployed by Netlify (`netlify.toml`).

A post opts in to being announced with an `announcement` block in its front
matter. The blurb is the only announcement-specific text; the title comes from
the post and the URL from its path:

```yaml
---
title: Testing blog announcements
date: 2026-10-13
announcement:
  text: >-
    A short blurb that goes to every channel, followed by the link.
---
```

- **Check blog announcements** (`check-blog.yml`): on pull requests, validates
  the block of new or changed posts and the length limit of every channel
  (Bluesky allows 300 characters including the URL). The job summary shows
  what each channel would receive. No secrets, nothing is sent.
- **Announce blog posts** (`announce-blog.yml`): on push to `main`, announces
  newly added posts that have the block. The shared workflow waits until the
  post's URL returns 200 (up to `ANNOUNCEMENT_WAIT_MINUTES`, default 30), then
  asks for approval and delivers. Edited, renamed, or draft posts are not
  announced. `workflow_dispatch` repeats a single post.

The front matter is read by `.github/scripts/blog_announcements.py` with `yq`,
which GitHub-hosted runners provide.

## Workflows with JSON files

- **Announce manually** (`announce-manual.yml`): `workflow_dispatch` with a
  file, optional channel list, and mode (default `check`).
- **Announce new files** (`announce-files.yml`): runs for files newly added to
  `.announcements/` on `main`. It uses the mode in the
  `ANNOUNCEMENT_AUTO_MODE` variable and falls back to `check`.

All workflows refuse `publish`: the playground only creates drafts. In
`draft` mode, Buffer and Groups.io create native drafts and Slack is only
previewed in the job summary.

Both call the workflow at `@feat/announcement-workflow` so changes on the
branch can be tested without re-pinning.

## Configuration

Environment `announcements`: a required reviewer, and the secrets for each
service as its test account becomes available.

| Variable | Example |
| -------- | ------- |
| `ANNOUNCEMENT_CHANNELS` | `["slack","groupsio"]` |
| `ANNOUNCEMENT_TARGETS` | `{"slack":["C0123456789"],"groupsio":[12345]}` |
| `ANNOUNCEMENT_AUTO_MODE` | `draft` (unset means `check`) |
| `SITE_URL` | `https://example.netlify.app` (the Netlify site address) |
| `ANNOUNCEMENT_WAIT_MINUTES` | `30` (unset means 30, at most 120) |

## Test destinations

| Service | Destination | Status |
| ------- | ----------- | ------ |
| Netlify | https://announcements-playground.netlify.app | Set up |
| Slack | Private test channel in CNCF Slack via Workflow Builder webhook | Set up |
| Groups.io | `severin-test-group@groups.io` | Set up |
| Buffer: Bluesky | Test account | Not set up |
| Buffer: Mastodon | Test account | Not set up |
| Buffer: LinkedIn | Test Page (draft only) | Not set up |
