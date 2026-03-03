/**
 * Google Workspace OAuth Worker Template
 *
 * Handles OAuth 2.0 flow for Google Workspace APIs.
 * Stores tokens in Cloudflare KV.
 */

interface Env {
  GOOGLE_CLIENT_ID: string
  GOOGLE_CLIENT_SECRET: string
  BASE_URL: string
  TOKENS: KVNamespace
}

interface TokenResponse {
  access_token: string
  refresh_token?: string
  expires_in: number
  token_type: string
  scope: string
}

interface StoredTokens {
  access_token: string
  refresh_token: string
  expires_at: number
}

// Configure scopes for your use case
const SCOPES = [
  'https://www.googleapis.com/auth/gmail.readonly',
  'https://www.googleapis.com/auth/calendar.readonly',
  // Add more scopes as needed
]

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url)

    switch (url.pathname) {
      case '/auth':
        return handleAuth(env)
      case '/callback':
        return handleCallback(request, env)
      case '/api/example':
        return handleApiCall(request, env)
      default:
        return new Response('Not found', { status: 404 })
    }
  },
}

function handleAuth(env: Env): Response {
  const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth')
  authUrl.searchParams.set('client_id', env.GOOGLE_CLIENT_ID)
  authUrl.searchParams.set('redirect_uri', `${env.BASE_URL}/callback`)
  authUrl.searchParams.set('response_type', 'code')
  authUrl.searchParams.set('scope', SCOPES.join(' '))
  authUrl.searchParams.set('access_type', 'offline')
  authUrl.searchParams.set('prompt', 'consent')

  return Response.redirect(authUrl.toString(), 302)
}

async function handleCallback(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url)
  const code = url.searchParams.get('code')
  const error = url.searchParams.get('error')

  if (error) {
    return new Response(`OAuth error: ${error}`, { status: 400 })
  }

  if (!code) {
    return new Response('Missing code parameter', { status: 400 })
  }

  // Exchange code for tokens
  const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      code,
      client_id: env.GOOGLE_CLIENT_ID,
      client_secret: env.GOOGLE_CLIENT_SECRET,
      redirect_uri: `${env.BASE_URL}/callback`,
      grant_type: 'authorization_code',
    }),
  })

  if (!tokenResponse.ok) {
    const error = await tokenResponse.text()
    return new Response(`Token exchange failed: ${error}`, { status: 400 })
  }

  const tokens: TokenResponse = await tokenResponse.json()

  // Get user info to use as key
  const userResponse = await fetch(
    'https://www.googleapis.com/oauth2/v2/userinfo',
    { headers: { Authorization: `Bearer ${tokens.access_token}` } }
  )
  const user = await userResponse.json()

  // Store tokens
  const storedTokens: StoredTokens = {
    access_token: tokens.access_token,
    refresh_token: tokens.refresh_token!,
    expires_at: Date.now() + tokens.expires_in * 1000,
  }
  await env.TOKENS.put(`user:${user.id}`, JSON.stringify(storedTokens))

  return new Response(`Authenticated as ${user.email}`, { status: 200 })
}

async function getValidToken(userId: string, env: Env): Promise<string> {
  const stored = await env.TOKENS.get(`user:${userId}`)
  if (!stored) {
    throw new Error('No tokens found - user must authenticate')
  }

  const tokens: StoredTokens = JSON.parse(stored)

  // Check if token is expired (with 5 min buffer)
  if (Date.now() > tokens.expires_at - 300000) {
    // Refresh the token
    const refreshResponse = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        refresh_token: tokens.refresh_token,
        client_id: env.GOOGLE_CLIENT_ID,
        client_secret: env.GOOGLE_CLIENT_SECRET,
        grant_type: 'refresh_token',
      }),
    })

    if (!refreshResponse.ok) {
      throw new Error('Token refresh failed - user must re-authenticate')
    }

    const newTokens: TokenResponse = await refreshResponse.json()

    // Update stored tokens
    tokens.access_token = newTokens.access_token
    tokens.expires_at = Date.now() + newTokens.expires_in * 1000
    if (newTokens.refresh_token) {
      tokens.refresh_token = newTokens.refresh_token
    }

    await env.TOKENS.put(`user:${userId}`, JSON.stringify(tokens))
  }

  return tokens.access_token
}

async function handleApiCall(request: Request, env: Env): Promise<Response> {
  // Get user ID from session/header (implement your auth)
  const userId = 'user-id-here'

  try {
    const accessToken = await getValidToken(userId, env)

    // Example: List Gmail labels
    const response = await fetch(
      'https://gmail.googleapis.com/gmail/v1/users/me/labels',
      { headers: { Authorization: `Bearer ${accessToken}` } }
    )

    return new Response(await response.text(), {
      headers: { 'Content-Type': 'application/json' },
    })
  } catch (error: any) {
    return new Response(error.message, { status: 401 })
  }
}
