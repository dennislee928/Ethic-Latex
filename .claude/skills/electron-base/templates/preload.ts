/**
 * Electron Preload Script
 *
 * This script runs in a privileged context and exposes a safe, typed API
 * to the renderer process via contextBridge.
 *
 * IMPORTANT: This file must be compiled to CommonJS format (.cjs)
 * because Electron's preload scripts don't support ES modules.
 */

import { contextBridge, ipcRenderer } from 'electron';

// ============================================================================
// TYPE DEFINITIONS
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
}

export interface Settings {
  theme: 'light' | 'dark' | 'system';
}

// ============================================================================
// API INTERFACE
// ============================================================================

export interface ElectronAPI {
  // Authentication
  auth: {
    /** Start OAuth flow in system browser */
    startOAuth: (provider: 'google' | 'github') => Promise<void>;
    /** Get current session (null if not authenticated) */
    getSession: () => Promise<Session | null>;
    /** Log out and clear session */
    logout: () => Promise<void>;
    /** Subscribe to auth success events (returns unsubscribe function) */
    onSuccess: (callback: (session: Session) => void) => () => void;
    /** Subscribe to auth error events (returns unsubscribe function) */
    onError: (callback: (error: string) => void) => () => void;
  };

  // Persistent storage
  store: {
    /** Get a value from storage */
    get: <T>(key: string) => Promise<T | undefined>;
    /** Set a value in storage */
    set: <T>(key: string, value: T) => Promise<void>;
    /** Delete a value from storage */
    delete: (key: string) => Promise<void>;
    /** Get settings */
    getSettings: () => Promise<Settings>;
    /** Update settings */
    updateSettings: (settings: Partial<Settings>) => Promise<void>;
  };

  // App utilities
  app: {
    /** Get app version */
    getVersion: () => Promise<string>;
    /** Open URL in system browser */
    openExternal: (url: string) => Promise<void>;
    /** Open directory picker dialog */
    selectDirectory: () => Promise<string | null>;
  };
}

// ============================================================================
// API IMPLEMENTATION
// ============================================================================

const electronAPI: ElectronAPI = {
  auth: {
    startOAuth: (provider) => ipcRenderer.invoke('auth:start-oauth', provider),
    getSession: () => ipcRenderer.invoke('auth:get-session'),
    logout: () => ipcRenderer.invoke('auth:logout'),

    // Event subscriptions with cleanup
    onSuccess: (callback) => {
      const handler = (_event: Electron.IpcRendererEvent, session: Session) =>
        callback(session);
      ipcRenderer.on('auth:success', handler);
      // Return unsubscribe function
      return () => ipcRenderer.removeListener('auth:success', handler);
    },
    onError: (callback) => {
      const handler = (_event: Electron.IpcRendererEvent, error: string) =>
        callback(error);
      ipcRenderer.on('auth:error', handler);
      return () => ipcRenderer.removeListener('auth:error', handler);
    },
  },

  store: {
    get: (key) => ipcRenderer.invoke('store:get', key),
    set: (key, value) => ipcRenderer.invoke('store:set', key, value),
    delete: (key) => ipcRenderer.invoke('store:delete', key),
    getSettings: () => ipcRenderer.invoke('store:get-settings'),
    updateSettings: (settings) =>
      ipcRenderer.invoke('store:update-settings', settings),
  },

  app: {
    getVersion: () => ipcRenderer.invoke('app:get-version'),
    openExternal: (url) => ipcRenderer.invoke('app:open-external', url),
    selectDirectory: () => ipcRenderer.invoke('dialog:open-directory'),
  },
};

// ============================================================================
// EXPOSE TO RENDERER
// ============================================================================

contextBridge.exposeInMainWorld('electron', electronAPI);

// ============================================================================
// GLOBAL TYPE DECLARATION
// ============================================================================

declare global {
  interface Window {
    electron: ElectronAPI;
  }
}
