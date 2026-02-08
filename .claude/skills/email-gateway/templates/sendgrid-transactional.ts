/**
 * SendGrid Transactional Email Template
 *
 * Send individual transactional emails via SendGrid Mail Send API.
 * Requires SENDGRID_API_KEY environment variable.
 */

interface Env {
  SENDGRID_API_KEY: string;
}

interface SendGridEmail {
  personalizations: Array<{
    to: Array<{ email: string; name?: string }>;
    cc?: Array<{ email: string; name?: string }>;
    bcc?: Array<{ email: string; name?: string }>;
    subject?: string;
    headers?: Record<string, string>;
    substitutions?: Record<string, string>;
    custom_args?: Record<string, string>;
  }>;
  from: { email: string; name?: string };
  reply_to?: { email: string; name?: string };
  subject?: string;
  content?: Array<{
    type: 'text/plain' | 'text/html';
    value: string;
  }>;
  attachments?: Array<{
    content: string; // base64
    filename: string;
    type?: string;
    disposition?: 'inline' | 'attachment';
    content_id?: string;
  }>;
  categories?: string[];
  send_at?: number; // Unix timestamp
  custom_args?: Record<string, string>;
  asm?: {
    group_id: number;
    groups_to_display?: number[];
  };
}

interface SendGridError {
  errors: Array<{
    message: string;
    field?: string;
    help?: string;
  }>;
}

/**
 * Send email via SendGrid API
 */
export async function sendEmail(
  email: SendGridEmail,
  env: Env
): Promise<{ success: boolean; error?: string }> {
  try {
    const response = await fetch('https://api.sendgrid.com/v3/mail/send', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.SENDGRID_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(email),
    });

    if (!response.ok) {
      const error: SendGridError = await response.json();
      const errorMessages = error.errors.map(e => e.message).join(', ');
      return {
        success: false,
        error: `SendGrid Error: ${errorMessages}`,
      };
    }

    // SendGrid returns 202 with no body on success
    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: (error as Error).message,
    };
  }
}

/**
 * Send simple email helper
 */
export async function sendSimpleEmail(
  to: string,
  subject: string,
  html: string,
  env: Env
): Promise<{ success: boolean; error?: string }> {
  return sendEmail(
    {
      personalizations: [{
        to: [{ email: to }],
      }],
      from: { email: 'noreply@yourdomain.com', name: 'Your App' },
      subject,
      content: [{
        type: 'text/html',
        value: html,
      }],
    },
    env
  );
}

/**
 * Send password reset email
 */
export async function sendPasswordReset(
  to: string,
  resetToken: string,
  env: Env
): Promise<{ success: boolean; error?: string }> {
  const resetUrl = `https://yourapp.com/reset-password?token=${resetToken}`;

  const html = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
      </head>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h1 style="color: #000;">Reset Your Password</h1>
          <p>You requested to reset your password. Click the button below to continue:</p>
          <div style="margin: 30px 0;">
            <a href="${resetUrl}"
               style="display: inline-block; padding: 12px 24px; background: #000; color: #fff; text-decoration: none; border-radius: 4px;">
              Reset Password
            </a>
          </div>
          <p style="color: #666; font-size: 14px;">
            This link expires in 1 hour. If you didn't request this, you can safely ignore this email.
          </p>
        </div>
      </body>
    </html>
  `;

  return sendEmail(
    {
      personalizations: [{
        to: [{ email: to }],
      }],
      from: { email: 'noreply@yourdomain.com', name: 'Your App' },
      subject: 'Reset Your Password',
      content: [{
        type: 'text/html',
        value: html,
      }],
      categories: ['password-reset'],
    },
    env
  );
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
  env: Env
): Promise<{ success: boolean; error?: string }> {
  return sendEmail(
    {
      personalizations: [{
        to: [{ email: to }],
      }],
      from: { email: 'noreply@yourdomain.com' },
      subject,
      content: [{
        type: 'text/html',
        value: html,
      }],
      attachments: [{
        content: attachmentContent,
        filename: attachmentFilename,
        type: 'application/pdf',
        disposition: 'attachment',
      }],
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

      return new Response(JSON.stringify({ success: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response('Not found', { status: 404 });
  },
};
