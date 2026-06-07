// Secure bridge between renderer and main process.
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('erh', {
  // payload: { items: [{ text, complexity? }], importanceQuantile?, C? }
  evaluate: (payload) => ipcRenderer.invoke('erh:evaluate', payload),
});
