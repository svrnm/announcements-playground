# Announcements playground

Test caller for the reusable
[announcements workflow](https://github.com/svrnm/shared-workflows/tree/feat/announcement-workflow/announcements)
in `shared-workflows`. Every destination configured here is a test account.
Nothing here posts to real OpenTelemetry channels.

This repository is public on purpose. It shows exactly what a public caller,
such as `opentelemetry.io`, exposes in its logs, job summaries, and artifacts.

## Workflows

- **Announce manually** (`announce-manual.yml`): `workflow_dispatch` with a
  file, optional channel list, and mode (default `dry-run`).
- **Announce new files** (`announce-files.yml`): runs for files newly added to
  `.announcements/` on `main`. It uses the mode in the
  `ANNOUNCEMENT_AUTO_MODE` variable and falls back to `dry-run`.

Both workflows refuse `publish` when a Buffer channel (`linkedin`, `bluesky`,
`mastodon`) is selected. Buffer stays drafts-only until its draft behavior is
verified, and the queues of the test channels are paused as a second safeguard.

Both call the workflow at `@feat/announcement-workflow` so changes on the
branch can be tested without re-pinning.

## Configuration

Environment `announcements`: a required reviewer, and the secrets for each
service as its test account becomes available.

| Variable | Example |
| -------- | ------- |
| `ANNOUNCEMENT_CHANNELS` | `["slack","groupsio"]` |
| `ANNOUNCEMENT_TARGETS` | `{"slack":["C0123456789"],"groupsio":[12345]}` |
| `ANNOUNCEMENT_AUTO_MODE` | `draft` (unset means `dry-run`) |
| `REDDIT_USER_AGENT` | `github-actions:otel-announcements-test:0.1 (by /u/YOUR_TEST_BOT)` |

## Test destinations

| Service | Destination | Status |
| ------- | ----------- | ------ |
| Slack | Test channel in CNCF Slack via incoming webhook | Not set up |
| Groups.io | Moderated test group on groups.io | Not set up |
| Buffer: Bluesky | Test account | Not set up |
| Buffer: Mastodon | Test account | Not set up |
| Buffer: LinkedIn | Test Page (draft only) | Not set up |
| Reddit | Private test subreddit | Not set up (API approval needed) |
