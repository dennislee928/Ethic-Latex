# Bug Fix Message Template

## Format

```
🐛 *Bug Fixed: {PROJECT_NAME}*

*Problem:* {WHAT_WAS_BROKEN}
*Solution:* {HOW_IT_WAS_FIXED}
*Files:* {KEY_FILES_CHANGED}

• Commit: `{COMMIT_HASH}`
{IF_DEPLOYED}• Live at: {URL}

_Please verify if you reported this issue._
```

## Example

```
🐛 *Bug Fixed: Acme Dashboard*

*Problem:* Users getting logged out randomly after 5 minutes
*Solution:* Fixed session refresh logic - was using wrong timestamp format
*Files:* lib/auth/session.ts, middleware.ts

• Commit: `e4f5g6h`
• Live at: https://acme-dashboard.vercel.app

_Please verify if you reported this issue._
```

## When to use

- After fixing a bug someone on the team reported
- After fixing a production issue
- When the fix needs verification from whoever found it

## What to include

- Clear description of what was broken (as user would see it)
- Brief explanation of the fix (not too technical)
- Files changed (helps team know what to review)
- Request for verification
