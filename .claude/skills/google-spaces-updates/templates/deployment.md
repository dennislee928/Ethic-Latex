# Deployment Message Template

## Format

```
🚀 *Deployed: {PROJECT_NAME}*

{SUMMARY - what was deployed, 1-2 sentences}

• Branch: `{BRANCH}`
• Commit: `{COMMIT_HASH}`
{IF_PREVIEW_URL}• Preview: {PREVIEW_URL}
{IF_PRODUCTION_URL}• Production: {PRODUCTION_URL}

_Posted by {USER} via Claude Code_
```

## Example

```
🚀 *Deployed: Acme Dashboard*

User authentication flow with OAuth support. Added login, logout, and session management.

• Branch: `feature/auth`
• Commit: `a1b2c3d`
• Preview: https://acme-dashboard-preview.vercel.app
• Production: https://acme-dashboard.vercel.app

_Posted by Alex via Claude Code_
```

## When to use

- After `vercel deploy` or `git push` to production
- After merging PR to main
- When staging/preview is ready for review

## What to include

- Brief summary of what changed
- Branch and commit for traceability
- URLs so team can verify
- Keep it concise - details are in the code
