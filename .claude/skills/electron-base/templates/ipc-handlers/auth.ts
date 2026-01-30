/**
 * OAuth Authentication IPC Handler
 *
 * Handles OAuth flow with:
 * - Machine-derived encryption (NOT hardcoded keys)
 * - CSRF protection via state parameter
 * - Proper error handling (no empty catch blocks)
 * - Token expiration with refresh capability
 */

import { ipcMain, shell } from 'electron';
import Store from 'electron-store';
import { machineIdSync } from 'node-machine-id';

// ============================================================================
// CONFIGURATION - Update for your app
// ============================================================================

const BACKEND_URL = 'https://your-api.example.com';

// ============================================================================
// TYPES
// ============================================================================

export interface Session {
  user: {
    id: string;
    email: string;
    name: string | null;
    image: string | null;
  };
  token: string;
  expiresAt: string;
  refreshToken?: string;
}

interface AuthStore {
  session: Session | null;
  pendingState: string | null;
}

// ============================================================================
// SECURE STORE
// ============================================================================

// IMPORTANT: Derive encryption key from machine ID, NEVER hardcode
const store = new Store<AuthStore>({
  name: 'app-auth',
  encryptionKey: machineIdSync().slice(0, 32), // Machine-unique 32-char key
  defaults: {
    session: null,
    pendingState: null,
  },
});

// ============================================================================
// IPC HANDLERS
// ============================================================================

export function setupAuth() {
  // Start OAuth flow
  ipcMain.handle(
    'auth:start-oauth',
    async (_event, provider: 'google' | 'github') => {
      console.log('[OAuth] Starting flow for:', provider);

      // Generate cryptographically secure state for CSRF protection
      const state = crypto.randomUUID();
      store.set('pendingState', state);

      // Open system browser for OAuth
      const authUrl = `${BACKEND_URL}/api/auth/signin/${provider}?state=${state}`;

      try {
        await shell.openExternal(authUrl);
        console.log('[OAuth] Browser opened successfully');
      } catch (err) {
        console.error('[OAuth] Failed to open browser:', err);
        throw err;
      }
    }
  );

  // Get current session
  ipcMain.handle('auth:get-session', async () => {
    const session = store.get('session');
    if (!session) return null;

    // Check if session is expired (with 5-minute buffer)
    const expiresAt = new Date(session.expiresAt);
    const bufferMs = 5 * 60 * 1000;

    if (Date.now() > expiresAt.getTime() - bufferMs) {
      // Try to refresh if we have a refresh token
      if (session.refreshToken) {
        try {
          const refreshed = await refreshSession(session.refreshToken);
          return refreshed;
        } catch (err) {
          console.error('[Auth] Token refresh failed:', err);
          store.set('session', null);
          return null;
        }
      }

      // No refresh token, session expired
      store.set('session', null);
      return null;
    }

    // Verify session with backend (if online)
    try {
      const response = await fetch(`${BACKEND_URL}/api/me`, {
        headers: {
          Authorization: `Bearer ${session.token}`,
        },
      });

      if (!response.ok) {
        console.warn('[Auth] Session invalid, clearing');
        store.set('session', null);
        return null;
      }

      return session;
    } catch (err) {
      // Network error - return cached session for offline use
      if (err instanceof TypeError) {
        console.log('[Auth] Offline, using cached session');
        return session;
      }

      console.error('[Auth] Unexpected error verifying session:', err);
      throw err;
    }
  });

  // Logout
  ipcMain.handle('auth:logout', async () => {
    const session = store.get('session');

    if (session) {
      try {
        await fetch(`${BACKEND_URL}/api/auth/signout`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${session.token}`,
          },
        });
      } catch (err) {
        // Log but don't throw - clear local session regardless
        if (err instanceof TypeError) {
          console.log('[Auth] Offline during logout, clearing local session');
        } else {
          console.error('[Auth] Logout request failed:', err);
        }
      }
    }

    store.set('session', null);
    store.set('pendingState', null);
  });
}

// ============================================================================
// OAUTH CALLBACK HANDLER
// ============================================================================

export async function handleAuthCallback(
  token: string,
  state: string
): Promise<Session> {
  const pendingState = store.get('pendingState');

  // CSRF protection - validate state matches
  if (state !== pendingState) {
    throw new Error('State mismatch - possible CSRF attack');
  }

  // Clear pending state immediately
  store.set('pendingState', null);

  // Get user info using the token
  const response = await fetch(`${BACKEND_URL}/api/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to get user info: ${response.status} ${errorText}`);
  }

  const { user, refreshToken } = await response.json();

  // Create session with reasonable expiration
  const session: Session = {
    user,
    token,
    expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days
    refreshToken, // Store refresh token if provided
  };

  store.set('session', session);

  return session;
}

// ============================================================================
// TOKEN REFRESH
// ============================================================================

async function refreshSession(refreshToken: string): Promise<Session> {
  const response = await fetch(`${BACKEND_URL}/api/auth/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refreshToken }),
  });

  if (!response.ok) {
    throw new Error(`Token refresh failed: ${response.status}`);
  }

  const { token, user, refreshToken: newRefreshToken, expiresIn } =
    await response.json();

  const session: Session = {
    user,
    token,
    expiresAt: new Date(Date.now() + expiresIn * 1000).toISOString(),
    refreshToken: newRefreshToken || refreshToken,
  };

  store.set('session', session);

  return session;
}

// ============================================================================
// UTILITY EXPORTS
// ============================================================================

export function getStoredSession(): Session | null {
  return store.get('session');
}

export function getSessionToken(): string | null {
  const session = store.get('session');
  return session?.token || null;
}
