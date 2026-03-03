/**
 * SMTP2Go Email Sending Template
 *
 * Send emails via SMTP2Go API (Australian-based provider).
 * Requires SMTP2GO_API_KEY environment variable.
 */

interface Env {
  SMTP2GO_API_KEY: string;
}

interface SMTP2GoEmail {
  api_key: string;
  to: string[]; // Must use angle brackets: ['<email@domain.com>']
  sender: string;
  subject: string;
  html_body?: string;
  text_body?: string;
  custom_headers?: Array<{
    header: string;
    value: string;
  }>;
  attachments?: Array<{
    filename: string;
    fileblob: string; // base64
    mimetype?: string;
  }>;
}

interface SMTP2GoResponse {
  data: {
    succeeded: number;
    failed: number;
    failures?: string[];
    email_id?: string;
  };
}

interface SMTP2GoError {
  data: {
    error: string;
    error_code: string;
  };
}

/**
 * Format email address for SMTP2Go (requires angle brackets)
 */
function formatEmail(email: string): string {
  return email.includes('<') ? email : `<${email}>`;
}

/**
 * Send email via SMTP2Go API
 */
export async function sendEmail(
  to: string | string[],
  subject: string,
  html: string,
  options: {
    text?: string;
    sender?: string;
    replyTo?: string;
    cc?: string[];
    bcc?: string[];
    customHeaders?: Record<string, string>;
  } = {},
  env: Env
): Promise<{ success: boolean; id?: string; error?: string }> {
  const recipients = Array.isArray(to) ? to : [to];

  const email: SMTP2GoEmail = {
    api_key: env.SMTP2GO_API_KEY,
    to: recipients.map(formatEmail),
    sender: options.sender || 'noreply@yourdomain.com',
    subject,
    html_body: html,
  };

  if (options.text) {
    email.text_body = options.text;
  }

  if (options.customHeaders) {
    email.custom_headers = Object.entries(options.customHeaders).map(([header, value]) => ({
      header,
      value,
    }));
  }

  if (options.replyTo) {
    email.custom_headers = email.custom_headers || [];
    email.custom_headers.push({
      header: 'Reply-To',
      value: options.replyTo,
    });
  }

  if (options.cc) {
    email.custom_headers = email.custom_headers || [];
    email.custom_headers.push({
      header: 'Cc',
      value: options.cc.map(formatEmail).join(', '),
    });
  }

  if (options.bcc) {
    email.custom_headers = email.custom_headers || [];
    email.custom_headers.push({
      header: 'Bcc',
      value: options.bcc.map(formatEmail).join(', '),
    });
  }

  try {
    const response = await fetch('https://api.smtp2go.com/v3/email/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(email),
    });

    if (!response.ok) {
      const error: SMTP2GoError = await response.json();
      return {
        success: false,
        error: `${error.data.error_code}: ${error.data.error}`,
      };
    }

    const data: SMTP2GoResponse = await response.json();

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
    return {
      success: false,
      error: (error as Error).message,
    };
  }
}

/**
 * Send email with attachment
 */
export async function sendEmailWithAttachment(
  to: string,
  subject: string,
  html: string,
  attachmentContent: string, // base64
  attachmentFilename: string,
  attachmentMimeType: string,
  env: Env
): Promise<{ success: boolean; id?: string; error?: string }> {
  const email: SMTP2GoEmail = {
    api_key: env.SMTP2GO_API_KEY,
    to: [formatEmail(to)],
    sender: 'noreply@yourdomain.com',
    subject,
    html_body: html,
    attachments: [{
      filename: attachmentFilename,
      fileblob: attachmentContent,
      mimetype: attachmentMimeType,
    }],
  };

  try {
    const response = await fetch('https://api.smtp2go.com/v3/email/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(email),
    });

    if (!response.ok) {
      const error: SMTP2GoError = await response.json();
      return {
        success: false,
        error: `${error.data.error_code}: ${error.data.error}`,
      };
    }

    const data: SMTP2GoResponse = await response.json();

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
    return {
      success: false,
      error: (error as Error).message,
    };
  }
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
    to,
    'Reset Your Password',
    html,
    {
      text: `Reset your password: ${resetUrl}\n\nThis link expires in 1 hour.`,
    },
    env
  );
}

/**
 * Send bulk emails (batch processing)
 */
export async function sendBulkEmails(
  recipients: Array<{
    email: string;
    subject: string;
    html: string;
  }>,
  env: Env
): Promise<Array<{ email: string; success: boolean; id?: string; error?: string }>> {
  const results = [];

  // SMTP2Go allows 100 recipients per request, but we'll send individually
  // for better error tracking per recipient
  for (const recipient of recipients) {
    const result = await sendEmail(
      recipient.email,
      recipient.subject,
      recipient.html,
      {},
      env
    );

    results.push({
      email: recipient.email,
      ...result,
    });

    // Rate limiting: 10 requests/second max
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  return results;
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
        email,
        `Welcome, ${name}!`,
        `<h1>Welcome to Our App</h1><p>Hi ${name}, thanks for signing up!</p>`,
        {
          text: `Welcome to Our App\n\nHi ${name}, thanks for signing up!`,
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

    if (url.pathname === '/send-bulk') {
      const { recipients } = await request.json();
      const results = await sendBulkEmails(recipients, env);

      const succeeded = results.filter(r => r.success).length;
      const failed = results.filter(r => !r.success).length;

      return new Response(JSON.stringify({
        succeeded,
        failed,
        results,
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response('Not found', { status: 404 });
  },
};
