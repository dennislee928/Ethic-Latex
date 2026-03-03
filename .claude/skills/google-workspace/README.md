# Google Workspace APIs

**Status**: Production Ready
**Last Updated**: 2026-01-03

## Auto-Trigger Keywords

### General
- google workspace, google workspace api, google apis
- google oauth, google service account, domain-wide delegation
- google api rate limit, google quota exceeded, 429 error

### Gmail
- gmail api, gmail integration, email automation
- gmail labels, gmail threads, gmail attachments
- gmail mcp, gmail push notifications

### Calendar
- google calendar, calendar api, calendar events
- recurring events, free busy, calendar sharing
- calendar mcp, event scheduling

### Drive
- google drive, drive api, file upload
- drive permissions, drive sharing, file search
- drive mcp, file storage

### Sheets
- google sheets, sheets api, spreadsheet
- a1 notation, sheets batch update, cell formatting
- sheets mcp, spreadsheet automation

### Docs
- google docs, docs api, document generation
- docs mcp, document automation

### Chat
- google chat, google chat api, google spaces
- chat bot, chat webhooks, cards v2
- chat mcp, interactive cards, chat forms

### Meet
- google meet, meet api, video conferencing
- meet mcp, meeting scheduling

### Forms
- google forms, forms api, form responses
- forms mcp, survey automation

### Tasks
- google tasks, tasks api, task management
- tasks mcp, todo automation

### Admin
- google admin, admin sdk, user management
- group management, domain admin
- admin mcp, workspace admin

## What This Skill Does

Comprehensive guide for building integrations with all Google Workspace APIs. Covers OAuth 2.0, service accounts, rate limits, batch operations, and Cloudflare Workers patterns.

## Core Capabilities

**Shared Patterns:**
- OAuth 2.0 with refresh tokens
- Service account authentication
- Domain-wide delegation
- Rate limit handling with exponential backoff
- Batch request patterns

**APIs Covered:**
- Gmail, Calendar, Drive, Sheets, Docs
- Chat, Meet, Forms, Tasks
- Admin SDK, People API

## Quick Start

```bash
# No npm packages required - use fetch API directly
# Just need jose for service account JWT signing
npm install jose
```

See [SKILL.md](SKILL.md) for complete documentation.

## Token Savings

- **Manual research**: ~15k tokens per API
- **With Skill**: ~3k tokens (shared patterns) + ~2k per API
- **Savings**: ~60-70%

## Production Tested

Built from real MCP server implementations for Google Workspace APIs.
