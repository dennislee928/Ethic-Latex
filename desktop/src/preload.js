// Secure bridge between renderer and main process.
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('erh', {
  // payload: { items: [{ text, complexity? }], importanceQuantile?, C? }
  evaluate: (payload) => ipcRenderer.invoke('erh:evaluate', payload),
  // params: { numActions, dist, seed, biasStrength } — Tier B (sidecar) only
  simulate: (params) => ipcRenderer.invoke('erh:simulate', params),
  backendInfo: () => ipcRenderer.invoke('erh:backendInfo'),
  importFile: () => ipcRenderer.invoke('erh:importFile'),
  exportResult: (result) => ipcRenderer.invoke('erh:exportResult', result),
});
