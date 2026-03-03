/**
 * OAuth Security Utilities for Cloudflare Workers
 *
 * Features:
 * - CSRF protection with HttpOnly cookies
 * - OAuth state management with KV storage
 * - Session binding to prevent token theft
 * - Client approval caching (30-day TTL)
 * - Beautiful approval dialog UI
 *
 * Based on Cloudflare's official OAuth patterns
 */

import type { AuthRequest, ClientInfo } from '@cloudflare/workers-oauth-provider';

/**
 * OAuth 2.1 compliant error class
 */
export class OAuthError extends Error {
  constructor(
    public code: string,
    public description: string,
    public statusCode = 400
  ) {
    super(description);
    this.name = 'OAuthError';
  }

  toResponse(): Response {
    return new Response(
      JSON.stringify({
        error: this.code,
        error_description: this.description,
      }),
      {
        status: this.statusCode,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}

export interface OAuthStateResult {
  stateToken: string;
}

export interface ValidateStateResult {
  oauthReqInfo: AuthRequest;
  clearCookie: string;
}

export interface BindStateResult {
  setCookie: string;
}

export interface CSRFProtectionResult {
  token: string;
  setCookie: string;
}

export interface ValidateCSRFResult {
  clearCookie: string;
}

// ===== Sanitization =====

/**
 * Sanitizes text content for safe display in HTML
 */
export function sanitizeText(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Validates a URL for security - whitelist only http/https
 */
export function sanitizeUrl(url: string): string {
  const normalized = url.trim();
  if (normalized.length === 0) return '';

  // Check for control characters
  for (let i = 0; i < normalized.length; i++) {
    const code = normalized.charCodeAt(i);
    if ((code >= 0x00 && code <= 0x1f) || (code >= 0x7f && code <= 0x9f)) {
      return '';
    }
  }

  let parsedUrl: URL;
  try {
    parsedUrl = new URL(normalized);
  } catch {
    return '';
  }

  const allowedSchemes = ['https', 'http'];
  const scheme = parsedUrl.protocol.slice(0, -1).toLowerCase();
  if (!allowedSchemes.includes(scheme)) {
    return '';
  }

  return normalized;
}

// ===== CSRF Protection =====

/**
 * Generates CSRF token and cookie
 * - HttpOnly: JavaScript can't access
 * - Secure: HTTPS only
 * - SameSite=Lax: Prevents cross-site requests
 * - 10-minute expiration
 */
export function generateCSRFProtection(): CSRFProtectionResult {
  const csrfCookieName = '__Host-CSRF_TOKEN';
  const token = crypto.randomUUID();
  const setCookie = `${csrfCookieName}=${token}; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=600`;
  return { token, setCookie };
}

/**
 * Validates CSRF token from form matches cookie
 */
export function validateCSRFToken(formData: FormData, request: Request): ValidateCSRFResult {
  const csrfCookieName = '__Host-CSRF_TOKEN';
  const tokenFromForm = formData.get('csrf_token');

  if (!tokenFromForm || typeof tokenFromForm !== 'string') {
    throw new OAuthError('invalid_request', 'Missing CSRF token in form data', 400);
  }

  const cookieHeader = request.headers.get('Cookie') || '';
  const cookies = cookieHeader.split(';').map((c) => c.trim());
  const csrfCookie = cookies.find((c) => c.startsWith(`${csrfCookieName}=`));
  const tokenFromCookie = csrfCookie ? csrfCookie.substring(csrfCookieName.length + 1) : null;

  if (!tokenFromCookie) {
    throw new OAuthError('invalid_request', 'Missing CSRF token cookie', 400);
  }

  if (tokenFromForm !== tokenFromCookie) {
    throw new OAuthError('invalid_request', 'CSRF token mismatch', 400);
  }

  const clearCookie = `${csrfCookieName}=; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=0`;
  return { clearCookie };
}

// ===== OAuth State Management =====

/**
 * Creates and stores OAuth state information in KV
 * - One-time use (deleted after validation)
 * - 10-minute TTL by default
 */
export async function createOAuthState(
  oauthReqInfo: AuthRequest,
  kv: KVNamespace,
  stateTTL = 600
): Promise<OAuthStateResult> {
  const stateToken = crypto.randomUUID();
  await kv.put(`oauth:state:${stateToken}`, JSON.stringify(oauthReqInfo), {
    expirationTtl: stateTTL,
  });
  return { stateToken };
}

/**
 * Binds OAuth state token to user's browser session
 * - SHA-256 hash prevents tampering
 * - Cookie ensures same browser completes flow
 */
export async function bindStateToSession(stateToken: string): Promise<BindStateResult> {
  const consentedStateCookieName = '__Host-CONSENTED_STATE';

  const encoder = new TextEncoder();
  const data = encoder.encode(stateToken);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');

  const setCookie = `${consentedStateCookieName}=${hashHex}; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=600`;
  return { setCookie };
}

/**
 * Validates OAuth state from the request
 * - Checks state exists in KV
 * - Validates session binding cookie matches
 * - Deletes state after use (one-time)
 */
export async function validateOAuthState(
  request: Request,
  kv: KVNamespace
): Promise<ValidateStateResult> {
  const consentedStateCookieName = '__Host-CONSENTED_STATE';
  const url = new URL(request.url);
  const stateFromQuery = url.searchParams.get('state');

  if (!stateFromQuery) {
    throw new OAuthError('invalid_request', 'Missing state parameter', 400);
  }

  const storedDataJson = await kv.get(`oauth:state:${stateFromQuery}`);
  if (!storedDataJson) {
    throw new OAuthError('invalid_request', 'Invalid or expired state', 400);
  }

  // Validate session binding
  const cookieHeader = request.headers.get('Cookie') || '';
  const cookies = cookieHeader.split(';').map((c) => c.trim());
  const consentedStateCookie = cookies.find((c) => c.startsWith(`${consentedStateCookieName}=`));
  const consentedStateHash = consentedStateCookie
    ? consentedStateCookie.substring(consentedStateCookieName.length + 1)
    : null;

  if (!consentedStateHash) {
    throw new OAuthError(
      'invalid_request',
      'Missing session binding cookie - authorization flow must be restarted',
      400
    );
  }

  // Hash and compare
  const encoder = new TextEncoder();
  const data = encoder.encode(stateFromQuery);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const stateHash = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');

  if (stateHash !== consentedStateHash) {
    throw new OAuthError(
      'invalid_request',
      'State token does not match session - possible CSRF attack detected',
      400
    );
  }

  let oauthReqInfo: AuthRequest;
  try {
    oauthReqInfo = JSON.parse(storedDataJson) as AuthRequest;
  } catch {
    throw new OAuthError('server_error', 'Invalid state data', 500);
  }

  // Delete state (one-time use only!)
  await kv.delete(`oauth:state:${stateFromQuery}`);

  const clearCookie = `${consentedStateCookieName}=; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=0`;
  return { oauthReqInfo, clearCookie };
}

// ===== Client Approval Caching =====

/**
 * Checks if a client has been previously approved
 */
export async function isClientApproved(
  request: Request,
  clientId: string,
  cookieSecret: string
): Promise<boolean> {
  const approvedClients = await getApprovedClientsFromCookie(request, cookieSecret);
  return approvedClients?.includes(clientId) ?? false;
}

/**
 * Adds a client to approved list
 * - HMAC-signed to prevent tampering
 * - 30-day TTL (users won't re-approve frequently)
 */
export async function addApprovedClient(
  request: Request,
  clientId: string,
  cookieSecret: string
): Promise<string> {
  const approvedClientsCookieName = '__Host-APPROVED_CLIENTS';
  const THIRTY_DAYS_IN_SECONDS = 2592000;

  const existingApprovedClients = (await getApprovedClientsFromCookie(request, cookieSecret)) || [];
  const updatedApprovedClients = Array.from(new Set([...existingApprovedClients, clientId]));

  const payload = JSON.stringify(updatedApprovedClients);
  const signature = await signData(payload, cookieSecret);
  const cookieValue = `${signature}.${btoa(payload)}`;

  return `${approvedClientsCookieName}=${cookieValue}; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=${THIRTY_DAYS_IN_SECONDS}`;
}

// ===== Approval Dialog =====

export interface ApprovalDialogOptions {
  client: ClientInfo | null;
  server: {
    name: string;
    logo?: string;
    description?: string;
  };
  state: Record<string, any>;
  csrfToken: string;
  setCookie: string;
}

/**
 * Renders OAuth approval dialog
 * TEMPLATE: Customize the colors and styling as needed
 */
export function renderApprovalDialog(request: Request, options: ApprovalDialogOptions): Response {
  const { client, server, state, csrfToken, setCookie } = options;

  const encodedState = btoa(JSON.stringify(state));
  const serverName = sanitizeText(server.name);
  const clientName = client?.clientName ? sanitizeText(client.clientName) : 'Unknown MCP Client';
  const serverDescription = server.description ? sanitizeText(server.description) : '';

  const logoUrl = server.logo ? sanitizeText(sanitizeUrl(server.logo)) : '';
  const clientUri = client?.clientUri ? sanitizeText(sanitizeUrl(client.clientUri)) : '';

  const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${clientName} | Authorization Request</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    :root {
      --background: #09090b;
      --foreground: #fafafa;
      --card: #18181b;
      --card-foreground: #fafafa;
      --muted: #27272a;
      --muted-foreground: #a1a1aa;
      --border: #27272a;
      --primary: #3b82f6;
      --primary-foreground: #fafafa;
      --secondary: #27272a;
      --secondary-foreground: #fafafa;
      --accent: #7c3aed;
      --radius: 0.75rem;
    }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      line-height: 1.6;
      color: var(--foreground);
      background: var(--background);
      margin: 0;
      padding: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
    }

    body::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background:
        radial-gradient(ellipse at 20% 20%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(124, 58, 237, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(16, 185, 129, 0.05) 0%, transparent 70%);
      pointer-events: none;
    }

    body::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-image:
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
      background-size: 64px 64px;
      pointer-events: none;
    }

    .container {
      max-width: 420px;
      width: 100%;
      margin: 1.5rem;
      position: relative;
      z-index: 1;
    }

    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 2rem;
      box-shadow:
        0 0 0 1px rgba(255,255,255,0.05),
        0 20px 50px -12px rgba(0,0,0,0.5),
        0 0 100px -20px rgba(59, 130, 246, 0.2);
    }

    .header {
      text-align: center;
      margin-bottom: 1.5rem;
    }

    .logo-container {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 56px;
      height: 56px;
      border-radius: 12px;
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
      margin-bottom: 1rem;
      box-shadow: 0 0 30px -5px rgba(59, 130, 246, 0.5);
    }

    .logo {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      object-fit: cover;
    }

    .logo-fallback {
      font-size: 1.5rem;
      font-weight: 600;
      color: white;
    }

    .title {
      font-size: 1.25rem;
      font-weight: 600;
      color: var(--foreground);
      margin-bottom: 0.25rem;
      letter-spacing: -0.02em;
    }

    .description {
      color: var(--muted-foreground);
      font-size: 0.875rem;
    }

    .divider {
      height: 1px;
      background: var(--border);
      margin: 1.5rem 0;
    }

    .request-card {
      background: var(--muted);
      border: 1px solid var(--border);
      border-radius: calc(var(--radius) - 2px);
      padding: 1rem;
      margin-bottom: 1rem;
    }

    .request-header {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 0.75rem;
    }

    .client-avatar {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      font-size: 0.875rem;
      color: white;
    }

    .client-info {
      flex: 1;
    }

    .client-name {
      font-weight: 600;
      color: var(--foreground);
      font-size: 0.9375rem;
    }

    .client-uri {
      color: var(--muted-foreground);
      font-size: 0.75rem;
    }

    .request-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.375rem;
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.2);
      color: #60a5fa;
      font-size: 0.75rem;
      font-weight: 500;
      padding: 0.25rem 0.625rem;
      border-radius: 9999px;
    }

    .request-badge svg {
      width: 12px;
      height: 12px;
    }

    .permissions {
      font-size: 0.8125rem;
      color: var(--muted-foreground);
      line-height: 1.5;
    }

    .permissions strong {
      color: var(--foreground);
      font-weight: 500;
    }

    .actions {
      display: flex;
      gap: 0.75rem;
      margin-top: 1.5rem;
    }

    .button {
      flex: 1;
      padding: 0.625rem 1.25rem;
      border-radius: calc(var(--radius) - 2px);
      font-weight: 500;
      font-size: 0.875rem;
      cursor: pointer;
      border: none;
      transition: all 0.15s ease;
      font-family: inherit;
    }

    .button-secondary {
      background: var(--secondary);
      color: var(--secondary-foreground);
      border: 1px solid var(--border);
    }

    .button-secondary:hover {
      background: #3f3f46;
      border-color: #3f3f46;
    }

    .button-primary {
      background: var(--primary);
      color: var(--primary-foreground);
      box-shadow: 0 0 20px -5px rgba(59, 130, 246, 0.5);
    }

    .button-primary:hover {
      background: #2563eb;
      box-shadow: 0 0 25px -5px rgba(59, 130, 246, 0.6);
      transform: translateY(-1px);
    }

    .footer {
      text-align: center;
      margin-top: 1.5rem;
      padding-top: 1rem;
      border-top: 1px solid var(--border);
    }

    .footer-text {
      font-size: 0.75rem;
      color: var(--muted-foreground);
    }

    .footer-text a {
      color: var(--primary);
      text-decoration: none;
    }

    .footer-text a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <div class="header">
        ${logoUrl
          ? '<img src="' + logoUrl + '" alt="' + serverName + '" class="logo">'
          : '<div class="logo-container"><span class="logo-fallback">' + serverName.charAt(0) + '</span></div>'
        }
        <h1 class="title">${serverName}</h1>
        ${serverDescription ? '<p class="description">' + serverDescription + '</p>' : ''}
      </div>

      <div class="request-card">
        <div class="request-header">
          <div class="client-avatar">${clientName.charAt(0)}</div>
          <div class="client-info">
            <div class="client-name">${clientName}</div>
            ${clientUri ? '<div class="client-uri">' + clientUri + '</div>' : ''}
          </div>
        </div>
        <span class="request-badge">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>
          </svg>
          Requesting access
        </span>
      </div>

      <p class="permissions">
        This will allow <strong>${clientName}</strong> to access your MCP server tools and resources.
      </p>

      <form method="post" action="${new URL(request.url).pathname}">
        <input type="hidden" name="state" value="${encodedState}">
        <input type="hidden" name="csrf_token" value="${csrfToken}">

        <div class="actions">
          <button type="button" class="button button-secondary" onclick="window.history.back()">Cancel</button>
          <button type="submit" class="button button-primary">Approve</button>
        </div>
      </form>

      <div class="footer">
        <p class="footer-text">Secured by OAuth 2.0 with Google</p>
      </div>
    </div>
  </div>
</body>
</html>
  `;

  return new Response(htmlContent, {
    headers: {
      'Content-Security-Policy': "frame-ancestors 'none'",
      'Content-Type': 'text/html; charset=utf-8',
      'Set-Cookie': setCookie,
      'X-Frame-Options': 'DENY',
    },
  });
}

// ===== Helper Functions =====

async function getApprovedClientsFromCookie(
  request: Request,
  cookieSecret: string
): Promise<string[] | null> {
  const approvedClientsCookieName = '__Host-APPROVED_CLIENTS';

  const cookieHeader = request.headers.get('Cookie');
  if (!cookieHeader) return null;

  const cookies = cookieHeader.split(';').map((c) => c.trim());
  const targetCookie = cookies.find((c) => c.startsWith(`${approvedClientsCookieName}=`));

  if (!targetCookie) return null;

  const cookieValue = targetCookie.substring(approvedClientsCookieName.length + 1);
  const parts = cookieValue.split('.');

  if (parts.length !== 2) return null;

  const [signatureHex, base64Payload] = parts;
  const payload = atob(base64Payload);

  const isValid = await verifySignature(signatureHex, payload, cookieSecret);
  if (!isValid) return null;

  try {
    const approvedClients = JSON.parse(payload);
    if (!Array.isArray(approvedClients) || !approvedClients.every((item) => typeof item === 'string')) {
      return null;
    }
    return approvedClients as string[];
  } catch {
    return null;
  }
}

async function signData(data: string, secret: string): Promise<string> {
  const key = await importKey(secret);
  const enc = new TextEncoder();
  const signatureBuffer = await crypto.subtle.sign('HMAC', key, enc.encode(data));
  return Array.from(new Uint8Array(signatureBuffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

async function verifySignature(signatureHex: string, data: string, secret: string): Promise<boolean> {
  const key = await importKey(secret);
  const enc = new TextEncoder();
  try {
    const signatureBytes = new Uint8Array(
      signatureHex.match(/.{1,2}/g)!.map((byte) => Number.parseInt(byte, 16))
    );
    return await crypto.subtle.verify('HMAC', key, signatureBytes.buffer, enc.encode(data));
  } catch {
    return false;
  }
}

async function importKey(secret: string): Promise<CryptoKey> {
  if (!secret) {
    throw new Error('cookieSecret is required for signing cookies');
  }
  const enc = new TextEncoder();
  return crypto.subtle.importKey('raw', enc.encode(secret), { hash: 'SHA-256', name: 'HMAC' }, false, [
    'sign',
    'verify',
  ]);
}
