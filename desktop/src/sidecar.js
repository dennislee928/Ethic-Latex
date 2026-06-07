// Sidecar manager — locates and drives the frozen erh_core Python backend
// (Tier B). If no sidecar binary is found, callers fall back to the pure-JS
// scorer in erh-eval.js (Tier A).

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

function candidatePaths() {
  const exe = process.platform === 'win32' ? 'erh_sidecar.exe' : 'erh_sidecar';
  const names = [];
  // Packaged: extraResources lands in process.resourcesPath/sidecar.
  if (process.resourcesPath) {
    names.push(path.join(process.resourcesPath, 'sidecar', exe));
  }
  // Dev: a locally built binary.
  names.push(path.join(__dirname, '..', 'sidecar', 'dist', exe));
  return names;
}

function findSidecarBinary() {
  for (const p of candidatePaths()) {
    try {
      if (fs.existsSync(p)) return { type: 'binary', cmd: p, args: [] };
    } catch (_) { /* ignore */ }
  }
  // Dev fallback: run the .py directly if a Python interpreter is available.
  const py = path.join(__dirname, '..', 'sidecar', 'erh_sidecar.py');
  if (fs.existsSync(py) && (process.env.ERH_PYTHON || process.platform !== 'win32')) {
    const python = process.env.ERH_PYTHON || 'python3';
    return { type: 'python', cmd: python, args: [py] };
  }
  return null;
}

class Sidecar {
  constructor() {
    this.proc = null;
    this.ready = false;
    this.info = null;
    this._buf = '';
    this._pending = new Map();
    this._nextId = 1;
    this._readyResolvers = [];
  }

  available() {
    return findSidecarBinary() !== null;
  }

  start() {
    if (this.proc) return;
    const bin = findSidecarBinary();
    if (!bin) return;
    try {
      this.proc = spawn(bin.cmd, bin.args, {
        cwd: path.join(__dirname, '..', '..'), // repo root for dev imports
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, PYTHONUNBUFFERED: '1' },
      });
    } catch (_) {
      this.proc = null;
      return;
    }
    this.proc.stdout.on('data', (d) => this._onData(d));
    this.proc.on('exit', () => this._onExit());
    this.proc.on('error', () => this._onExit());
  }

  _onExit() {
    this.proc = null;
    this.ready = false;
    for (const { reject } of this._pending.values()) reject(new Error('sidecar exited'));
    this._pending.clear();
  }

  _onData(chunk) {
    this._buf += chunk.toString();
    let idx;
    while ((idx = this._buf.indexOf('\n')) >= 0) {
      const line = this._buf.slice(0, idx).trim();
      this._buf = this._buf.slice(idx + 1);
      if (!line) continue;
      let msg;
      try { msg = JSON.parse(line); } catch (_) { continue; }
      if (msg.event === 'ready') {
        this.ready = true;
        this.info = msg;
        this._readyResolvers.forEach((r) => r(msg));
        this._readyResolvers = [];
        continue;
      }
      const p = this._pending.get(msg.id);
      if (p) {
        this._pending.delete(msg.id);
        if (msg.ok) p.resolve(msg.result);
        else p.reject(new Error(msg.error || 'sidecar error'));
      }
    }
  }

  waitReady(timeoutMs = 8000) {
    if (this.ready) return Promise.resolve(this.info);
    if (!this.proc) this.start();
    if (!this.proc) return Promise.reject(new Error('sidecar unavailable'));
    return new Promise((resolve, reject) => {
      const t = setTimeout(() => reject(new Error('sidecar start timeout')), timeoutMs);
      this._readyResolvers.push((info) => { clearTimeout(t); resolve(info); });
    });
  }

  request(cmd, params, timeoutMs = 30000) {
    return this.waitReady().then(() => new Promise((resolve, reject) => {
      const id = this._nextId++;
      this._pending.set(id, { resolve, reject });
      const t = setTimeout(() => {
        if (this._pending.has(id)) {
          this._pending.delete(id);
          reject(new Error('sidecar request timeout'));
        }
      }, timeoutMs);
      const wrap = (fn) => (v) => { clearTimeout(t); fn(v); };
      this._pending.set(id, { resolve: wrap(resolve), reject: wrap(reject) });
      this.proc.stdin.write(JSON.stringify({ id, cmd, params }) + '\n');
    }));
  }

  stop() {
    if (this.proc) { try { this.proc.kill(); } catch (_) { /* ignore */ } }
    this.proc = null;
  }
}

module.exports = { Sidecar };
