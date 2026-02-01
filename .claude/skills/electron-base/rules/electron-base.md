# Electron Security and Pattern Corrections

## Encryption Key Derivation

Never hardcode encryption keys. Derive from machine identifier.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `encryptionKey: 'secret'` | `encryptionKey: machineIdSync().slice(0, 32)` |
| `encryptionKey: 'my-app-key'` | Machine-derived key |
| String literal encryption key | `node-machine-id` derivation |

```typescript
// WRONG - hardcoded key
const store = new Store({
  encryptionKey: 'flaredesk-secure-key',
});

// CORRECT - machine-derived
import { machineIdSync } from 'node-machine-id';

const store = new Store({
  encryptionKey: machineIdSync().slice(0, 32),
});
```

## Context Isolation

Always enable context isolation. Never disable it.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `contextIsolation: false` | `contextIsolation: true` |
| `nodeIntegration: true` | `nodeIntegration: false` with preload |
| Direct `ipcRenderer` in renderer | `contextBridge.exposeInMainWorld` |

```typescript
// WRONG - insecure
webPreferences: {
  contextIsolation: false,
  nodeIntegration: true,
}

// CORRECT - secure
webPreferences: {
  preload: join(__dirname, 'preload.cjs'),
  contextIsolation: true,
  nodeIntegration: false,
  sandbox: false, // Only if needed for native modules
}
```

## Error Handling

Never use empty catch blocks. Always log and distinguish error types.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `catch { }` | `catch (err) { console.error(err); throw err; }` |
| `catch {}` (empty) | Proper error logging and re-throw |
| Silent error swallowing | Distinguish network vs auth errors |

```typescript
// WRONG - masks failures
try {
  await fetch(url);
} catch {
  // Silent
}

// CORRECT - proper error handling
try {
  await fetch(url);
} catch (err) {
  if (err instanceof TypeError) {
    console.error('[Network] Offline:', err.message);
  } else {
    console.error('[Auth] Error:', err);
  }
  throw err;
}
```

## OAuth State Storage

Store OAuth state persistently, not in memory.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `let pendingState: string` | `store.set('pendingState', state)` |
| In-memory state storage | electron-store persistence |

```typescript
// WRONG - lost on restart
let pendingState: string | null = null;

// CORRECT - persisted
store.set('pendingState', state);
const pending = store.get('pendingState');
```

## Native Module Externalization

Always externalize Electron and native modules in Vite config.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Bundling better-sqlite3 | `external: ['better-sqlite3']` |
| Bundling electron | `external: ['electron', ...]` |

```typescript
// vite.config.ts
rollupOptions: {
  external: ['electron', 'better-sqlite3', 'electron-store'],
}
```

## Preload Script Format

Preload scripts must use CommonJS format for Electron compatibility.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Preload as ESM | Preload as CJS |
| `format: 'es'` for preload | `format: 'cjs'` for preload |

```typescript
// vite.config.ts - preload config
preload: {
  input: 'electron/preload.ts',
  vite: {
    build: {
      rollupOptions: {
        output: {
          format: 'cjs',
          entryFileNames: '[name].cjs',
        },
      },
    },
  },
},
```

## External Links

Open external links in system browser, never in Electron window.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `window.open(url)` | `shell.openExternal(url)` |
| Opening links in BrowserWindow | System browser via shell |

```typescript
// In main process
mainWindow.webContents.setWindowOpenHandler(({ url }) => {
  shell.openExternal(url);
  return { action: 'deny' };
});

// IPC handler for renderer
ipcMain.handle('app:open-external', (_event, url: string) => {
  shell.openExternal(url);
});
```

## Token Expiration

Implement token refresh or sliding sessions. Never hardcode expiration without refresh.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Hardcoded 30-day expiration | Expiration with refresh mechanism |
| No expiration handling | Check expiration with buffer |

```typescript
// Check with buffer before expiration
const session = store.get('session');
const expiresAt = new Date(session.expiresAt);
const bufferMs = 5 * 60 * 1000; // 5 minutes

if (Date.now() > expiresAt.getTime() - bufferMs) {
  await refreshToken(session.token);
}
```
