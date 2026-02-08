/**
 * SMTP2Go Bulk Email Template
 *
 * Advanced bulk sending with rate limiting, retry logic, and progress tracking.
 * Optimized for large email campaigns via SMTP2Go API.
 */

interface Env {
  SMTP2GO_API_KEY: string;
  // Optional: KV for rate limiting
  RATE_LIMITS?: KVNamespace;
  // Optional: D1 for tracking sends
  DB?: D1Database;
}

interface BulkEmailRecipient {
  email: string;
  subject: string;
  html: string;
  text?: string;
  customHeaders?: Record<string, string>;
}

interface BulkSendResult {
  total: number;
  succeeded: number;
  failed: number;
  results: Array<{
    email: string;
    success: boolean;
    id?: string;
    error?: string;
  }>;
}

/**
 * Format email address for SMTP2Go (requires angle brackets)
 */
function formatEmail(email: string): string {
  return email.includes('<') ? email : `<${email}>`;
}

/**
 * Send single email with retry logic
 */
async function sendEmailWithRetry(
  recipient: BulkEmailRecipient,
  env: Env,
  maxRetries = 3
): Promise<{ success: boolean; id?: string; error?: string }> {
  let lastError: string | undefined;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch('https://api.smtp2go.com/v3/email/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: env.SMTP2GO_API_KEY,
          to: [formatEmail(recipient.email)],
          sender: 'noreply@yourdomain.com',
          subject: recipient.subject,
          html_body: recipient.html,
          text_body: recipient.text,
          custom_headers: recipient.customHeaders
            ? Object.entries(recipient.customHeaders).map(([header, value]) => ({
                header,
                value,
              }))
            : undefined,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        lastError = error.data?.error || 'Unknown error';

        // Don't retry 4xx errors (client errors)
        if (response.status >= 400 && response.status < 500) {
          return { success: false, error: lastError };
        }

        // Retry 5xx errors with exponential backoff
        if (attempt < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
          continue;
        }

        return { success: false, error: lastError };
      }

      const data = await response.json();

      if (data.data.failed > 0) {
        return {
          success: false,
          error: data.data.failures?.join(', ') || 'Unknown error',
        };
      }

      return {
        success: true,
        id: data.data.email_id,
      };
    } catch (error) {
      lastError = (error as Error).message;

      if (attempt < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
      }
    }
  }

  return { success: false, error: lastError };
}

/**
 * Check rate limit (10 requests/second for SMTP2Go)
 */
async function checkRateLimit(env: Env): Promise<boolean> {
  if (!env.RATE_LIMITS) return true;

  const key = 'smtp2go:rate-limit';
  const count = await env.RATE_LIMITS.get(key);

  if (!count) {
    await env.RATE_LIMITS.put(key, '1', { expirationTtl: 1 });
    return true;
  }

  const currentCount = parseInt(count);
  if (currentCount >= 10) {
    return false;
  }

  await env.RATE_LIMITS.put(key, String(currentCount + 1), { expirationTtl: 1 });
  return true;
}

/**
 * Send bulk emails with rate limiting
 */
export async function sendBulkEmails(
  recipients: BulkEmailRecipient[],
  env: Env,
  options: {
    batchSize?: number;
    delayBetweenBatches?: number;
    onProgress?: (sent: number, total: number) => void;
  } = {}
): Promise<BulkSendResult> {
  const batchSize = options.batchSize || 100;
  const delayBetweenBatches = options.delayBetweenBatches || 10000; // 10 seconds

  const results: BulkSendResult['results'] = [];
  let succeeded = 0;
  let failed = 0;

  // Process in batches
  for (let i = 0; i < recipients.length; i += batchSize) {
    const batch = recipients.slice(i, i + batchSize);

    // Send batch with rate limiting
    for (const recipient of batch) {
      // Wait if rate limit reached
      let canSend = await checkRateLimit(env);
      while (!canSend) {
        await new Promise(resolve => setTimeout(resolve, 100));
        canSend = await checkRateLimit(env);
      }

      const result = await sendEmailWithRetry(recipient, env);

      results.push({
        email: recipient.email,
        ...result,
      });

      if (result.success) {
        succeeded++;
      } else {
        failed++;
      }

      // Track in database if available
      if (env.DB) {
        await env.DB.prepare(`
          INSERT INTO bulk_send_log (email, success, email_id, error, sent_at)
          VALUES (?, ?, ?, ?, ?)
        `).bind(
          recipient.email,
          result.success ? 1 : 0,
          result.id || null,
          result.error || null,
          Date.now()
        ).run();
      }

      // Progress callback
      if (options.onProgress) {
        options.onProgress(i + batch.indexOf(recipient) + 1, recipients.length);
      }

      // Small delay to avoid overwhelming the API
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    // Delay between batches (except for last batch)
    if (i + batchSize < recipients.length) {
      await new Promise(resolve => setTimeout(resolve, delayBetweenBatches));
    }
  }

  return {
    total: recipients.length,
    succeeded,
    failed,
    results,
  };
}

/**
 * Send campaign email to list
 */
export async function sendCampaign(
  recipientEmails: string[],
  subject: string,
  html: string,
  text: string,
  env: Env
): Promise<BulkSendResult> {
  const recipients: BulkEmailRecipient[] = recipientEmails.map(email => ({
    email,
    subject,
    html,
    text,
  }));

  return sendBulkEmails(recipients, env, {
    batchSize: 100,
    delayBetweenBatches: 10000,
    onProgress: (sent, total) => {
      console.log(`Sent ${sent}/${total} emails`);
    },
  });
}

/**
 * Send personalized bulk emails
 */
export async function sendPersonalizedBulk(
  recipients: Array<{
    email: string;
    variables: Record<string, string>;
  }>,
  subjectTemplate: string,
  htmlTemplate: string,
  textTemplate: string,
  env: Env
): Promise<BulkSendResult> {
  const emails: BulkEmailRecipient[] = recipients.map(recipient => ({
    email: recipient.email,
    subject: replaceVariables(subjectTemplate, recipient.variables),
    html: replaceVariables(htmlTemplate, recipient.variables),
    text: replaceVariables(textTemplate, recipient.variables),
  }));

  return sendBulkEmails(emails, env);
}

/**
 * Replace {{variable}} placeholders in template
 */
function replaceVariables(template: string, variables: Record<string, string>): string {
  return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return variables[key] || match;
  });
}

/**
 * Cloudflare Worker handler
 */
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/send-campaign') {
      const { recipients, subject, html, text } = await request.json();

      const result = await sendCampaign(recipients, subject, html, text, env);

      return new Response(JSON.stringify(result), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    if (url.pathname === '/send-personalized') {
      const { recipients, subjectTemplate, htmlTemplate, textTemplate } = await request.json();

      const result = await sendPersonalizedBulk(
        recipients,
        subjectTemplate,
        htmlTemplate,
        textTemplate,
        env
      );

      return new Response(JSON.stringify(result), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response('Not found', { status: 404 });
  },
};

/**
 * D1 Schema for bulk send tracking
 */
export const schema = `
  CREATE TABLE IF NOT EXISTS bulk_send_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    success INTEGER NOT NULL,
    email_id TEXT,
    error TEXT,
    sent_at INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE INDEX idx_bulk_send_email ON bulk_send_log(email);
  CREATE INDEX idx_bulk_send_sent_at ON bulk_send_log(sent_at);
`;
