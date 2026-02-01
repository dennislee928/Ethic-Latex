# Electron Base Skill

Production patterns for building secure desktop applications with Electron 33, Vite, React, and TypeScript.

## When to Use

This skill provides guidance for:

- Setting up Electron with Vite and React
- Implementing type-safe IPC via contextBridge
- OAuth authentication with custom protocol handlers
- Native module integration (better-sqlite3, electron-store)
- Packaging with electron-builder

## Auto-Trigger Keywords

### Technologies
- electron
- electron-builder
- electron-store
- vite-plugin-electron
- contextBridge
- preload script
- desktop app
- cross-platform desktop
- native desktop app

### Patterns
- IPC main renderer
- main process
- renderer process
- custom protocol handler
- deep linking electron
- electron OAuth
- electron authentication

### Error Messages
- NODE_MODULE_VERSION mismatch
- Cannot read properties of undefined (reading 'invoke')
- contextBridge is not defined
- State mismatch - possible CSRF attack
- Module did not self-register
- electron-rebuild
- sandbox native module

## Key Features

- **Security-First**: Context isolation, no node integration, machine-derived encryption
- **Type-Safe IPC**: Full TypeScript interface for main/renderer communication
- **OAuth Patterns**: Custom protocol handlers with CSRF protection
- **Native Modules**: Compatibility guidance for better-sqlite3, electron-store
- **Build Ready**: electron-builder configuration with code signing

## Prevents Common Errors

1. Hardcoded encryption keys in electron-store
2. NODE_MODULE_VERSION mismatches
3. Context isolation bypasses
4. OAuth state validation failures
5. Sandbox conflicts with native modules
6. Empty catch blocks masking auth failures
7. Dual auth system maintenance burden
8. Token expiration without refresh

## Templates Included

- `main.ts` - Main process with protocol handlers
- `preload.ts` - Type-safe contextBridge implementation
- `vite.config.ts` - Dual-entry Vite configuration
- `electron-builder.json` - Cross-platform packaging
- `ipc-handlers/auth.ts` - Secure OAuth handler
- `ipc-handlers/store.ts` - electron-store setup

## Dependencies

```
electron@^33.0.0
electron-builder@^25.0.0
electron-store@^10.0.0
vite-plugin-electron@^0.28.0
node-machine-id@^1.1.12 (optional)
better-sqlite3@^11.0.0 (optional)
```
