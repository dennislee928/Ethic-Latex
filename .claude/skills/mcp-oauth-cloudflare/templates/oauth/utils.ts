/**
 * OAuth utility functions for Google OAuth
 *
 * These utilities handle:
 * - Constructing Google authorization URLs
 * - Exchanging auth codes for access tokens
 * - Fetching user info from Google
 */

// Context from the auth process, encrypted & stored in the auth token
// and provided to the DurableMCP as this.props
export type Props = {
  id: string;      // Google user ID
  email: string;   // User's email
  name: string;    // User's display name
  picture?: string; // Profile picture URL
  accessToken: string; // Google access token (for Google API calls)
  refreshToken?: string; // Google refresh token (for long-lived access)
};

/**
 * Constructs an authorization URL for Google OAuth
 *
 * @param upstream_url - Google's authorization endpoint
 * @param client_id - Your Google OAuth client ID
 * @param scope - OAuth scopes (e.g., 'openid email profile')
 * @param redirect_uri - Your callback URL
 * @param state - OAuth state token for CSRF protection
 */
export function getUpstreamAuthorizeUrl({
  upstream_url,
  client_id,
  scope,
  redirect_uri,
  state,
}: {
  upstream_url: string;
  client_id: string;
  scope: string;
  redirect_uri: string;
  state?: string;
}) {
  const upstream = new URL(upstream_url);
  upstream.searchParams.set('client_id', client_id);
  upstream.searchParams.set('redirect_uri', redirect_uri);
  upstream.searchParams.set('scope', scope);
  if (state) upstream.searchParams.set('state', state);
  upstream.searchParams.set('response_type', 'code');
  upstream.searchParams.set('access_type', 'offline'); // For refresh tokens
  upstream.searchParams.set('prompt', 'consent'); // Always show consent screen
  return upstream.href;
}

/**
 * Token response from Google OAuth
 */
export type TokenResponse = {
  accessToken: string;
  refreshToken?: string; // Only returned on first authorization with access_type=offline
};

/**
 * Fetches an authorization token from Google
 *
 * @returns Tuple of [TokenResponse, null] on success or [null, Response] on error
 *
 * Note: refresh_token is only returned on first authorization when access_type=offline.
 * Subsequent authorizations won't include it unless the user revokes access and reauthorizes.
 */
export async function fetchUpstreamAuthToken({
  client_id,
  client_secret,
  code,
  redirect_uri,
  upstream_url,
}: {
  code: string | undefined;
  upstream_url: string;
  client_secret: string;
  redirect_uri: string;
  client_id: string;
}): Promise<[TokenResponse, null] | [null, Response]> {
  if (!code) {
    return [null, new Response('Missing code', { status: 400 })];
  }

  const resp = await fetch(upstream_url, {
    body: new URLSearchParams({
      client_id,
      client_secret,
      code,
      redirect_uri,
      grant_type: 'authorization_code',
    }).toString(),
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    method: 'POST',
  });

  if (!resp.ok) {
    const errorText = await resp.text();
    console.error('Google token exchange failed:', errorText);
    return [null, new Response('Failed to fetch access token', { status: 500 })];
  }

  const body = await resp.json() as {
    access_token?: string;
    refresh_token?: string;
    error?: string;
  };

  if (body.error) {
    console.error('Google OAuth error:', body.error);
    return [null, new Response(`OAuth error: ${body.error}`, { status: 400 })];
  }

  const accessToken = body.access_token;
  if (!accessToken) {
    return [null, new Response('Missing access token', { status: 400 })];
  }

  return [{
    accessToken,
    refreshToken: body.refresh_token, // May be undefined for subsequent auths
  }, null];
}

/**
 * Fetches user info from Google
 *
 * @param accessToken - Google access token
 * @returns User object with id, email, name, picture or null on error
 */
export async function fetchGoogleUserInfo(accessToken: string): Promise<{
  id: string;
  email: string;
  name: string;
  picture?: string;
} | null> {
  const resp = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!resp.ok) {
    console.error('Failed to fetch Google user info:', await resp.text());
    return null;
  }

  const user = await resp.json() as {
    id: string;
    email: string;
    name: string;
    picture?: string;
  };

  return user;
}
