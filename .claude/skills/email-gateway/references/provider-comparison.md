# Email Provider Comparison

Comprehensive comparison of Resend, SendGrid, Mailgun, and SMTP2Go for transactional email.

## Quick Decision Matrix

| Your Needs | Best Provider | Reason |
|------------|---------------|--------|
| React Email, modern DX | **Resend** | Native JSX support, simple API |
| Enterprise scale (1M+/mo) | **SendGrid** | Advanced analytics, A/B testing |
| Developer webhooks, flexibility | **Mailgun** | Detailed events, template engine |
| Simple relay, AU-based | **SMTP2Go** | Reliable, good support |
| Starting out, small app | **Resend** or **SendGrid** | Both have generous free tiers |
| Budget-conscious (<$50/mo) | **Resend** | Best value at scale |

---

## Detailed Comparison

### Pricing (as of 2026)

| Provider | Free Tier | Entry Paid | Scale ($90-100/mo) |
|----------|-----------|------------|-------------------|
| **Resend** | 100/day, 3k/mo | $20 for 50k | $80 for 500k |
| **SendGrid** | 100/day forever | $15 for 10k | $90 for 100k |
| **Mailgun** | 100/day forever | $15 for 10k | $90 for 100k |
| **SMTP2Go** | 1k trial | $10 for 10k | $80 for 100k |

**Best Value**: Resend (500k emails for $80 vs competitors' 100k)

---

### Features

#### Email Composition

| Feature | Resend | SendGrid | Mailgun | SMTP2Go |
|---------|--------|----------|---------|---------|
| HTML Email | ✅ | ✅ | ✅ | ✅ |
| Plain Text | ✅ | ✅ | ✅ | ✅ |
| React Email (JSX) | ✅ Native | ❌ | ❌ | ❌ |
| Dynamic Templates | ✅ | ✅ | ✅ | ✅ |
| Template Builder | Dashboard | Visual editor | Dashboard | Dashboard |
| Template Versioning | ✅ | ✅ | ✅ | Limited |

**Winner**: Resend (React Email is game-changing for developers)

#### Delivery Features

| Feature | Resend | SendGrid | Mailgun | SMTP2Go |
|---------|--------|----------|---------|---------|
| Batch Sending | 50/req | 1000/req | 1000/req | 100/req |
| Scheduled Send | ✅ | ✅ | ✅ | ❌ |
| SMTP Relay | ✅ | ✅ | ✅ | ✅ Primary |
| Dedicated IPs | Enterprise | $90+/mo | $80+/mo | Custom |
| IP Warmup | Managed | Manual | Manual | Managed |
| Custom Domains | ✅ | ✅ | ✅ | ✅ |

**Winner**: SendGrid/Mailgun (better batch capabilities)

#### Analytics & Tracking

| Feature | Resend | SendGrid | Mailgun | SMTP2Go |
|---------|--------|----------|---------|---------|
| Open Tracking | ✅ | ✅ | ✅ | ✅ |
| Click Tracking | ✅ | ✅ | ✅ | ✅ |
| Bounce Handling | ✅ | ✅ | ✅ | ✅ |
| Spam Reports | ✅ | ✅ | ✅ | ✅ |
| Dashboard Analytics | Basic | Advanced | Advanced | Good |
| A/B Testing | ❌ | ✅ | ✅ | ❌ |
| Engagement Insights | Basic | Advanced | Advanced | Basic |

**Winner**: SendGrid (most comprehensive analytics)

#### Developer Experience

| Feature | Resend | SendGrid | Mailgun | SMTP2Go |
|---------|--------|----------|---------|---------|
| API Simplicity | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Documentation | Excellent | Good | Excellent | Good |
| SDKs | 10+ languages | 7 languages | 8 languages | 4 languages |
| Webhooks | ✅ 6 events | ✅ 15+ events | ✅ 12+ events | ✅ 8 events |
| Webhook Verification | ✅ HMAC | ✅ ECDSA | ✅ HMAC | ✅ HMAC |
| API Rate Limits | 10/sec | 600/sec | Varies | 10/sec |

**Winner**: Resend (simplest API) / Mailgun (most detailed webhooks)

#### Support & Reliability

| Feature | Resend | SendGrid | Mailgun | SMTP2Go |
|---------|--------|----------|---------|---------|
| Free Tier Support | Email | Email | Ticket | Email |
| Paid Support | Email/Slack | Chat/Phone | Email/Chat | Email/Phone |
| SLA | 99.9% (paid) | 99.9% (paid) | 99.9% (paid) | 99.9% |
| Status Page | ✅ | ✅ | ✅ | ✅ |
| Region Options | Global | Global | US/EU | AU-focused |

**Winner**: Tie (all have good uptime, SMTP2Go best for AU)

---

## Use Case Recommendations

### Modern SaaS App (React/Next.js)

**Choose: Resend**

Why:
- React Email integration
- Simple API
- Best pricing at scale
- Modern developer experience

Example:
```typescript
await resend.emails.send({
  from: 'app@yourdomain.com',
  to: 'user@example.com',
  subject: 'Welcome!',
  react: WelcomeEmail({ name: 'Alice' }),
});
```

---

### Enterprise Email (1M+/month)

**Choose: SendGrid**

Why:
- Advanced analytics
- A/B testing
- Proven at scale
- Phone support

Example:
```typescript
// Batch 1000 personalized emails
personalizations: users.map(u => ({
  to: [{ email: u.email }],
  dynamic_template_data: { name: u.name },
}))
```

---

### Developer Tools / Webhooks-Heavy

**Choose: Mailgun**

Why:
- Detailed webhook events
- Flexible template variables
- Developer-friendly API
- Good documentation

Example:
```typescript
// Track every email event
events: ['delivered', 'opened', 'clicked', 'failed', 'complained']
```

---

### Simple Transactional (Australia)

**Choose: SMTP2Go**

Why:
- AU-based (low latency)
- Simple, reliable
- Good support
- Affordable

Example:
```typescript
// Just works, no fuss
{
  api_key: env.SMTP2GO_API_KEY,
  to: ['<user@example.com>'],
  sender: 'noreply@yourdomain.com',
  subject: 'Welcome',
  html_body: '<h1>Hello</h1>',
}
```

---

## Migration Considerations

### From SendGrid to Resend

**Why migrate:**
- Lower cost at scale
- Better DX
- React Email support

**Migration path:**
1. Set up Resend account, verify domain
2. Convert dynamic templates to React components or HTML
3. Update API calls (simple structure change)
4. Switch DNS/webhooks
5. Monitor deliverability for 1 week
6. Cancel SendGrid

**Gotchas:**
- Batch size drops from 1000 to 50 per request
- Template syntax changes (handlebars → React)
- Webhook events slightly different

---

### From Mailgun to Resend

**Why migrate:**
- Simpler API
- React Email
- Better pricing

**Migration path:**
1. Verify domain in Resend
2. Convert Mailgun templates to React or HTML
3. Update FormData API calls to JSON
4. Update webhook handlers (different signature verification)
5. Switch DNS
6. Monitor for 1 week

**Gotchas:**
- No more FormData (use JSON body)
- Template variables format changes
- Webhook signature verification method different

---

### From Resend to SendGrid

**Why migrate:**
- Need A/B testing
- Need advanced analytics
- Larger batch sizes

**Migration path:**
1. Set up SendGrid, verify domain
2. Convert React Email to dynamic templates (or render to HTML)
3. Update API calls (more complex structure)
4. Set up webhook handlers
5. Switch DNS
6. Monitor deliverability

**Gotchas:**
- More complex API structure
- Template builder less developer-friendly
- React Email requires pre-rendering

---

## Technical Comparison

### API Request Format

**Resend** (Simple JSON):
```json
{
  "from": "noreply@domain.com",
  "to": "user@example.com",
  "subject": "Welcome",
  "html": "<h1>Hello</h1>"
}
```

**SendGrid** (Nested JSON):
```json
{
  "personalizations": [{
    "to": [{ "email": "user@example.com" }]
  }],
  "from": { "email": "noreply@domain.com" },
  "subject": "Welcome",
  "content": [{
    "type": "text/html",
    "value": "<h1>Hello</h1>"
  }]
}
```

**Mailgun** (FormData):
```
from: noreply@domain.com
to: user@example.com
subject: Welcome
html: <h1>Hello</h1>
```

**SMTP2Go** (JSON with angle brackets):
```json
{
  "api_key": "...",
  "to": ["<user@example.com>"],
  "sender": "noreply@domain.com",
  "subject": "Welcome",
  "html_body": "<h1>Hello</h1>"
}
```

---

### Webhook Event Names

| Event | Resend | SendGrid | Mailgun | SMTP2Go |
|-------|--------|----------|---------|---------|
| Delivered | `email.delivered` | `delivered` | `delivered` | `delivered` |
| Bounced | `email.bounced` | `bounce` | `failed` | `bounce` |
| Spam | `email.complained` | `spamreport` | `complained` | `spam` |
| Opened | `email.opened` | `open` | `opened` | `open` |
| Clicked | `email.clicked` | `click` | `clicked` | `click` |

---

### Rate Limits

| Provider | Requests/sec | Burst | Emails/day (Free) |
|----------|--------------|-------|-------------------|
| Resend | 10 | Yes | 100 |
| SendGrid | 600 | Yes | 100 |
| Mailgun | Varies | Yes | 100 |
| SMTP2Go | 10 | Limited | ~33 (1k/mo trial) |

---

## Summary

**Best Overall**: **Resend** (modern, simple, best value)
**Best for Enterprise**: **SendGrid** (scale, analytics, support)
**Best for Developers**: **Mailgun** (webhooks, flexibility)
**Best for Australia**: **SMTP2Go** (local, reliable)

Choose based on your specific needs and priorities.
