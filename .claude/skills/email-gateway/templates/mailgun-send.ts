/**
 * Mailgun Email Sending Template
 *
 * Send emails via Mailgun API with FormData.
 * Requires MAILGUN_API_KEY and MAILGUN_DOMAIN environment variables.
 */

interface Env {
  MAILGUN_API_KEY: string;
  MAILGUN_DOMAIN: string;
  MAILGUN_REGION?: 'us' | 'eu'; // Default: us
}

interface MailgunResponse {
  id: string;
  message: string;
}

interface MailgunError {
  message: string;
}

/**
 * Get Mailgun API base URL based on region
 */
function getMailgunApiUrl(region: 'us' | 'eu' = 'us'): string {
  return region === 'eu'
    ? 'https://api.eu.mailgun.net/v3'
    : 'https://api.mailgun.net/v3';
}

/**
 * Send email via Mailgun API
 */
export async function sendEmail(
  from: string,
  to: string | string[],
  subject: string,
  html: string,
  options: {
    text?: string;
    cc?: string | string[];
    bcc?: string | string[];
    replyTo?: string;
    tags?: string[];
    tracking?: boolean;
    trackingClicks?: boolean | 'htmlonly';
    trackingOpens?: boolean;
    customVariables?: Record<string, string>;
  } = {},
  env: Env
): Promise<{ success: boolean; id?: string; error?: string }> {
  const formData = new FormData();

  formData.append('from', from);

  if (Array.isArray(to)) {
    to.forEach(recipient => formData.append('to', recipient));
  } else {
    formData.append('to', to);
  }

  formData.append('subject', subject);
  formData.append('html', html);

  if (options.text) {
    formData.append('text', options.text);
  }

  if (options.cc) {
    const ccList = Array.isArray(options.cc) ? options.cc : [options.cc];
    ccList.forEach(recipient => formData.append('cc', recipient));
  }

  if (options.bcc) {
    const bccList = Array.isArray(options.bcc) ? options.bcc : [options.bcc];
    bccList.forEach(recipient => formData.append('bcc', recipient));
  }

  if (options.replyTo) {
    formData.append('h:Reply-To', options.replyTo);
  }

  if (options.tags) {
    options.tags.forEach(tag => formData.append('o:tag', tag));
  }

  if (options.tracking !== undefined) {
    formData.append('o:tracking', options.tracking ? 'yes' : 'no');
  }

  if (options.trackingClicks !== undefined) {
    formData.append(
      'o:tracking-clicks',
      typeof options.trackingClicks === 'boolean'
        ? (options.trackingClicks ? 'yes' : 'no')
        : options.trackingClicks
    );
  }

  if (options.trackingOpens !== undefined) {
    formData.append('o:tracking-opens', options.trackingOpens ? 'yes' : 'no');
  }

  if (options.customVariables) {
    formData.append('h:X-Mailgun-Variables', JSON.stringify(options.customVariables));
  }

  const apiUrl = getMailgunApiUrl(env.MAILGUN_REGION);
  const response = await fetch(`${apiUrl}/${env.MAILGUN_DOMAIN}/messages`, {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${btoa(`api:${env.MAILGUN_API_KEY}`)}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error: MailgunError = await response.json();
    return {
      success: false,
      error: error.message,
    };
  }

  const data: MailgunResponse = await response.json();
  return {
    success: true,
    id: data.id,
  };
}

/**
 * Send email with attachment
 */
export async function sendEmailWithAttachment(
  from: string,
  to: string,
  subject: string,
  html: string,
  attachment: File,
  env: Env
): Promise<{ success: boolean; id?: string; error?: string }> {
  const formData = new FormData();

  formData.append('from', from);
  formData.append('to', to);
  formData.append('subject', subject);
  formData.append('html', html);
  formData.append('attachment', attachment);

  const apiUrl = getMailgunApiUrl(env.MAILGUN_REGION);
  const response = await fetch(`${apiUrl}/${env.MAILGUN_DOMAIN}/messages`, {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${btoa(`api:${env.MAILGUN_API_KEY}`)}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error: MailgunError = await response.json();
    return {
      success: false,
      error: error.message,
    };
  }

  const data: MailgunResponse = await response.json();
  return {
    success: true,
    id: data.id,
  };
}

/**
 * Send email using Mailgun template
 */
export async function sendTemplateEmail(
  from: string,
  to: string,
  subject: string,
  templateName: string,
  templateVariables: Record<string, unknown>,
  env: Env
): Promise<{ success: boolean; id?: string; error?: string }> {
  const formData = new FormData();

  formData.append('from', from);
  formData.append('to', to);
  formData.append('subject', subject);
  formData.append('template', templateName);
  formData.append('h:X-Mailgun-Variables', JSON.stringify(templateVariables));

  const apiUrl = getMailgunApiUrl(env.MAILGUN_REGION);
  const response = await fetch(`${apiUrl}/${env.MAILGUN_DOMAIN}/messages`, {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${btoa(`api:${env.MAILGUN_API_KEY}`)}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error: MailgunError = await response.json();
    return {
      success: false,
      error: error.message,
    };
  }

  const data: MailgunResponse = await response.json();
  return {
    success: true,
    id: data.id,
  };
}

/**
 * Send password reset email
 */
export async function sendPasswordReset(
  to: string,
  resetToken: string,
  env: Env
): Promise<{ success: boolean; id?: string; error?: string }> {
  const resetUrl = `https://yourapp.com/reset-password?token=${resetToken}`;

  const html = `
    <!DOCTYPE html>
    <html>
      <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h1>Reset Your Password</h1>
          <p>Click the link below to reset your password:</p>
          <a href="${resetUrl}"
             style="display: inline-block; padding: 12px 24px; background: #000; color: #fff; text-decoration: none; border-radius: 4px;">
            Reset Password
          </a>
          <p style="margin-top: 20px; color: #666; font-size: 14px;">
            This link expires in 1 hour.
          </p>
        </div>
      </body>
    </html>
  `;

  return sendEmail(
    'noreply@yourdomain.com',
    to,
    'Reset Your Password',
    html,
    {
      tags: ['password-reset'],
      tracking: true,
    },
    env
  );
}

/**
 * Example Cloudflare Worker
 */
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/send-reset') {
      const { email, token } = await request.json();
      const result = await sendPasswordReset(email, token, env);

      if (!result.success) {
        return new Response(JSON.stringify({ error: result.error }), {
          status: 500,
          headers: { 'Content-Type': 'application/json' },
        });
      }

      return new Response(JSON.stringify({ success: true, id: result.id }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    if (url.pathname === '/send-welcome') {
      const { email, name } = await request.json();

      const result = await sendEmail(
        'noreply@yourdomain.com',
        email,
        `Welcome, ${name}!`,
        `<h1>Welcome to Our App</h1><p>Hi ${name}, thanks for signing up!</p>`,
        {
          tags: ['welcome'],
          tracking: true,
          trackingClicks: 'htmlonly',
          trackingOpens: true,
        },
        env
      );

      if (!result.success) {
        return new Response(JSON.stringify({ error: result.error }), {
          status: 500,
          headers: { 'Content-Type': 'application/json' },
        });
      }

      return new Response(JSON.stringify({ success: true, id: result.id }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response('Not found', { status: 404 });
  },
};
