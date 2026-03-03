# Webhook Events Reference

Complete guide to webhook events for all four email providers.

## Event Types by Provider

### Resend Webhook Events

| Event | Trigger | Typical Action |
|-------|---------|----------------|
| `email.sent` | Email accepted by Resend | Log timestamp |
| `email.delivered` | Email delivered to recipient | Update delivery status |
| `email.delivery_delayed` | Temporary delivery issue | Alert if >1 hour |
| `email.bounced` | Permanent delivery failure | Mark email invalid |
| `email.complained` | Spam complaint | Unsubscribe immediately |
| `email.opened` | Recipient opened email | Track engagement |
| `email.clicked` | Recipient clicked link | Track conversion |

**Signature Verification**: HMAC SHA-256 (Svix format)

Headers:
- `svix-id`: Message ID
- `svix-timestamp`: Unix timestamp
- `svix-signature`: HMAC signature

Example payload:
```json
{
  "type": "email.delivered",
  "created_at": "2026-01-10T12:00:00Z",
  "data": {
    "email_id": "49a3999c-0ce1-4ea6-ab68-afcd6dc2e794",
    "from": "noreply@yourdomain.com",
    "to": ["user@example.com"],
    "subject": "Welcome!",
    "created_at": "2026-01-10T11:59:00Z"
  }
}
```

---

### SendGrid Webhook Events

| Event | Trigger | Typical Action |
|-------|---------|----------------|
| `processed` | Email processed by SendGrid | Log initial processing |
| `dropped` | Email dropped (invalid, duplicate) | Alert, investigate |
| `delivered` | Email delivered successfully | Update status |
| `bounce` | Hard/soft bounce | Mark email invalid if hard |
| `deferred` | Temporary delivery delay | Monitor |
| `open` | Email opened (tracking pixel) | Track engagement |
| `click` | Link clicked | Track conversion |
| `spamreport` | Marked as spam | Unsubscribe, review content |
| `unsubscribe` | Unsubscribe link clicked | Unsubscribe user |
| `group_unsubscribe` | Unsubscribed from group | Update preferences |
| `group_resubscribe` | Resubscribed to group | Update preferences |

**Signature Verification**: ECDSA with public key

Headers:
- `X-Twilio-Email-Event-Webhook-Signature`: Base64 encoded signature
- `X-Twilio-Email-Event-Webhook-Timestamp`: Unix timestamp

Example payload (array of events):
```json
[
  {
    "email": "user@example.com",
    "timestamp": 1736508000,
    "smtp-id": "<20260110120000.5817@sendgrid.net>",
    "event": "delivered",
    "category": ["welcome"],
    "sg_event_id": "abc123...",
    "sg_message_id": "def456..."
  }
]
```

---

### Mailgun Webhook Events

| Event | Trigger | Typical Action |
|-------|---------|----------------|
| `accepted` | Email accepted by Mailgun | Log acceptance |
| `rejected` | Email rejected (invalid) | Alert, fix sender config |
| `delivered` | Email delivered successfully | Update status |
| `failed` | Permanent/temporary failure | Mark invalid if permanent |
| `opened` | Email opened | Track engagement |
| `clicked` | Link clicked | Track conversion |
| `unsubscribed` | Unsubscribe link clicked | Unsubscribe user |
| `complained` | Spam complaint | Unsubscribe immediately |
| `stored` | Email stored (for retrieval) | Optional archival |

**Signature Verification**: HMAC SHA-256

Fields in payload:
- `signature.timestamp`: Unix timestamp
- `signature.token`: Random token
- `signature.signature`: HMAC hash

Example payload:
```json
{
  "signature": {
    "timestamp": "1736508000",
    "token": "abc123...",
    "signature": "def456..."
  },
  "event-data": {
    "event": "delivered",
    "timestamp": 1736508000.123,
    "id": "xyz789...",
    "recipient": "user@example.com",
    "message": {
      "headers": {
        "message-id": "<20260110120000@mg.yourdomain.com>",
        "from": "noreply@yourdomain.com",
        "to": "user@example.com",
        "subject": "Welcome!"
      }
    },
    "tags": ["welcome"],
    "user-variables": {
      "user_id": "12345"
    }
  }
}
```

---

### SMTP2Go Webhook Events

| Event | Trigger | Typical Action |
|-------|---------|----------------|
| `delivered` | Email delivered successfully | Update status |
| `bounce` | Hard/soft bounce | Mark email invalid if hard |
| `spam` | Spam complaint | Unsubscribe immediately |
| `open` | Email opened | Track engagement |
| `click` | Link clicked | Track conversion |
| `unsubscribe` | Unsubscribe link clicked | Unsubscribe user |
| `suppress` | Email suppressed (blocklist) | Alert, investigate |
| `error` | Send error | Alert, investigate |

**Signature Verification**: HMAC SHA-256

Headers:
- `X-Smtp2go-Signature`: Hex-encoded HMAC signature

Example payload:
```json
{
  "event": "delivered",
  "email_id": "abc123...",
  "email": "user@example.com",
  "timestamp": 1736508000,
  "subject": "Welcome!",
  "message_id": "<def456@smtp2go.com>"
}
```

---

## Webhook Security

### Resend Signature Verification

```typescript
import { createHmac } from 'crypto';

function verifyResendWebhook(
  request: Request,
  secret: string
): boolean {
  const signature = request.headers.get('svix-signature');
  const timestamp = request.headers.get('svix-timestamp');
  const body = await request.text();

  if (!signature || !timestamp) return false;

  const signedContent = `${timestamp}.${body}`;
  const expectedSignature = createHmac('sha256', secret)
    .update(signedContent)
    .digest('base64');

  return signature.includes(expectedSignature);
}
```

---

### SendGrid Signature Verification

```typescript
import { EventWebhook, EventWebhookHeader } from '@sendgrid/eventwebhook';

function verifySendGridWebhook(
  request: Request,
  publicKey: string
): boolean {
  const signature = request.headers.get(EventWebhookHeader.SIGNATURE());
  const timestamp = request.headers.get(EventWebhookHeader.TIMESTAMP());
  const body = await request.text();

  const eventWebhook = new EventWebhook();
  const ecPublicKey = eventWebhook.convertPublicKeyToECDSA(publicKey);

  return eventWebhook.verifySignature(
    ecPublicKey,
    body,
    signature!,
    timestamp!
  );
}
```

---

### Mailgun Signature Verification

```typescript
import { createHmac } from 'crypto';

function verifyMailgunWebhook(
  timestamp: string,
  token: string,
  signature: string,
  signingKey: string
): boolean {
  const encoded = createHmac('sha256', signingKey)
    .update(`${timestamp}${token}`)
    .digest('hex');

  return encoded === signature;
}
```

---

### SMTP2Go Signature Verification

```typescript
import { createHmac } from 'crypto';

function verifySMTP2GoWebhook(
  body: string,
  signature: string,
  secret: string
): boolean {
  const expectedSignature = createHmac('sha256', secret)
    .update(body)
    .digest('hex');

  return expectedSignature === signature;
}
```

---

## Common Webhook Patterns

### Handle Bounces

```typescript
async function handleBounce(email: string, severity: 'permanent' | 'temporary') {
  if (severity === 'permanent') {
    // Hard bounce - mark email as invalid
    await db.prepare(`
      UPDATE users SET email_valid = 0 WHERE email = ?
    `).bind(email).run();

    console.log(`Marked email as invalid: ${email}`);
  } else {
    // Soft bounce - track but don't invalidate yet
    await db.prepare(`
      INSERT INTO email_bounces (email, severity, bounced_at)
      VALUES (?, ?, ?)
    `).bind(email, severity, Date.now()).run();

    console.log(`Soft bounce tracked: ${email}`);
  }
}
```

---

### Handle Spam Complaints

```typescript
async function handleSpamComplaint(email: string) {
  // Immediately unsubscribe
  await db.prepare(`
    UPDATE users SET subscribed = 0, spam_complained = 1 WHERE email = ?
  `).bind(email).run();

  // Alert team
  await sendSlackAlert({
    channel: '#email-alerts',
    text: `⚠️ Spam complaint from ${email}`,
  });

  console.log(`Unsubscribed due to spam complaint: ${email}`);
}
```

---

### Track Engagement

```typescript
async function trackEmailOpen(email: string, messageId: string) {
  await db.prepare(`
    INSERT INTO email_opens (email, message_id, opened_at)
    VALUES (?, ?, ?)
  `).bind(email, messageId, Date.now()).run();

  console.log(`Email opened: ${email}`);
}

async function trackEmailClick(email: string, messageId: string, url: string) {
  await db.prepare(`
    INSERT INTO email_clicks (email, message_id, url, clicked_at)
    VALUES (?, ?, ?, ?)
  `).bind(email, messageId, url, Date.now()).run();

  console.log(`Link clicked: ${email} -> ${url}`);
}
```

---

## Webhook Testing

### Test Webhook Locally (ngrok)

```bash
# Install ngrok
brew install ngrok

# Start your Worker locally
npm run dev

# Create tunnel
ngrok http 8787

# Use ngrok URL in provider webhook settings
https://abc123.ngrok.io/webhook
```

---

### Test Webhook Signature Verification

```typescript
// Test Resend webhook
const testPayload = {
  type: 'email.delivered',
  data: { email_id: 'test-123' },
};

const secret = 'whsec_test...';
const timestamp = String(Date.now());
const body = JSON.stringify(testPayload);
const signature = createHmac('sha256', secret)
  .update(`${timestamp}.${body}`)
  .digest('base64');

console.log('Signature:', signature);
console.log('Use this in X-Svix-Signature header');
```

---

## Webhook Best Practices

### 1. Return 200 Quickly

Process webhooks asynchronously:

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Verify signature first
    const isValid = await verifyWebhook(request, env.WEBHOOK_SECRET);
    if (!isValid) {
      return new Response('Invalid signature', { status: 401 });
    }

    // Parse event
    const event = await request.json();

    // Queue processing (don't block response)
    env.ctx.waitUntil(processWebhook(event, env));

    // Return 200 immediately
    return new Response('OK', { status: 200 });
  },
};

async function processWebhook(event: any, env: Env) {
  // Handle event logic here
  // Runs after response is sent
}
```

---

### 2. Implement Idempotency

Track processed events to avoid duplicates:

```typescript
async function processWebhook(event: any, env: Env) {
  const eventId = event.id || event.event_id || event.sg_event_id;

  // Check if already processed
  const existing = await env.DB.prepare(`
    SELECT id FROM processed_events WHERE event_id = ?
  `).bind(eventId).first();

  if (existing) {
    console.log(`Event already processed: ${eventId}`);
    return;
  }

  // Process event
  await handleEvent(event, env);

  // Mark as processed
  await env.DB.prepare(`
    INSERT INTO processed_events (event_id, processed_at)
    VALUES (?, ?)
  `).bind(eventId, Date.now()).run();
}
```

---

### 3. Handle Retries Gracefully

Providers retry failed webhooks:

- **Resend**: Exponential backoff, up to 3 days
- **SendGrid**: Up to 3 retries over 10 hours
- **Mailgun**: Exponential backoff, up to 8 hours
- **SMTP2Go**: Up to 5 retries over 24 hours

Ensure your handler is idempotent (see above).

---

### 4. Monitor Webhook Health

Track webhook processing metrics:

```typescript
await env.DB.prepare(`
  INSERT INTO webhook_metrics (provider, event_type, success, duration_ms)
  VALUES (?, ?, ?, ?)
`).bind(provider, event.type, success, duration).run();
```

Alert on:
- High failure rates
- Signature verification failures
- Slow processing times

---

## Summary

- **Verify signatures** for all webhooks
- **Return 200 quickly** (use waitUntil for processing)
- **Implement idempotency** to handle retries
- **Track metrics** for health monitoring
- **Handle spam complaints** immediately
- **Mark permanent bounces** as invalid
