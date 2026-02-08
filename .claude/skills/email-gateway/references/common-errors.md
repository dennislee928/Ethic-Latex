# Common Email API Errors

Comprehensive error reference for all four providers with solutions.

## Resend Errors

### Authentication Errors

**401 Unauthorized**

Error:
```json
{
  "statusCode": 401,
  "message": "Missing API key",
  "name": "missing_api_key"
}
```

Cause: Missing or invalid `Authorization` header

Fix:
```typescript
headers: {
  'Authorization': `Bearer ${env.RESEND_API_KEY}`, // Must start with "re_"
  'Content-Type': 'application/json',
}
```

---

### Validation Errors

**422 Validation Error - Missing `to` field**

Error:
```json
{
  "statusCode": 422,
  "message": "The `to` field is required.",
  "name": "validation_error"
}
```

Fix: Ensure `to` field is present and non-empty

```typescript
{
  from: 'noreply@yourdomain.com',
  to: 'user@example.com', // Required
  subject: 'Welcome',
  html: '<h1>Hello</h1>',
}
```

---

**422 Validation Error - Invalid Email Format**

Error:
```json
{
  "statusCode": 422,
  "message": "Invalid email format",
  "name": "validation_error"
}
```

Fix: Validate email format before sending

```typescript
function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

if (!isValidEmail(to)) {
  throw new Error('Invalid email address');
}
```

---

**422 Validation Error - Domain Not Verified**

Error:
```json
{
  "statusCode": 422,
  "message": "The `from` email address domain is not verified.",
  "name": "validation_error"
}
```

Fix:
1. Go to Resend dashboard → Domains
2. Add domain and configure DNS records
3. Wait for verification (can take up to 48 hours)
4. Use verified domain in `from` field

---

**422 Validation Error - Attachment Too Large**

Error:
```json
{
  "statusCode": 422,
  "message": "Attachment size exceeds 40 MB",
  "name": "validation_error"
}
```

Fix: Reduce attachment size or host file externally

```typescript
const MAX_SIZE = 40 * 1024 * 1024; // 40 MB

if (fileSize > MAX_SIZE) {
  // Host file on R2/S3 and send link instead
  const fileUrl = await uploadToR2(file);
  html += `<a href="${fileUrl}">Download file</a>`;
}
```

---

### Rate Limiting

**429 Too Many Requests**

Error:
```json
{
  "statusCode": 429,
  "message": "Rate limit exceeded",
  "name": "rate_limit_exceeded"
}
```

Response headers:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets
- `Retry-After`: Seconds to wait before retrying

Fix: Implement exponential backoff

```typescript
async function sendWithRetry(sendFn: () => Promise<Response>, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const response = await sendFn();

    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After');
      const delay = retryAfter ? parseInt(retryAfter) * 1000 : Math.pow(2, attempt) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
      continue;
    }

    return response;
  }

  throw new Error('Max retries exceeded');
}
```

---

### Server Errors

**500 Internal Server Error**

Error:
```json
{
  "statusCode": 500,
  "message": "Internal server error",
  "name": "internal_error"
}
```

Fix: Retry with exponential backoff (transient issue)

---

## SendGrid Errors

### Authentication Errors

**401 Unauthorized**

Error:
```json
{
  "errors": [{
    "message": "The provided authorization grant is invalid, expired, or revoked",
    "field": null,
    "help": null
  }]
}
```

Cause: Invalid API key

Fix: Verify API key starts with `SG.` and has correct permissions

```typescript
headers: {
  'Authorization': `Bearer ${env.SENDGRID_API_KEY}`, // Must start with "SG."
}
```

---

### Validation Errors

**400 Bad Request - Missing Personalizations**

Error:
```json
{
  "errors": [{
    "message": "The personalizations field is required.",
    "field": "personalizations",
    "help": "http://sendgrid.com/docs/API_Reference/Web_API_v3/Mail/errors.html#message.personalizations"
  }]
}
```

Fix: Include personalizations array

```typescript
{
  personalizations: [{ // Required
    to: [{ email: 'user@example.com' }],
  }],
  from: { email: 'noreply@yourdomain.com' },
  subject: 'Welcome',
  content: [{ type: 'text/html', value: '<h1>Hello</h1>' }],
}
```

---

**400 Bad Request - Invalid From Address**

Error:
```json
{
  "errors": [{
    "message": "The from email does not contain a valid address.",
    "field": "from.email",
    "help": "http://sendgrid.com/docs/API_Reference/Web_API_v3/Mail/errors.html#message.from.email"
  }]
}
```

Fix: Verify sender domain

1. Go to SendGrid dashboard → Settings → Sender Authentication
2. Authenticate domain or single sender
3. Use verified email in `from` field

---

**400 Bad Request - Invalid Template ID**

Error:
```json
{
  "errors": [{
    "message": "The template_id is invalid.",
    "field": "template_id",
    "help": null
  }]
}
```

Fix: Verify template exists and ID is correct

```bash
# List templates via API
curl https://api.sendgrid.com/v3/templates \
  -H "Authorization: Bearer $SENDGRID_API_KEY"
```

---

**413 Payload Too Large**

Error:
```json
{
  "errors": [{
    "message": "The message size exceeds the maximum allowed (20 MB).",
    "field": null,
    "help": null
  }]
}
```

Fix: Reduce message size or split into multiple emails

---

### Rate Limiting

**429 Too Many Requests**

Response headers:
- `X-RateLimit-Limit`: 600 requests/second
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp

Fix: Implement rate limiting (same as Resend)

---

## Mailgun Errors

### Authentication Errors

**401 Unauthorized**

Error:
```json
{
  "message": "Forbidden"
}
```

Cause: Invalid API key or wrong region

Fix: Verify API key and region

```typescript
// US region
const apiUrl = 'https://api.mailgun.net/v3';

// EU region
const apiUrl = 'https://api.eu.mailgun.net/v3';

headers: {
  'Authorization': `Basic ${btoa(`api:${env.MAILGUN_API_KEY}`)}`,
}
```

---

### Domain Errors

**404 Not Found**

Error:
```json
{
  "message": "Domain not found: invalid.domain.com"
}
```

Fix: Verify domain is added and active in Mailgun dashboard

---

### Validation Errors

**400 Bad Request - Invalid Recipient**

Error:
```json
{
  "message": "'to' parameter is not a valid address. please check documentation"
}
```

Fix: Ensure email format is correct

```typescript
// Mailgun is strict about email format
formData.append('to', 'user@example.com'); // Correct
formData.append('to', 'User <user@example.com>'); // Also correct
formData.append('to', 'user@'); // ❌ Invalid
```

---

**400 Bad Request - Invalid Template Variables**

Error:
```json
{
  "message": "Template variable parsing error"
}
```

Fix: Ensure template variables are valid JSON

```typescript
formData.append('h:X-Mailgun-Variables', JSON.stringify({
  name: 'Alice',
  code: '123',
})); // Must be valid JSON string
```

---

### Quota Errors

**402 Payment Required**

Error:
```json
{
  "message": "Free accounts are limited to 100 emails per day. Please upgrade."
}
```

Fix: Upgrade plan or wait for quota reset

---

## SMTP2Go Errors

### Authentication Errors

**401 Unauthorized**

Error:
```json
{
  "data": {
    "error": "Invalid API Key",
    "error_code": "E_ApiResponseCodes_INVALID_API_KEY"
  }
}
```

Fix: Verify API key is active

```typescript
{
  api_key: env.SMTP2GO_API_KEY, // Must be valid and active
}
```

---

### Validation Errors

**422 Validation Error - Invalid Sender**

Error:
```json
{
  "data": {
    "error": "Invalid sender email address",
    "error_code": "E_ApiResponseCodes_INVALID_SENDER_ADDRESS"
  }
}
```

Fix: Verify sender domain or use verified sender

---

**422 Validation Error - Invalid Recipient Format**

Error:
```json
{
  "data": {
    "error": "Invalid recipient format",
    "error_code": "E_ApiResponseCodes_INVALID_RECIPIENT"
  }
}
```

Fix: SMTP2Go requires angle brackets for recipients

```typescript
// ❌ Wrong
to: ['user@example.com']

// ✅ Correct
to: ['<user@example.com>']

// Helper function
function formatEmail(email: string): string {
  return email.includes('<') ? email : `<${email}>`;
}
```

---

### Rate Limiting

**429 Too Many Requests**

Error:
```json
{
  "data": {
    "error": "Rate limit exceeded",
    "error_code": "E_ApiResponseCodes_RATE_LIMIT_EXCEEDED"
  }
}
```

Fix: SMTP2Go allows 10 requests/second. Implement throttling.

---

## Cross-Provider Error Patterns

### Domain Not Verified

All providers require domain verification. Steps:

1. **Add domain** in provider dashboard
2. **Add DNS records**:
   - SPF: `v=spf1 include:_spf.provider.com ~all`
   - DKIM: `<selector>._domainkey TXT <value>`
   - DMARC: `_dmarc TXT v=DMARC1; p=none;`
3. **Wait for verification** (15 minutes to 48 hours)
4. **Test** with provider's verification tool

---

### Invalid Email Format

All providers reject malformed emails. Validate before sending:

```typescript
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateEmail(email: string): boolean {
  if (!EMAIL_REGEX.test(email)) return false;

  // Additional checks
  if (email.length > 254) return false; // RFC 5321
  const [local, domain] = email.split('@');
  if (local.length > 64) return false; // RFC 5321
  if (domain.length > 253) return false; // RFC 1035

  return true;
}
```

---

### Rate Limit Exceeded

All providers have rate limits. Use exponential backoff:

```typescript
async function sendWithBackoff(
  sendFn: () => Promise<Response>,
  maxRetries = 5
): Promise<Response> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await sendFn();

      if (response.status === 429) {
        const retryAfter = response.headers.get('Retry-After');
        const delay = retryAfter
          ? parseInt(retryAfter) * 1000
          : Math.pow(2, attempt) * 1000;

        console.log(`Rate limited. Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }

      if (response.status >= 500) {
        const delay = Math.pow(2, attempt) * 1000;
        console.log(`Server error. Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }

      return response;
    } catch (error) {
      lastError = error as Error;
      if (attempt < maxRetries - 1) {
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError || new Error('Max retries exceeded');
}
```

---

### Attachment Size Exceeded

All providers have attachment size limits:
- Resend: 40 MB total
- SendGrid: 20 MB total
- Mailgun: 25 MB total
- SMTP2Go: 50 MB total

For large files, host externally:

```typescript
async function sendWithLargeFile(
  to: string,
  subject: string,
  html: string,
  file: File,
  env: Env
) {
  const MAX_SIZE = 20 * 1024 * 1024; // 20 MB for SendGrid

  if (file.size > MAX_SIZE) {
    // Upload to R2/S3
    const fileUrl = await env.R2.put(`files/${file.name}`, file);
    const signedUrl = await generateSignedUrl(fileUrl);

    // Send link instead
    html += `<p><a href="${signedUrl}">Download ${file.name}</a></p>`;
    return sendEmail(to, subject, html, env);
  }

  // Send with attachment
  const base64 = await fileToBase64(file);
  return sendEmailWithAttachment(to, subject, html, base64, file.name, env);
}
```

---

## Debugging Tips

### Enable Verbose Logging

```typescript
async function sendEmailWithLogging(email: any, env: Env) {
  console.log('Sending email:', JSON.stringify(email, null, 2));

  const response = await fetch(endpoint, {
    method: 'POST',
    headers,
    body: JSON.stringify(email),
  });

  console.log('Response status:', response.status);
  console.log('Response headers:', Object.fromEntries(response.headers.entries()));

  const body = await response.text();
  console.log('Response body:', body);

  return response;
}
```

---

### Test in Development

Use provider test modes:

**Resend**: Use test API key (starts with `re_test_`)
**SendGrid**: Use Sandbox Mode (set `mail_settings.sandbox_mode.enable: true`)
**Mailgun**: Send to `@sandbox[domain].mailgun.org`
**SMTP2Go**: Use test mode in dashboard

---

### Monitor Error Rates

Track errors in D1:

```typescript
await env.DB.prepare(`
  INSERT INTO email_errors (provider, error_code, error_message, timestamp)
  VALUES (?, ?, ?, ?)
`).bind(provider, error.code, error.message, Date.now()).run();
```

Alert when error rate exceeds threshold.

---

## Summary

- **Verify domains** before production
- **Validate email addresses** before sending
- **Implement exponential backoff** for retries
- **Monitor error rates** and alert on anomalies
- **Handle provider-specific quirks** (e.g., SMTP2Go angle brackets)
- **Use test modes** during development
- **Log verbosely** for debugging
