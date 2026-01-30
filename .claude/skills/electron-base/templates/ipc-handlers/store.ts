/**
 * Persistent Storage IPC Handler
 *
 * Provides encrypted storage for app settings and data using electron-store.
 * Uses machine-derived encryption key for security.
 */

import { ipcMain } from 'electron';
import Store from 'electron-store';
import { machineIdSync } from 'node-machine-id';

// ============================================================================
// TYPES
// ============================================================================

export interface Settings {
  theme: 'light' | 'dark' | 'system';
  // Add your app-specific settings here
}

interface AppStore {
  settings: Settings;
  // Add other persisted data types here
  [key: string]: unknown;
}

// ============================================================================
// STORE INITIALIZATION
// ============================================================================

// IMPORTANT: Derive encryption key from machine ID, NEVER hardcode
const store = new Store<AppStore>({
  name: 'app-data',
  encryptionKey: machineIdSync().slice(0, 32), // Machine-unique 32-char key
  defaults: {
    settings: {
      theme: 'system',
    },
  },
  // Optional: Clear storage on corrupted JSON
  clearInvalidConfig: true,
});

// ============================================================================
// IPC HANDLERS
// ============================================================================

export function setupStore() {
  // Generic get
  ipcMain.handle('store:get', (_event, key: string) => {
    return store.get(key);
  });

  // Generic set
  ipcMain.handle('store:set', (_event, key: string, value: unknown) => {
    store.set(key, value);
  });

  // Generic delete
  ipcMain.handle('store:delete', (_event, key: string) => {
    store.delete(key as keyof AppStore);
  });

  // Get settings (typed)
  ipcMain.handle('store:get-settings', () => {
    return store.get('settings');
  });

  // Update settings (partial update)
  ipcMain.handle('store:update-settings', (_event, updates: Partial<Settings>) => {
    const current = store.get('settings');
    store.set('settings', { ...current, ...updates });
  });
}

// ============================================================================
// UTILITY EXPORTS (for use in main process)
// ============================================================================

export function getSettings(): Settings {
  return store.get('settings');
}

export function updateSettings(updates: Partial<Settings>): void {
  const current = store.get('settings');
  store.set('settings', { ...current, ...updates });
}

export function getValue<T>(key: string): T | undefined {
  return store.get(key) as T | undefined;
}

export function setValue<T>(key: string, value: T): void {
  store.set(key, value);
}

export function deleteValue(key: string): void {
  store.delete(key as keyof AppStore);
}

// Export store instance for advanced use cases
export { store };
