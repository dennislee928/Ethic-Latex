# Feature Complete Message Template

## Format

```
✨ *Feature Complete: {PROJECT_NAME}*

*{FEATURE_NAME}*

{DESCRIPTION - what it does, how to use it, 2-3 sentences}

{IF_DEMO_URL}• Demo: {DEMO_URL}
• Files: {KEY_FILES}

_Ready for review/testing._
```

## Example

```
✨ *Feature Complete: Acme Dashboard*

*Export to CSV*

Users can now export their data to CSV from any table view. Click the download icon in the top-right corner, select date range, and choose which columns to include. Works with up to 10,000 rows.

• Demo: https://acme-dashboard.vercel.app/reports
• Files: components/export/, lib/csv-generator.ts

_Ready for review/testing._
```

## When to use

- After completing a feature that's ready for others to see/use
- When something is ready for QA or client review
- After implementing something the team discussed

## What to include

- Feature name (clear, not technical)
- What it does and how to use it (user perspective)
- Demo link if available
- Note that it's ready for review
