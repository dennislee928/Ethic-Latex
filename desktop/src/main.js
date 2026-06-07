// ERH Ethics Inspector — Electron main process.
//
// Creates the window and wires IPC. Scoring prefers the Tier B erh_core Python
// sidecar (real research math); if it is unavailable it transparently falls
// back to the Tier A pure-JS scorer (src/erh-eval.js). Also handles file
// import/export and optional auto-update.

const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const fs = require('fs');
const path = require('path');
const { evaluateResponses } = require('./erh-eval');
const { Sidecar } = require('./sidecar');

const sidecar = new Sidecar();
let backendMode = 'js'; // 'erh_core' once the sidecar is confirmed ready

function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 860,
    title: 'ERH Ethics Inspector',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
  return win;
}

// --- Scoring: sidecar first, JS fallback -------------------------------------
async function evaluate(payload) {
  if (sidecar.available()) {
    try {
      const result = await sidecar.request('evaluate', payload);
      backendMode = 'erh_core';
      return { ...result, backend: 'erh_core' };
    } catch (err) {
      // fall through to JS on any sidecar failure
    }
  }
  backendMode = 'js';
  return { ...evaluateResponses(payload), backend: 'js' };
}

ipcMain.handle('erh:evaluate', async (_e, payload) => {
  try { return { ok: true, result: await evaluate(payload) }; }
  catch (err) { return { ok: false, error: String(err && err.message || err) }; }
});

ipcMain.handle('erh:simulate', async (_e, params) => {
  if (!sidecar.available()) {
    return { ok: false, error: 'Simulation requires the erh_core sidecar (Tier B), which is not bundled in this build.' };
  }
  try { return { ok: true, result: await sidecar.request('simulate', params) }; }
  catch (err) { return { ok: false, error: String(err && err.message || err) }; }
});

ipcMain.handle('erh:backendInfo', async () => {
  const info = { mode: backendMode, sidecarAvailable: sidecar.available() };
  if (sidecar.available()) {
    try { info.version = await sidecar.waitReady(5000); } catch (_) { /* ignore */ }
  }
  return info;
});

// --- File import / export ----------------------------------------------------
ipcMain.handle('erh:importFile', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    title: 'Import LLM responses',
    filters: [
      { name: 'Text / JSONL', extensions: ['txt', 'jsonl', 'json', 'csv'] },
      { name: 'All files', extensions: ['*'] },
    ],
    properties: ['openFile'],
  });
  if (canceled || !filePaths[0]) return { ok: false, canceled: true };
  try {
    const raw = fs.readFileSync(filePaths[0], 'utf8');
    return { ok: true, content: raw, path: filePaths[0] };
  } catch (err) {
    return { ok: false, error: String(err.message || err) };
  }
});

ipcMain.handle('erh:exportResult', async (_e, result) => {
  const { canceled, filePath } = await dialog.showSaveDialog({
    title: 'Export ERH report',
    defaultPath: 'erh-report.json',
    filters: [{ name: 'JSON', extensions: ['json'] }],
  });
  if (canceled || !filePath) return { ok: false, canceled: true };
  try {
    fs.writeFileSync(filePath, JSON.stringify(result, null, 2), 'utf8');
    return { ok: true, path: filePath };
  } catch (err) {
    return { ok: false, error: String(err.message || err) };
  }
});

// --- Optional auto-update ----------------------------------------------------
function initAutoUpdate() {
  if (!app.isPackaged) return;
  try {
    const { autoUpdater } = require('electron-updater');
    autoUpdater.on('error', (err) => {
      console.log('Update check skipped (no release found or offline):', err.message);
    });
    autoUpdater.checkForUpdatesAndNotify().catch(() => {});
  } catch (_) { /* electron-updater not installed; skip */ }
}

app.whenReady().then(() => {
  console.log('ERH Ethics Inspector starting...');
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    { role: 'fileMenu' },
    { role: 'editMenu' },
    { role: 'viewMenu' },
    { role: 'windowMenu' },
  ]));

  if (sidecar.available()) {
    console.log('Sidecar (Tier B) binary detected, initializing...');
    sidecar.start();
  } else {
    console.log('Sidecar not found, using Tier A (JS) fallback.');
  }

  createWindow();
  initAutoUpdate();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  sidecar.stop();
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => sidecar.stop());
