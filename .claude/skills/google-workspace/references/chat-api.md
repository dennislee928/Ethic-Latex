# Google Chat API Reference

**Last Updated**: 2026-01-03
**API Version**: v1 (stable)
**Cards**: v2 (v1 deprecated)

---

## Overview

Google Chat API enables building bots, webhooks, and integrations for Google Chat spaces.

**Two Integration Types:**
1. **Incoming Webhooks** - Send notifications (one-way, no auth needed)
2. **HTTP Endpoint Bots** - Interactive bots with Cards v2 (requires auth)

---

## Scopes

| Scope | Access |
|-------|--------|
| `chat.bot` | Bot-level access (default for bots) |
| `chat.spaces.readonly` | List/get spaces |
| `chat.spaces` | Create/update spaces |
| `chat.spaces.create` | Create spaces only |
| `chat.memberships.readonly` | List/get members |
| `chat.memberships` | Add/remove members |
| `chat.messages.readonly` | Read messages |
| `chat.messages` | Send/update messages |
| `chat.messages.reactions` | Add/remove reactions |

---

## Webhooks (Notifications Only)

No authentication required - just POST to webhook URL.

```typescript
async function sendNotification(webhookUrl: string, message: string) {
  await fetch(webhookUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: message,
      cardsV2: [{
        cardId: `notif-${Date.now()}`,
        card: {
          header: { title: "Alert" },
          sections: [{
            widgets: [{
              textParagraph: { text: message }
            }]
          }]
        }
      }]
    })
  })
}
```

---

## Interactive Bot Handler

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const event = await request.json()

    switch (event.type) {
      case 'ADDED_TO_SPACE':
        return Response.json({ text: "Thanks for adding me!" })

      case 'MESSAGE':
        return handleMessage(event)

      case 'CARD_CLICKED':
        return handleCardClick(event)

      case 'REMOVED_FROM_SPACE':
        return new Response('OK')

      default:
        return Response.json({ text: "Unknown event" })
    }
  }
}
```

---

## Cards v2 Structure

```typescript
const card = {
  cardsV2: [{
    cardId: "unique-id",
    card: {
      header: {
        title: "Card Title",
        subtitle: "Optional subtitle",
        imageUrl: "https://..."
      },
      sections: [{
        header: "Section 1",
        widgets: [
          { textParagraph: { text: "Some text" } },
          { buttonList: { buttons: [...] } }
        ]
      }]
    }
  }]
}
```

**Widget Types:**
- `textParagraph` - Text content (supports Markdown and HTML)
- `buttonList` - Buttons (text or icon)
- `textInput` - Text input field
- `selectionInput` - Dropdowns, checkboxes, switches
- `dateTimePicker` - Date/time selection
- `divider` - Horizontal line
- `image` - Images
- `decoratedText` - Text with icon/button

**Limits:**
- Max 100 widgets per card (silently truncated)
- cardId must be unique

---

## Text Formatting

Cards v2 supports both Markdown and HTML:

```typescript
// Markdown (recommended for AI agents)
{ textParagraph: { text: "**bold** and *italic*\n\n- List item\n- Another" } }

// HTML
{ textParagraph: { text: "<b>bold</b> and <font color='#ea9999'>colored</font>" } }
```

**Markdown Support:**
- `**bold**`, `*italic*`
- `` `code` ``, ` ```code block``` `
- `- list item`, `1. ordered`
- `~strikethrough~`

---

## Spaces API

### List Spaces

```typescript
async function listSpaces(accessToken: string) {
  const response = await fetch(
    'https://chat.googleapis.com/v1/spaces?pageSize=100',
    { headers: { Authorization: `Bearer ${accessToken}` } }
  )
  return response.json()  // { spaces: [...], nextPageToken }
}
```

### Create Space

```typescript
async function createSpace(accessToken: string, displayName: string) {
  const response = await fetch('https://chat.googleapis.com/v1/spaces', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      spaceType: 'SPACE',  // or 'GROUP_CHAT', 'DIRECT_MESSAGE'
      displayName,
      spaceDetails: { description: 'Created via API' }
    })
  })
  return response.json()
}
```

### Search Spaces

```typescript
const params = new URLSearchParams({
  query: 'displayName:Project AND spaceType:SPACE',
  pageSize: '50'
})
const response = await fetch(
  `https://chat.googleapis.com/v1/spaces:search?${params}`,
  { headers: { Authorization: `Bearer ${accessToken}` } }
)
```

---

## Members API

### Add Member

```typescript
async function addMember(accessToken: string, spaceName: string, userEmail: string) {
  const response = await fetch(
    `https://chat.googleapis.com/v1/${spaceName}/members`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        member: { name: `users/${userEmail}`, type: 'HUMAN' },
        role: 'ROLE_MEMBER'  // or 'ROLE_MANAGER'
      })
    }
  )
  return response.json()
}
```

### List Members

```typescript
const response = await fetch(
  `https://chat.googleapis.com/v1/${spaceName}/members?pageSize=100`,
  { headers: { Authorization: `Bearer ${accessToken}` } }
)
// Returns: { memberships: [...], nextPageToken }
```

---

## Reactions API

### Add Reaction

```typescript
async function addReaction(accessToken: string, messageName: string, emoji: string) {
  const response = await fetch(
    `https://chat.googleapis.com/v1/${messageName}/reactions`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        emoji: { unicode: emoji }  // e.g., '👍'
      })
    }
  )
  return response.json()
}
```

---

## Rate Limits

| Operation | Per-Project | Per-Space |
|-----------|-------------|-----------|
| Read operations | 3,000/min | 15/sec |
| Message writes | 600/min | 1/sec |
| Membership writes | 300/min | - |
| Space writes | 60/min | - |
| Reactions | 600/min | - |

---

## Bearer Token Verification

For HTTP endpoint bots, verify the bearer token:

```typescript
async function verifyBearerToken(token: string): Promise<boolean> {
  // Verify token is from chat@system.gserviceaccount.com
  // See full implementation in templates/bearer-token-verify.ts
  const response = await fetch(
    `https://oauth2.googleapis.com/tokeninfo?access_token=${token}`
  )
  const info = await response.json()
  return info.email === 'chat@system.gserviceaccount.com'
}
```

---

## Dialogs (Modals)

```typescript
function openDialog() {
  return {
    actionResponse: {
      type: "DIALOG",
      dialogAction: {
        dialog: {
          body: {
            sections: [{
              header: "Confirm Action",
              widgets: [
                { textParagraph: { text: "Are you sure?" } },
                {
                  buttonList: {
                    buttons: [
                      { text: "Confirm", onClick: { action: { function: "confirm" } } },
                      { text: "Cancel", onClick: { action: { function: "cancel" } } }
                    ]
                  }
                }
              ]
            }]
          }
        }
      }
    }
  }
}
```

---

## Form Validation Errors

Return correct format for validation errors:

```typescript
return Response.json({
  actionResponse: {
    type: "DIALOG",
    dialogAction: {
      actionStatus: {
        statusCode: "INVALID_ARGUMENT",
        userFacingMessage: "Email is required"
      }
    }
  }
})
```

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid/missing bearer token | Verify token correctly |
| 400 Invalid JSON | Wrong card schema | Check field names, nesting |
| Widgets don't render | Exceeded 100 widget limit | Split into multiple cards |
| "Unable to connect" | URL not accessible, timeout | Check worker is deployed, responds fast |
| 429 Rate limited | Quota exceeded | Implement exponential backoff |

---

## Official Docs

- **Chat API**: https://developers.google.com/workspace/chat
- **Cards v2 Reference**: https://developers.google.com/workspace/chat/api/reference/rest/v1/cards
- **Webhooks Guide**: https://developers.google.com/workspace/chat/quickstart/webhooks
