# Email Gateway (Multi-Provider)

Multi-provider email sending skill for Cloudflare Workers and Node.js applications. Comprehensive coverage of Resend, SendGrid, Mailgun, and SMTP2Go APIs.

## Auto-Trigger Keywords

This skill should be suggested when the user mentions:

**Technology Names:**
- resend, resend api, resend.com
- sendgrid, sendgrid api, twilio sendgrid
- mailgun, mailgun api
- smtp2go, smtp2go api
- email api, email service, email provider
- transactional email, transactional emails

**Use Cases:**
- send email, sending emails, email delivery
- password reset email, verification email, confirmation email
- bulk email, batch email, mass email
- email templates, dynamic templates, react email
- email webhooks, bounce handling, complaint handling
- email attachments, file attachments
- smtp relay, email relay

**Error Messages:**
- "unauthorized" (resend, sendgrid, mailgun, smtp2go)
- "validation error" (resend, smtp2go)
- "rate limit exceeded" (resend, sendgrid, mailgun, smtp2go)
- "domain not verified" (resend, sendgrid, mailgun, smtp2go)
- "invalid email format" (all providers)
- "payload too large" (sendgrid)
- "attachment size exceeds" (resend, sendgrid, mailgun)
- "invalid template id" (sendgrid, mailgun)
- "failed to deliver" (all providers)

**React Email:**
- react email, react-email, @react-email/components
- jsx email, component email, email components
- html email templates, responsive email

**Webhooks:**
- email bounced, email delivered, email opened, email clicked
- bounce webhook, delivery webhook, open tracking, click tracking
- spam complaint, unsubscribe webhook
- webhook signature, verify webhook, webhook verification

**Migration:**
- switch from sendgrid to resend
- migrate from mailgun to sendgrid
- change email provider, email provider abstraction

## What This Skill Covers

1. **Provider Setup** - Configuration for Resend, SendGrid, Mailgun, SMTP2Go
2. **Sending Patterns** - Transactional, batch, templates, attachments
3. **React Email** - Component-driven email design (Resend)
4. **Dynamic Templates** - Handlebars/variable substitution
5. **Webhooks** - Event tracking, signature verification, bounce handling
6. **Error Handling** - Provider-specific error codes and recovery
7. **Rate Limiting** - Exponential backoff, quota tracking
8. **Migration** - Provider abstraction layer for switching
9. **Testing** - Connectivity tests, test mode sending

## Quick Example

```typescript
// Resend - Modern, React Email support
const response = await fetch('https://api.resend.com/emails', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${env.RESEND_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    from: 'noreply@yourdomain.com',
    to: 'user@example.com',
    subject: 'Welcome!',
    html: '<h1>Hello World</h1>',
  }),
});

// SendGrid - Enterprise scale
const response = await fetch('https://api.sendgrid.com/v3/mail/send', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${env.SENDGRID_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    personalizations: [{
      to: [{ email: 'user@example.com' }],
    }],
    from: { email: 'noreply@yourdomain.com' },
    subject: 'Welcome!',
    content: [{
      type: 'text/html',
      value: '<h1>Hello World</h1>',
    }],
  }),
});
```

## Related Skills

- **cloudflare-worker-base** - Cloudflare Workers setup
- **react-hook-form-zod** - Form validation before sending
- **project-planning** - Planning email features in applications
