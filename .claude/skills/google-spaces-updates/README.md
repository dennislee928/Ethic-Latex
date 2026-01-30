# Google Spaces Updates

Post team updates to Google Chat Spaces via webhook.

## Auto-trigger keywords

- "post to team", "notify team", "update the team"
- "tell Deepinder", "tell Joshua", "tell Raquel"
- "google spaces", "team chat"
- After deployments, major features, or when asking questions

## What this skill does

1. Reads project config from `.claude/settings.json`
2. Formats messages based on update type
3. Posts to Google Spaces webhook with rich formatting
4. Includes relevant context (commits, URLs, files changed)

## Commands

| Command | Purpose |
|---------|---------|
| `/google-spaces-updates setup` | Create settings.json for current project |
| `/google-spaces-updates deployment` | Post deployment notification |
| `/google-spaces-updates bugfix` | Post bug fix notification |
| `/google-spaces-updates feature` | Post feature completion |
| `/google-spaces-updates question` | Ask team a question |
| `/google-spaces-updates custom "message"` | Post custom message |

## When NOT to use

- Minor refactors, typo fixes
- WIP commits that aren't ready for review
- Internal debugging/testing
- Anything that would just be noise

## Prerequisites

Project must have `.claude/settings.json` with:
```json
{
  "project": { "name": "...", "repo": "..." },
  "team": { "chat_webhook": "https://chat.googleapis.com/v1/spaces/..." }
}
```

Run `/google-spaces-updates setup` to create this file interactively.

## Testing

For developing new formats or debugging, use the test space webhook in `test-config.json` instead of posting to real team spaces.
