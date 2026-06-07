// ERH Ethics Inspector — Electron main process.
// Creates the application window and wires IPC handlers that run the local
// ERH ethical-degree evaluator (no network/backend required).

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { evaluateResponses } = require('./erh-eval');

function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 800,
    title: 'ERH Ethics Inspector',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

// IPC: evaluate a batch of LLM responses and return ERH metrics.
ipcMain.handle('erh:evaluate', async (_event, payload) => {
  try {
    return { ok: true, result: evaluateResponses(payload) };
  } catch (err) {
    return { ok: false, error: String(err && err.message ? err.message : err) };
  }
});

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
