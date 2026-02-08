/**
 * Electron Main Process
 *
 * This is the entry point for the Electron main process.
 * It handles window creation, protocol registration, and IPC setup.
 */

import { app, BrowserWindow, ipcMain, shell, protocol, dialog } from 'electron';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { setupAuth, handleAuthCallback } from './ipc-handlers/auth';
import { setupStore } from './ipc-handlers/store';

// ES modules equivalent of __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ============================================================================
// CONFIGURATION - Update these for your app
// ============================================================================

const PROTOCOL_SCHEME = 'myapp'; // Custom protocol (e.g., myapp://auth/callback)
const DEV_SERVER_URL = 'http://localhost:5173';

// ============================================================================
// PROTOCOL REGISTRATION
// ============================================================================

// Register custom protocol for OAuth callback
if (process.defaultApp) {
  // Development: need to pass executable path
  if (process.argv.length >= 2) {
    app.setAsDefaultProtocolClient(PROTOCOL_SCHEME, process.execPath, [
      process.argv[1],
    ]);
  }
} else {
  // Production: simpler registration
  app.setAsDefaultProtocolClient(PROTOCOL_SCHEME);
}

// ============================================================================
// WINDOW MANAGEMENT
// ============================================================================

let mainWindow: BrowserWindow | null = null;
const isDev = process.env.NODE_ENV !== 'production' || !app.isPackaged;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: join(__dirname, 'preload.cjs'),
      contextIsolation: true, // REQUIRED - isolates preload from renderer
      nodeIntegration: false, // REQUIRED - no Node.js in renderer
      sandbox: false, // Required for better-sqlite3 - document this trade-off
    },
    // macOS title bar styling
    titleBarStyle: 'hiddenInset',
    trafficLightPosition: { x: 16, y: 16 },
    show: false, // Show when ready to prevent flash
  });

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  // Load the app
  if (isDev) {
    mainWindow.loadURL(DEV_SERVER_URL);
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(join(__dirname, '../dist/index.html'));
  }

  // Handle external links - open in system browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ============================================================================
// SINGLE INSTANCE LOCK
// ============================================================================

const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  // Another instance is running - quit this one
  app.quit();
} else {
  // Handle second instance launch (Windows/Linux protocol handling)
  app.on('second-instance', (_event, commandLine) => {
    const url = commandLine.find((arg) =>
      arg.startsWith(`${PROTOCOL_SCHEME}://`)
    );
    if (url) {
      handleProtocolUrl(url);
    }

    // Focus main window
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

// ============================================================================
// PROTOCOL URL HANDLING
// ============================================================================

function handleProtocolUrl(url: string) {
  try {
    const parsedUrl = new URL(url);

    // Handle OAuth callback
    if (
      parsedUrl.pathname === '//auth/callback' ||
      parsedUrl.pathname === '/auth/callback'
    ) {
      const token = parsedUrl.searchParams.get('token');
      const state = parsedUrl.searchParams.get('state');
      const error = parsedUrl.searchParams.get('error');

      if (error) {
        mainWindow?.webContents.send('auth:error', error);
      } else if (token && state) {
        handleAuthCallback(token, state)
          .then((session) => {
            mainWindow?.webContents.send('auth:success', session);
          })
          .catch((err) => {
            console.error('[Auth] Callback error:', err);
            mainWindow?.webContents.send('auth:error', err.message);
          });
      }
    }
  } catch (err) {
    console.error('[Protocol] Failed to parse URL:', err);
  }
}

// macOS handles protocol via open-url event
app.on('open-url', (_event, url) => {
  handleProtocolUrl(url);
});

// ============================================================================
// APP LIFECYCLE
// ============================================================================

app.whenReady().then(() => {
  // Register protocol handler for development
  protocol.handle(PROTOCOL_SCHEME, (request) => {
    handleProtocolUrl(request.url);
    return new Response('', { status: 200 });
  });

  createWindow();

  // Setup IPC handlers
  setupAuth();
  setupStore();

  // macOS: re-create window when dock icon clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed (except macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// ============================================================================
// GENERAL IPC HANDLERS
// ============================================================================

ipcMain.handle('app:get-version', () => {
  return app.getVersion();
});

ipcMain.handle('app:open-external', (_event, url: string) => {
  shell.openExternal(url);
});

ipcMain.handle('dialog:open-directory', async () => {
  if (!mainWindow) return null;

  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory', 'createDirectory'],
    title: 'Select a folder',
  });

  if (result.canceled) {
    return null;
  }

  return result.filePaths[0];
});
