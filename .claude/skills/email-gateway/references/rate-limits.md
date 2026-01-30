# Rate Limits & Quotas

Comprehensive rate limiting reference for all four email providers.

## Rate Limits by Provider

### Resend

| Tier | Daily Limit | Monthly Limit | API Rate | Burst |
|------|-------------|---------------|----------|-------|
| Free | 100 | 3,000 | 10 req/sec | Yes |
| Paid ($20) | Unlimited | 50,000 | 10 req/sec | Yes |
| Scale ($80) | Unlimited | 500,000 | 50 req/sec | Yes |

**Batch Size**: 50 recipients per request

**Response Headers**:
- `X-RateLimit-Limit`: Maximum requests
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp for reset
- `Retry-After`: Seconds to wait (on 429)

**Burst Handling**: Short bursts above limit are tolerated

**Overage Cost**: $1 per 1,000 emails

---

### SendGrid

| Tier | Daily Limit | Monthly Limit | API Rate | Burst |
|------|-------------|---------------|----------|-------|
| Free | 100 | Forever | 600 req/sec | Yes |
| Basic ($15) | Unlimited | 10,000 | 600 req/sec | Yes |
| Foundation ($35) | Unlimited | 50,000 | 600 req/sec | Yes |
| Scale ($90) | Unlimited | 100,000 | 600 req/sec | Yes |

**Batch Size**: 1,000 recipients per request (via personalizations)

**Response Headers**:
- `X-RateLimit-Limit`: 600
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp

**Burst Handling**: Allows bursts up to 6,000 requests in 10 seconds

**Overage Cost**: $1.80-$1.10 per 1,000 emails (tier-dependent)

---

### Mailgun

| Tier | Daily Limit | Monthly Limit | API Rate | Burst |
|------|-------------|---------------|----------|-------|
| Free | 100 | Forever | Varies | Limited |
| Basic ($15) | Unlimited | 10,000 | 100 req/sec | Yes |
| Foundation ($35) | Unlimited | 50,000 | 300 req/sec | Yes |
| Scale ($90) | Unlimited | 100,000 | 1,000 req/sec | Yes |

**Batch Size**: 1,000 recipients per request

**Response Headers**:
- `X-RateLimit-Limit`: Tier-specific
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp
- `Retry-After`: Seconds to wait (on 429)

**Burst Handling**: Short bursts tolerated on paid plans

**Overage Cost**: $1.30-$1.10 per 1,000 emails (tier-dependent)

---

### SMTP2Go

| Tier | Daily Limit | Monthly Limit | API Rate | Burst |
|------|-------------|---------------|----------|-------|
| Trial | ~33 | 1,000 | 10 req/sec | Limited |
| Basic ($10) | Unlimited | 10,000 | 10 req/sec | Limited |
| Standard ($35) | Unlimited | 50,000 | 10 req/sec | Limited |
| Pro ($80) | Unlimited | 100,000 | 10 req/sec | Limited |

**Batch Size**: 100 recipients per request

**Response Headers**:
- `X-RateLimit-Limit`: 10
- `X-RateLimit-Remaining`: Requests remaining
- `Retry-After`: Seconds to wait (on 429)

**Burst Handling**: Limited burst capacity

**Overage Cost**: Varies by tier (~$1 per 1,000)

---

## Rate Limiting Implementation

### Simple Token Bucket (KV-based)

```typescript
interface RateLimitConfig {
  maxRequests: number;
  windowSeconds: number;
}

async function checkRateLimit(
  key: string,
  config: RateLimitConfig,
  kv: KVNamespace
): Promise<{ allowed: boolean; resetAt?: number }> {
  const now = Date.now();
  const stateKey = `rate-limit:${key}`;
  const stateJson = await kv.get(stateKey);

  if (!stateJson) {
    // First request in window
    const state = {
      count: 1,
      resetAt: now + config.windowSeconds * 1000,
    };
    await kv.put(stateKey, JSON.stringify(state), { expirationTtl: config.windowSeconds });
    return { allowed: true };
  }

  const state = JSON.parse(stateJson);

  if (now > state.resetAt) {
    // Window expired, reset
    const newState = {
      count: 1,
      resetAt: now + config.windowSeconds * 1000,
    };
    await kv.put(stateKey, JSON.stringify(newState), { expirationTtl: config.windowSeconds });
    return { allowed: true };
  }

  if (state.count >= config.maxRequests) {
    // Rate limit exceeded
    return { allowed: false, resetAt: state.resetAt };
  }

  // Increment count
  state.count++;
  await kv.put(stateKey, JSON.stringify(state), { expirationTtl: config.windowSeconds });
  return { allowed: true };
}

// Usage
const limit = await checkRateLimit('user:123', { maxRequests: 10, windowSeconds: 1 }, env.KV);
if (!limit.allowed) {
  return new Response('Rate limit exceeded', {
    status: 429,
    headers: {
      'Retry-After': String(Math.ceil((limit.resetAt! - Date.now()) / 1000)),
    },
  });
}
```

---

### Durable Objects Rate Limiter

```typescript
// rate-limiter.ts
export class RateLimiter {
  private state: DurableObjectState;
  private counts: Map<string, { count: number; resetAt: number }> = new Map();

  constructor(state: DurableObjectState) {
    this.state = state;
  }

  async fetch(request: Request): Promise<Response> {
    const { key, maxRequests, windowMs } = await request.json();

    const now = Date.now();
    const current = this.counts.get(key);

    if (!current || now > current.resetAt) {
      this.counts.set(key, { count: 1, resetAt: now + windowMs });
      return new Response(JSON.stringify({ allowed: true }));
    }

    if (current.count >= maxRequests) {
      return new Response(JSON.stringify({
        allowed: false,
        resetAt: current.resetAt,
      }));
    }

    current.count++;
    this.counts.set(key, current);
    return new Response(JSON.stringify({ allowed: true }));
  }
}

// Usage in Worker
const id = env.RATE_LIMITER.idFromName('email-limits');
const stub = env.RATE_LIMITER.get(id);
const response = await stub.fetch('http://internal/check', {
  method: 'POST',
  body: JSON.stringify({
    key: `user:${userId}`,
    maxRequests: 10,
    windowMs: 1000,
  }),
});

const { allowed, resetAt } = await response.json();
if (!allowed) {
  return new Response('Rate limit exceeded', { status: 429 });
}
```

---

### Per-Provider Rate Limiting

```typescript
const PROVIDER_LIMITS: Record<string, RateLimitConfig> = {
  resend: { maxRequests: 10, windowSeconds: 1 },
  sendgrid: { maxRequests: 600, windowSeconds: 1 },
  mailgun: { maxRequests: 100, windowSeconds: 1 },
  smtp2go: { maxRequests: 10, windowSeconds: 1 },
};

async function sendEmailRateLimited(
  provider: 'resend' | 'sendgrid' | 'mailgun' | 'smtp2go',
  email: any,
  env: Env
) {
  const limit = await checkRateLimit(
    `provider:${provider}`,
    PROVIDER_LIMITS[provider],
    env.KV
  );

  if (!limit.allowed) {
    const waitMs = limit.resetAt! - Date.now();
    await new Promise(resolve => setTimeout(resolve, waitMs));
  }

  return sendEmail(provider, email, env);
}
```

---

## Quota Management

### Track Usage

```typescript
// Increment quota on each send
async function trackEmailSent(userId: string, env: Env) {
  const month = new Date().toISOString().slice(0, 7); // YYYY-MM
  const key = `quota:${userId}:${month}`;

  const current = await env.KV.get(key);
  const count = current ? parseInt(current) + 1 : 1;

  await env.KV.put(key, String(count), {
    expirationTtl: 60 * 60 * 24 * 32, // 32 days
  });

  return count;
}

// Check quota before sending
async function checkQuota(userId: string, plan: 'free' | 'pro', env: Env) {
  const limits = { free: 1000, pro: 50000 };
  const month = new Date().toISOString().slice(0, 7);
  const key = `quota:${userId}:${month}`;

  const current = await env.KV.get(key);
  const count = current ? parseInt(current) : 0;

  return {
    used: count,
    limit: limits[plan],
    remaining: limits[plan] - count,
    exceeded: count >= limits[plan],
  };
}
```

---

### Quota Exceeded Response

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const userId = getUserId(request);
    const plan = await getUserPlan(userId, env);

    const quota = await checkQuota(userId, plan, env);
    if (quota.exceeded) {
      return new Response(JSON.stringify({
        error: 'Monthly quota exceeded',
        used: quota.used,
        limit: quota.limit,
        resetDate: getNextMonth(),
      }), {
        status: 429,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    await sendEmail(request, env);
    await trackEmailSent(userId, env);

    return new Response(JSON.stringify({ success: true }));
  },
};
```

---

## Burst Handling

### Cloudflare Queues for Burst Absorption

```typescript
// Producer (API endpoint)
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const email = await request.json();

    // Queue email instead of sending immediately
    await env.EMAIL_QUEUE.send(email);

    return new Response(JSON.stringify({ queued: true }));
  },
};

// Consumer (rate-limited sender)
export default {
  async queue(batch: MessageBatch<any>, env: Env): Promise<void> {
    for (const message of batch.messages) {
      const email = message.body;

      // Rate-limited send
      const limit = await checkRateLimit('provider:resend', { maxRequests: 10, windowSeconds: 1 }, env.KV);
      if (!limit.allowed) {
        const waitMs = limit.resetAt! - Date.now();
        await new Promise(resolve => setTimeout(resolve, waitMs));
      }

      await sendEmail(email, env);
      message.ack();
    }
  },
};
```

---

## Multi-Provider Failover

Route to different providers based on quota/rate limits:

```typescript
async function sendWithFailover(email: any, env: Env) {
  const providers: Array<'resend' | 'sendgrid' | 'mailgun' | 'smtp2go'> = [
    'resend',
    'sendgrid',
    'mailgun',
    'smtp2go',
  ];

  for (const provider of providers) {
    const limit = await checkRateLimit(
      `provider:${provider}`,
      PROVIDER_LIMITS[provider],
      env.KV
    );

    if (limit.allowed) {
      try {
        return await sendEmail(provider, email, env);
      } catch (error) {
        console.error(`${provider} failed:`, error);
        continue;
      }
    }
  }

  throw new Error('All providers rate limited or failed');
}
```

---

## Monitoring & Alerts

### Track Rate Limit Hits

```typescript
async function logRateLimitHit(provider: string, env: Env) {
  await env.DB.prepare(`
    INSERT INTO rate_limit_hits (provider, timestamp)
    VALUES (?, ?)
  `).bind(provider, Date.now()).run();
}

// Alert if rate limit hits exceed threshold
const hits = await env.DB.prepare(`
  SELECT COUNT(*) as count FROM rate_limit_hits
  WHERE provider = ? AND timestamp > ?
`).bind(provider, Date.now() - 60000).first(); // Last minute

if (hits.count > 10) {
  await sendSlackAlert({
    text: `⚠️ ${provider} rate limit hit ${hits.count} times in last minute`,
  });
}
```

---

## Best Practices

1. **Use Queues**: Absorb bursts with Cloudflare Queues
2. **Implement Backoff**: Exponential backoff on 429 responses
3. **Track Quotas**: Monitor usage vs limits
4. **Multi-Provider**: Failover to alternate providers
5. **Alert Early**: Notify when approaching limits
6. **Batch When Possible**: Use provider batch capabilities
7. **Respect Retry-After**: Honor provider retry headers

---

## Summary

| Provider | Best For | Rate Limit | Batch Size |
|----------|----------|------------|------------|
| Resend | Low-volume, bursts ok | 10/sec | 50 |
| SendGrid | High-volume enterprise | 600/sec | 1,000 |
| Mailgun | Medium-volume flexible | 100/sec | 1,000 |
| SMTP2Go | Low-volume reliable | 10/sec | 100 |

Choose based on your sending patterns and volume requirements.
