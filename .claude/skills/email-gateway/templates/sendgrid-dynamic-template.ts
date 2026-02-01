/**
 * SendGrid Dynamic Template
 *
 * Use SendGrid's dynamic templates with handlebars variables.
 * Create templates in SendGrid dashboard first.
 */

interface Env {
  SENDGRID_API_KEY: string;
}

interface DynamicTemplateData {
  [key: string]: unknown;
}

/**
 * Send email using dynamic template
 */
export async function sendDynamicTemplate(
  to: string | Array<{ email: string; name?: string }>,
  templateId: string,
  dynamicData: DynamicTemplateData,
  env: Env
): Promise<{ success: boolean; error?: string }> {
  const recipients = Array.isArray(to)
    ? to
    : [{ email: to }];

  const response = await fetch('https://api.sendgrid.com/v3/mail/send', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.SENDGRID_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      personalizations: [{
        to: recipients,
        dynamic_template_data: dynamicData,
      }],
      from: { email: 'noreply@yourdomain.com', name: 'Your App' },
      template_id: templateId,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    return {
      success: false,
      error: error.errors?.map((e: any) => e.message).join(', ') || 'Unknown error',
    };
  }

  return { success: true };
}

/**
 * Send batch emails with different data per recipient
 */
export async function sendBatchDynamicTemplate(
  recipients: Array<{
    email: string;
    name?: string;
    data: DynamicTemplateData;
  }>,
  templateId: string,
  env: Env
): Promise<{ success: boolean; error?: string }> {
  const response = await fetch('https://api.sendgrid.com/v3/mail/send', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.SENDGRID_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      personalizations: recipients.map(r => ({
        to: [{ email: r.email, name: r.name }],
        dynamic_template_data: r.data,
      })),
      from: { email: 'noreply@yourdomain.com', name: 'Your App' },
      template_id: templateId,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    return {
      success: false,
      error: error.errors?.map((e: any) => e.message).join(', ') || 'Unknown error',
    };
  }

  return { success: true };
}

/**
 * Example: Welcome email template
 *
 * Create template in SendGrid dashboard:
 * - Subject: Welcome to {{companyName}}, {{firstName}}!
 * - Body:
 *   <h1>Hi {{firstName}},</h1>
 *   <p>Welcome to {{companyName}}! We're excited to have you.</p>
 *   <a href="{{confirmUrl}}">Confirm Your Email</a>
 */
export async function sendWelcomeEmail(
  email: string,
  firstName: string,
  confirmUrl: string,
  env: Env
): Promise<{ success: boolean; error?: string }> {
  const WELCOME_TEMPLATE_ID = 'd-xxxxxxxxxxxxxxxxxxxxxxxx';

  return sendDynamicTemplate(
    email,
    WELCOME_TEMPLATE_ID,
    {
      firstName,
      companyName: 'Your App',
      confirmUrl,
    },
    env
  );
}

/**
 * Example: Weekly digest template
 *
 * Template variables:
 * - {{userName}}
 * - {{weekStart}}
 * - {{weekEnd}}
 * - {{activities}} (array)
 */
export async function sendWeeklyDigest(
  email: string,
  userName: string,
  activities: Array<{ title: string; date: string; url: string }>,
  env: Env
): Promise<{ success: boolean; error?: string }> {
  const DIGEST_TEMPLATE_ID = 'd-yyyyyyyyyyyyyyyyyyyyyyyy';

  const now = new Date();
  const weekStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

  return sendDynamicTemplate(
    email,
    DIGEST_TEMPLATE_ID,
    {
      userName,
      weekStart: weekStart.toLocaleDateString(),
      weekEnd: now.toLocaleDateString(),
      activities,
    },
    env
  );
}

/**
 * Example: Batch onboarding emails
 */
export async function sendBatchOnboarding(
  users: Array<{
    email: string;
    name: string;
    plan: string;
    trialEnds: string;
  }>,
  env: Env
): Promise<{ success: boolean; error?: string }> {
  const ONBOARDING_TEMPLATE_ID = 'd-zzzzzzzzzzzzzzzzzzzzzzzz';

  return sendBatchDynamicTemplate(
    users.map(user => ({
      email: user.email,
      name: user.name,
      data: {
        firstName: user.name.split(' ')[0],
        plan: user.plan,
        trialEnds: user.trialEnds,
      },
    })),
    ONBOARDING_TEMPLATE_ID,
    env
  );
}

/**
 * Example Cloudflare Worker
 */
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/send-welcome') {
      const { email, firstName, confirmUrl } = await request.json();
      const result = await sendWelcomeEmail(email, firstName, confirmUrl, env);

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
