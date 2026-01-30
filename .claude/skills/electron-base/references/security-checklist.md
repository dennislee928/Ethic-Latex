# Electron Security Checklist

Use this checklist before releasing your Electron application.

## Required Security Settings

### Web Preferences

- [ ] `contextIsolation: true` - Isolates preload script from renderer
- [ ] `nodeIntegration: false` - No Node.js APIs in renderer
- [ ] `sandbox: true` (if possible) - Additional process isolation

```typescript
webPreferences: {
  preload: join(__dirname, 'preload.cjs'),
  contextIsolation: true,
  nodeIntegration: false,
  sandbox: true, // Disable only if native modules require it
}
```

### If Sandbox Must Be Disabled

Document why and what native modules require it:

```typescript
webPreferences: {
  sandbox: false, // Required for better-sqlite3 - see security-checklist.md
}
```

**Modules requiring sandbox: false:**
- better-sqlite3
- node-pty
- native-keymap
- Any module with native (.node) bindings

## Encryption and Secrets

- [ ] No hardcoded encryption keys
- [ ] No secrets in source code
- [ ] Encryption keys derived from machine ID

```typescript
// WRONG
const store = new Store({
  encryptionKey: 'my-secret-key',
});

// CORRECT
import { machineIdSync } from 'node-machine-id';

const store = new Store({
  encryptionKey: machineIdSync().slice(0, 32),
});
```

## OAuth and Authentication

- [ ] CSRF protection via state parameter
- [ ] State stored persistently (not in memory)
- [ ] State validated on callback
- [ ] Token expiration handled
- [ ] Refresh token flow implemented (if applicable)

```typescript
// Generate state
const state = crypto.randomUUID();
store.set('pendingState', state);

// Validate on callback
if (state !== store.get('pendingState')) {
  throw new Error('State mismatch - possible CSRF attack');
}
```

## IPC Security

- [ ] No sensitive data in IPC channel names
- [ ] Input validation on all IPC handlers
- [ ] No arbitrary code execution from renderer
- [ ] Limited API surface exposed via contextBridge

```typescript
// CORRECT - specific, validated handlers
ipcMain.handle('auth:get-session', () => {
  // Return only what's needed
  const session = store.get('session');
  return session ? { user: session.user } : null;
});
```

**Never allow arbitrary code execution from renderer:**
- No handlers that execute arbitrary strings
- No file path traversal
- Validate all inputs

## External Links

- [ ] External URLs open in system browser
- [ ] No arbitrary URL navigation in BrowserWindow

```typescript
// Block navigation to external URLs
mainWindow.webContents.setWindowOpenHandler(({ url }) => {
  shell.openExternal(url);
  return { action: 'deny' };
});
```

## Content Security Policy

- [ ] CSP headers configured for production
- [ ] No inline scripts (unless nonce-based)
- [ ] Limited external resource loading

```typescript
// In production, set CSP via session
session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
  callback({
    responseHeaders: {
      ...details.responseHeaders,
      'Content-Security-Policy': [
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
      ],
    },
  });
});
```

## Error Handling

- [ ] No empty catch blocks
- [ ] Errors logged with context
- [ ] Sensitive errors not exposed to renderer
- [ ] Network errors vs auth errors distinguished

```typescript
// WRONG
try {
  await fetch(url);
} catch {
  // Silent failure
}

// CORRECT
try {
  await fetch(url);
} catch (err) {
  if (err instanceof TypeError) {
    console.error('[Network] Offline or DNS failure');
  } else {
    console.error('[Auth] Unexpected error:', err);
  }
  throw err;
}
```

## Build and Distribution

### macOS

- [ ] Hardened runtime enabled
- [ ] Code signed with valid certificate
- [ ] Notarized for distribution
- [ ] Entitlements minimized

```json
{
  "mac": {
    "hardenedRuntime": true,
    "gatekeeperAssess": false,
    "entitlements": "build/entitlements.mac.plist",
    "entitlementsInherit": "build/entitlements.mac.plist"
  }
}
```

### Windows

- [ ] Code signed with valid certificate
- [ ] No unnecessary permissions

### All Platforms

- [ ] Auto-update uses HTTPS
- [ ] Update signature verification enabled
- [ ] No development dependencies in production

## Development vs Production

- [ ] DevTools disabled in production
- [ ] Different URLs for dev/prod
- [ ] Environment detection correct

```typescript
const isDev = process.env.NODE_ENV !== 'production' || !app.isPackaged;

if (isDev) {
  mainWindow.loadURL('http://localhost:5173');
  mainWindow.webContents.openDevTools();
} else {
  mainWindow.loadFile(join(__dirname, '../dist/index.html'));
}
```

## Audit Commands

```bash
# Check for known vulnerabilities
npm audit

# Check Electron version for security updates
npx electron --version

# Check electron-builder version
npx electron-builder --version
```

## Security Resources

- [Electron Security Documentation](https://www.electronjs.org/docs/latest/tutorial/security)
- [Electron Security Checklist](https://www.electronjs.org/docs/latest/tutorial/security#checklist-security-recommendations)
- [CVE Database for Electron](https://www.cvedetails.com/vulnerability-list/vendor_id-18218/product_id-43011/Electron-Electron.html)
