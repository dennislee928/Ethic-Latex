# SDK 發佈指南（GitHub Actions）｜SDK Publishing Guide

本文件說明 **`erh`（PyPI）** 與 **`erh-js-sdk`（npm）** 在本 repo 中如何經 CI 驗證與發佈，以及如何手動發佈。對應 workflow：`.github/workflows/sdk_python.yml`、`.github/workflows/sdk_node.yml`。

This document describes how **`erh` (PyPI)** and **`erh-js-sdk` (npm)** are validated and released via GitHub Actions in this repository, including manual release steps. Workflows: `.github/workflows/sdk_python.yml`, `.github/workflows/sdk_node.yml`.

---

## 繁體中文

### 1. 套件與來源位置

| 套件 | Registry | 版本來源 | 打包根目錄／目錄 |
|------|-----------|----------|------------------|
| `erh` | [PyPI](https://pypi.org/project/erh/) | `pyproject.toml` → `[project]` `version` | 儲存庫**根目錄**（`python -m build`） |
| `erh-js-sdk` | [npm](https://www.npmjs.com/package/erh-js-sdk) | `js-sdk/package.json` → `version` | `js-sdk/`（`npm run build`、`npm publish`） |

發佈前請確認 **兩邊版本策略一致**（例如都已 bump 為 `0.1.1`），並與 Git **tag**（見下文）對齊，以避免「tag 已打但套件版本仍是舊的」這類落差。

---

### 2. Workflow 觸發條件（何時會跑）

**Python：`sdk_python.yml`**

- **push**：`main`、`dev` 分支，以及 **`v*` 標籤**（例如 `v0.2.0`）。
- **pull_request**：對 `main` 的 PR。

**Node：`sdk_node.yml`**

- **push**：僅 **`main`** 分支，以及 **`v*` 標籤**。
- **pull_request**：對 `main` 的 PR。

> **注意**：Node workflow **不會**在 push 到 `dev` 時觸發（除非你擴充 `on.push.branches`）。Python 會。

---

### 3. Job 結構：`test` → `publish`

兩個 workflow 皆為 **`test` 完成後才可 `publish`**（`needs: test`）。

| Job | 目的 |
|-----|------|
| **test** | 安裝依賴、建置／測試（以及 Python 端的 lint／安全掃描等） |
| **publish** | 建置發佈產物並上傳至 PyPI／npm |

---

### 4. 為何「第二部 publish 常顯示 Skipped？」

**`publish` job** 有下列條件（兩個 workflow 相同語意）：

```yaml
if: startsWith(github.ref, 'refs/tags/v')
```

因此：

- **只在 push 形如 `refs/tags/v1.2.3` 的 Git tag** 時，`publish` **會執行**。
- **一般分支 push（`main`/`dev`）、或未打 tag 的情況下**，`publish` **會被跳過**。這通常就是您看到的「第二部 skip」——屬於**設計**，不是 CI 故障。

若要觸發發佈，請使用 **語意化版本 tag**，例如：

```bash
git tag v0.2.0
git push origin v0.2.0
```

（請依實際版本號調整；tag 名與 `pyproject.toml` / `package.json` 的版本應一致或遵循團隊規範。）

---

### 5. Node：`test` 整段被 skip 的原因（placeholder 偵測）

`sdk_node.yml` 會檢查 `js-sdk/package.json`：

- 若檔案不存在；**或**
- **同時**滿足：`"version": "0.0.0"` **且** `"private": true`

則視為 **placeholder**，後續 `npm install` / `npm run build` / `npm test` **全部不執行**。

正式 SDK 請維持**非**上述組合（例如目前常見為 `0.1.0`、無 `private: true`），CI 才會跑 Node 步驟。

建置相關：`js-sdk/tsconfig.json` 需符合 TypeScript 6 對 **`rootDir`** 的要求（例如設為 `"./src"`），否則 `npm run build` 可能在 CI 失敗（錯誤 `TS5011`）。

---

### 6. Python：`publish` 實際做了什麼

1. Checkout  
2. 安裝 `build`、`twine`  
3. 在**儲存庫根目錄**執行 **`python -m build`**（依 `pyproject.toml` 產出 `dist/`）  
4. **`twine upload dist/* --skip-existing`**，憑證使用 **`secrets.PYPI_TOKEN`**

`--skip-existing`：若 PyPI 上已存在相同檔名，會略過該檔，方便 **重跑 workflow** 時不因重複上傳而整體失敗。

---

### 7. Node：`publish` 實際做了什麼

1. 同樣先做 placeholder 檢查（見第 5 節）  
2. `npm ci`/`npm install`、`npm run build`  
3. **`npm publish`**，`NODE_AUTH_TOKEN` 使用 **`secrets.NPM_TOKEN`**

**Token 類型**：請使用 npm 的 **Automation token**（可在 npm 網站建立）。CI 無法互動輸入 OTP；若 token 類型需要二次驗證，容易出現 **EOTP** 類錯誤。

---

### 8. GitHub Secrets 設定

於 **Repository → Settings → Secrets and variables → Actions** 新增：

| Secret 名稱 | 用途 |
|-------------|------|
| `PYPI_TOKEN` | PyPI API token（上傳權限）。`twine` 使用 `TWINE_USERNAME=__token__` + 此 token。 |
| `NPM_TOKEN` | npm **Automation** token，供 `NODE_AUTH_TOKEN` 使用。 |

請勿將 token 寫入程式碼或公開 issue／PR。

---

### 9. 建議發佈流程（CI 自動）

1. 更新版本號：  
   - Python：`pyproject.toml` 中 `[project]` 的 `version`  
   - Node：`js-sdk/package.json` 的 `version`  
2. Commit 並推送到預設分支（依團隊流程，可能需 PR review）。  
3. 建立並推送 **同一發佈意圖** 的 tag，例如 `v0.2.0`：  
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```  
4. 在 **Actions** 分頁確認 `sdk_python.yml` / `sdk_node.yml`：`test` 通過後 **`publish`** 有執行且成功。

**registry 注意事項**

- PyPI：若該版本對應的 artifact **已存在**，`--skip-existing` 可能使上傳「無新檔」；發新檔請 **必 bump 版本**。  
- npm：**同一 `version` 無法重複 publish**；發新版務必 bump `js-sdk/package.json` 的 `version`。

---

### 10. 手動發佈（不依賴 CI）

**PyPI（儲存庫根目錄）**

```bash
python -m pip install --upgrade pip build twine
python -m build
TWINE_USERNAME=__token__ TWINE_PASSWORD=<your-pypi-token> twine upload dist/*
```

**npm（`js-sdk/` 目錄）**

```bash
cd js-sdk
npm install
npm run build
# 需已登入 npm，或設定 NODE_AUTH_TOKEN 後：
npm publish
```

---

### 11. 疑難排解（摘要）

| 現象 | 可能原因 |
|------|-----------|
| `publish` 永遠 skip | 未推送 `v*` tag；ref 不是 `refs/tags/v...` |
| Node `test` 全 skip | `js-sdk/package.json` 仍為 `0.0.0` + `private: true` |
| `npm run build` 失敗（TS5011） | `js-sdk/tsconfig.json` 缺少 `rootDir`（例如 `"./src"`） |
| PyPI 上無新版本 | 未 bump `pyproject.toml`；或 artifact 已存在被 skip |
| npm publish 403／EOTP | Token 類型錯誤或非 Automation；權限／套件名稱不符 |

---

### 12. 進階：若要「merge main 就自動發佈」

目前設計為 **僅 tag 觸發 `publish`**。若改為每次 merge 即發佈，需修改 workflow 的 `if:`，並嚴格避免 **每次 push 都重發同一版本**（registry 與使用者體驗風險）。建議維持 tag 發佈或改用 release 流程（例如 GitHub Releases + workflow_dispatch）。

---

## English

### 1. Packages and sources

| Package | Registry | Version source | Build root |
|---------|----------|----------------|------------|
| `erh` | [PyPI](https://pypi.org/project/erh/) | `pyproject.toml` → `[project]` `version` | Repository **root** (`python -m build`) |
| `erh-js-sdk` | [npm](https://www.npmjs.com/package/erh-js-sdk) | `js-sdk/package.json` → `version` | `js-sdk/` (`npm run build`, `npm publish`) |

Before releasing, align **version numbers** across Python and Node (and with your Git tag policy) so you do not tag `v0.2.0` while packages still declare `0.1.0`.

---

### 2. When workflows run

**Python (`sdk_python.yml`):** push to **`main`**, **`dev`**, and tags **`v*`**; PRs targeting **`main`**.

**Node (`sdk_node.yml`):** push to **`main`** and tags **`v*`** only; PRs targeting **`main`**.

Node does **not** run on pushes to `dev` unless you extend `on.push.branches`.

---

### 3. Jobs: `test` then `publish`

Both workflows use **`needs: test`** for **`publish`**.

| Job | Role |
|-----|------|
| **test** | Install deps, build/test (plus Python lint/security steps) |
| **publish** | Build artifacts and upload to PyPI/npm |

---

### 4. Why `publish` is often “Skipped”

The **`publish`** job is gated by:

```yaml
if: startsWith(github.ref, 'refs/tags/v')
```

So **`publish` runs only when you push a version tag** such as `v0.2.0`. Ordinary branch pushes (without a tag) skip **`publish`** by design—that is usually what people mean by “the second job skipped.”

Example:

```bash
git tag v0.2.0
git push origin v0.2.0
```

---

### 5. Node: when the entire `test` job is skipped (placeholder detection)

If `js-sdk/package.json` is missing **or** matches **both** `"version": "0.0.0"` **and** `"private": true`, the workflow treats the package as a **placeholder** and skips install/build/test.

For a real SDK, keep a non-placeholder manifest (e.g. `0.1.0` without `"private": true`).

Build note: **`js-sdk/tsconfig.json` must set `rootDir`** (e.g. `"./src"`) for TypeScript 6 compatibility; otherwise CI may fail `npm run build` with **`TS5011`**.

---

### 6. Python `publish` steps

1. Checkout  
2. Install `build` and `twine`  
3. Run **`python -m build`** at the **repo root**  
4. **`twine upload dist/* --skip-existing`** using **`secrets.PYPI_TOKEN`**

`--skip-existing` avoids hard failures when re-running a workflow if artifacts already exist on PyPI.

---

### 7. Node `publish` steps

After the same placeholder check: install, **`npm run build`**, then **`npm publish`** with **`NODE_AUTH_TOKEN`** from **`secrets.NPM_TOKEN`**.

Use an npm **Automation** token for CI (non-interactive). Tokens that require OTP often surface as **EOTP** errors.

---

### 8. Required GitHub Secrets

**Settings → Secrets and variables → Actions:**

| Secret | Purpose |
|--------|---------|
| `PYPI_TOKEN` | PyPI API token with upload scope (`TWINE_USERNAME=__token__`). |
| `NPM_TOKEN` | npm Automation token for `NODE_AUTH_TOKEN`. |

Never commit tokens.

---

### 9. Recommended CI release sequence

1. Bump versions in **`pyproject.toml`** and **`js-sdk/package.json`**.  
2. Merge to your default branch per team process.  
3. Create and push a matching tag:  
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```  
4. Verify in **Actions** that **`test`** passes and **`publish`** runs successfully.

Registry notes:

- PyPI: if artifacts for that version already exist, uploads may be skipped; bump the version for a new release.  
- npm: **you cannot republish the same version**; bump **`js-sdk/package.json`** before publishing again.

---

### 10. Manual publishing (without CI)

**PyPI (repository root)**

```bash
python -m pip install --upgrade pip build twine
python -m build
TWINE_USERNAME=__token__ TWINE_PASSWORD=<your-pypi-token> twine upload dist/*
```

**npm (`js-sdk/`)**

```bash
cd js-sdk
npm install
npm run build
npm publish   # or set NODE_AUTH_TOKEN for non-interactive publish
```

---

### 11. Troubleshooting (quick reference)

| Symptom | Likely cause |
|---------|----------------|
| `publish` always skipped | No **`v*`** tag pushed |
| Node `test` skipped | Placeholder `package.json` (`0.0.0` + `private`) |
| `npm run build` fails (`TS5011`) | Missing `rootDir` in **`js-sdk/tsconfig.json`** |
| No new files on PyPI | Version not bumped or artifacts skipped as existing |
| npm 403 / EOTP | Wrong token type or permissions |

---

### 12. Advanced: publishing on every `main` merge

Today **`publish`** is **tag-only**. Changing that requires editing workflow `if:` conditions and careful guardrails to avoid republishing the same version repeatedly. Tag-based releases or **`workflow_dispatch`** are safer defaults.

---

## Document maintenance

- When workflow paths or branch filters change, update **§2** and file references at the top.  
- When registry package names or monorepo layout change, update **§1**.  
- Keep **Secrets** names in sync with `.github/workflows/sdk_*.yml`.
