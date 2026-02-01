/**
 * Resend Basic Email Template
 *
 * Minimal working example for sending emails via Resend API.
 * Requires RESEND_API_KEY environment variable.
 */

interface Env {
  RESEND_API_KEY: string;
}

interface ResendEmail {
  from: string;
  to: string | string[];
  subject: string;
  html?: string;
  text?: string;
  cc?: string | string[];
  bcc?: string | string[];
  replyTo?: string | string[];
  headers?: Record<string, string>;
  attachments?: Array<{
    filename: string;
    content: string; // base64
  }>;
  tags?: Record<string, string>;
  scheduledAt?: string; // ISO 8601
}

interface ResendResponse {
  id: string;
}

interface ResendError {
  statusCode: number;
  message: string;
  name: string;
}

/**
 * Send email via Resend API
 */
export async function sendEmail(
  email: ResendEmail,
  env: Env
): Promise<{ success: boolean; id?: string; error?: string }> {
  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(email),
    });

    if (!response.ok) {
      const error: ResendError = await response.json();
      return {
        success: false,
        error: `${error.statusCode}: ${error.message}`,
      };
    }

    const data: ResendResponse = await response.json();
    return {
      success: true,
      id: data.id,
    };
  } catch (error) {
    return {
      success: false,
      error: (error as Error).message,
    };
  }
}

/**
 * Example usage
 */
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const result = await sendEmail(
      {
        from: 'noreply@yourdomain.com',
        to: 'user@example.com',
        subject: 'Welcome to Our App',
        html: `
          <h1>Welcome!</h1>
          <p>Thanks for signing up.</p>
        `,
        text: 'Welcome! Thanks for signing up.',
      },
      env
    );

    if (!result.success) {
      return new Response(JSON.stringify({ error: result.error }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify({ emailId: result.id }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  },
};
