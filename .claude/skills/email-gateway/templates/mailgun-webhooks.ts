/**
 * Mailgun Webhook Handler
 *
 * Handle Mailgun webhook events (delivered, bounced, complained, opened, clicked).
 * Requires MAILGUN_WEBHOOK_SIGNING_KEY environment variable.
 */

import { createHmac } from 'crypto';

interface Env {
  MAILGUN_WEBHOOK_SIGNING_KEY: string;
  // Optional: Database binding for storing events
  DB?: D1Database;
}

interface MailgunWebhook {
  signature: {
    timestamp: string;
    token: string;
    signature: string;
  };
  'event-data': {
    event: 'delivered' | 'failed' | 'opened' | 'clicked' | 'unsubscribed' | 'complained';
    timestamp: number;
    id: string;
    recipient: string;
    message: {
      headers: {
        'message-id': string;
        from: string;
        to: string;
        subject: string;
      };
    };
    tags?: string[];
    'user-variables'?: Record<string, string>;
    'delivery-status'?: {
      message: string;
      code: number;
      description: string;
    };
    severity?: 'temporary' | 'permanent';
    reason?: 'bounce' | 'suppress-bounce' | 'suppress-unsubscribe' | 'suppress-complaint';
    url?: string; // For clicked events
  };
}

/**
 * Verify Mailgun webhook signature
 */
export function verifyWebhookSignature(
  timestamp: string,
  token: string,
  signature: string,
  signingKey: string
): boolean {
  const encodedToken = createHmac('sha256', signingKey)
    .update(`${timestamp}${token}`)
    .digest('hex');

  return encodedToken === signature;
}

/**
 * Handle webhook event
 */
export async function handleWebhookEvent(
  event: MailgunWebhook['event-data'],
  env: Env
): Promise<void> {
  console.log(`Mailgun event: ${event.event} for ${event.recipient}`);

  switch (event.event) {
    case 'delivered':
      await handleDelivered(event, env);
      break;

    case 'failed':
      await handleFailed(event, env);
      break;

    case 'opened':
      await handleOpened(event, env);
      break;

    case 'clicked':
      await handleClicked(event, env);
      break;

    case 'unsubscribed':
      await handleUnsubscribed(event, env);
      break;

    case 'complained':
      await handleComplained(event, env);
      break;

    default:
      console.log(`Unhandled event type: ${event.event}`);
  }
}

async function handleDelivered(
  event: MailgunWebhook['event-data'],
  env: Env
): Promise<void> {
  // Track successful delivery
  if (env.DB) {
    await env.DB.prepare(`
      INSERT INTO email_events (event_type, email, message_id, timestamp)
      VALUES (?, ?, ?, ?)
    `).bind(
      'delivered',
      event.recipient,
      event.message.headers['message-id'],
      event.timestamp
    ).run();
  }
}

async function handleFailed(
  event: MailgunWebhook['event-data'],
  env: Env
): Promise<void> {
  const isPermanent = event.severity === 'permanent';

  console.log(`Email failed: ${event.recipient} (${isPermanent ? 'permanent' : 'temporary'})`);

  if (isPermanent) {
    // Mark email as invalid in database
    if (env.DB) {
      await env.DB.prepare(`
        UPDATE users SET email_valid = 0 WHERE email = ?
      `).bind(event.recipient).run();
    }
  }

  // Log failure
  if (env.DB) {
    await env.DB.prepare(`
      INSERT INTO email_events (event_type, email, message_id, timestamp, metadata)
      VALUES (?, ?, ?, ?, ?)
    `).bind(
      'failed',
      event.recipient,
      event.message.headers['message-id'],
      event.timestamp,
      JSON.stringify({
        severity: event.severity,
        reason: event.reason,
        code: event['delivery-status']?.code,
        description: event['delivery-status']?.description,
      })
    ).run();
  }
}

async function handleOpened(
  event: MailgunWebhook['event-data'],
  env: Env
): Promise<void> {
  // Track email open
  if (env.DB) {
    await env.DB.prepare(`
      INSERT INTO email_opens (email, message_id, timestamp)
      VALUES (?, ?, ?)
    `).bind(
      event.recipient,
      event.message.headers['message-id'],
      event.timestamp
    ).run();
  }
}

async function handleClicked(
  event: MailgunWebhook['event-data'],
  env: Env
): Promise<void> {
  // Track email click
  if (env.DB) {
    await env.DB.prepare(`
      INSERT INTO email_clicks (email, message_id, url, timestamp)
      VALUES (?, ?, ?, ?)
    `).bind(
      event.recipient,
      event.message.headers['message-id'],
      event.url || '',
      event.timestamp
    ).run();
  }
}

async function handleUnsubscribed(
  event: MailgunWebhook['event-data'],
  env: Env
): Promise<void> {
  console.log(`User unsubscribed: ${event.recipient}`);

  // Update user subscription status
  if (env.DB) {
    await env.DB.prepare(`
      UPDATE users SET subscribed = 0 WHERE email = ?
    `).bind(event.recipient).run();
  }
}

async function handleComplained(
  event: MailgunWebhook['event-data'],
  env: Env
): Promise<void> {
  console.log(`Spam complaint from: ${event.recipient}`);

  // Immediately unsubscribe and mark as complained
  if (env.DB) {
    await env.DB.prepare(`
      UPDATE users SET subscribed = 0, spam_complained = 1 WHERE email = ?
    `).bind(event.recipient).run();
  }
}

/**
 * Cloudflare Worker handler
 */
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    const body = await request.text();
    const webhook: MailgunWebhook = JSON.parse(body);

    // Verify signature
    const isValid = verifyWebhookSignature(
      webhook.signature.timestamp,
      webhook.signature.token,
      webhook.signature.signature,
      env.MAILGUN_WEBHOOK_SIGNING_KEY
    );

    if (!isValid) {
      console.error('Invalid webhook signature');
      return new Response('Invalid signature', { status: 401 });
    }

    // Process event
    try {
      await handleWebhookEvent(webhook['event-data'], env);
      return new Response('OK', { status: 200 });
    } catch (error) {
      console.error('Error processing webhook:', error);
      return new Response('Internal error', { status: 500 });
    }
  },
};

/**
 * D1 Schema for webhook events
 */
export const schema = `
  CREATE TABLE IF NOT EXISTS email_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    email TEXT NOT NULL,
    message_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    metadata TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS email_opens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    message_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS email_clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    message_id TEXT NOT NULL,
    url TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE INDEX idx_email_events_email ON email_events(email);
  CREATE INDEX idx_email_events_timestamp ON email_events(timestamp);
  CREATE INDEX idx_email_opens_message_id ON email_opens(message_id);
  CREATE INDEX idx_email_clicks_message_id ON email_clicks(message_id);
`;
