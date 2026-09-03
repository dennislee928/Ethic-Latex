# ERH Guardian — issue #93 剩餘 dev 工作計畫

> 核准後第一步：把本計畫複製到 `/Users/dennis/Documents/git/Ethic-Latex/.claude/hackathon-remaining-dev.plan.md`（使用者指定位置）。

## Context

Agents for Humans hackathon（Devpost 期限 9/14，自訂送出日 9/13）。issue #93 是總 checklist；本計畫涵蓋其中 **Claude 可執行的 dev 工作**，人工步驟（Devpost join、錄影、送件）由使用者操作。

### 本 session 已完成 / 已確認

- **A3 Bedrock ✅ 全綠**：AWS CLI v2 已裝；`aws login` 通（帳號 `711553772978`）；use-case 表單 + 帳號驗證都過；`global.anthropic.claude-sonnet-4-6` Converse 實測成功（us-west-2）；Haiku profile ACTIVE 可當 fallback。→ 待補資料區可填：AWS Account ID `711553772978`、model id `global.anthropic.claude-sonnet-4-6`、開通日期 2026-09-03。
- **A2 情報**（join 本身仍需使用者）：credits 表單 `https://forms.gle/Ssr8zLw4afKg114M7`；截止 9/11 12pm PT；必填 Email / 姓名 / 國家 / **Devpost Username** / **Track+2–3 句描述**（沒寫 track 自動拒絕）；審核約 3 個工作天 → 建議 9/8 前送。
- **使用者已決策**：(1) worker 補 bearer token——寫入端保護、面板 GET 保持公開；(2) engine 依賴用 git+sha 釘版；(3) PR #94 縮成 engine-only。

### 程式現況（Explore 已驗證，branch `feat-hackthon-agents`）

- `mcp-worker/src/index.ts`（192 行）：**無任何 auth**；`/api/*` 已有 CORS `*` + OPTIONS preflight（L132-136、L165-170）；`/api/*` 只有 GET（profile、decisions），**寫入都走 `/mcp`、`/sse` 的 MCP tools**（`update_profile`、`log_decision`）。
- `mcp-worker/wrangler.jsonc`：`database_id` 仍是 `"REPLACE_WITH_D1_DATABASE_ID"`（L15）；無 vars/secrets。
- `ui/src/App.tsx`：L3 `VITE_API_URL`（build-time）；只打 GET `/api/profile`、`/api/decisions?limit=50`；無 `.env.example`。
- `pyproject.toml`：ERH engine **只是註解不是依賴**（L18-19），靠 `src/erh_guardian/_bootstrap.py` 的 sys.path hack；`[dev]` 只有 pytest。
- `README.md`：setup 寫「from the Ethic-Latex repository root」+ `pip install -e hackathon/erh-guardian-agent[dev]`——抽 repo 後會失效；disclosure 段落已存在（L82-88）；只有 1 個簡化版 mermaid（L25-42）。
- `mcp_link.py:19-24`：讀 `ERH_GUARDIAN_MCP_URL`，`streamablehttp_client(url)` **沒帶 headers**。
- 無 `docs/` 目錄、repo 內零圖片檔。
- 測試：`tests/test_guardian.py` 7 個（離線）；worker/UI 無測試。
- `.claude/implementation.plan.md` §4 有全系統 mermaid（L55-93）；Phase 2 bearer token 項目未勾（L136）。

---

## 工作項（依序）

### P1 — Worker bearer token auth（B2 前置，R2 風險）

檔案：`hackathon/erh-guardian-agent/mcp-worker/src/index.ts`

- `Env` 加 `MCP_AUTH_TOKEN?: string`（用 `wrangler secret put MCP_AUTH_TOKEN` 設定，不進 wrangler.jsonc）。
- 新增 guard：`/mcp`、`/sse` 與任何非 GET/OPTIONS 的 `/api/*` 要求 `Authorization: Bearer <token>`，不符回 401（JSON + CORS headers）。
- `MCP_AUTH_TOKEN` 未設定時（本地 `wrangler dev`）跳過檢查並 `console.warn`——保持本地開發零設定。
- 保持公開：`/health`、GET `/api/profile`、GET `/api/decisions`（透明面板要能直接給 judges 看）。
- `src/erh_guardian/mcp_link.py`：讀 `ERH_GUARDIAN_MCP_TOKEN` 環境變數（沿用現有 `os.environ.get` 慣例），有值時 `streamablehttp_client(url, headers={"Authorization": f"Bearer {token}"})`。
- UI 不用改（只打公開 GET）。
- README（頂層 + `mcp-worker/README.md`）補 `ERH_GUARDIAN_MCP_TOKEN` 與 secret 設定說明。
- 測試：`tests/test_guardian.py` 不受影響；worker 用 `npm run typecheck` 驗。

### P2 — pyproject 把 ERH engine 變成真依賴（C1 前置，R5）

檔案：`hackathon/erh-guardian-agent/pyproject.toml`、`README.md`

- 先確認 Ethic-Latex repo 根目錄的 Python 打包（setup.py/pyproject、package 名稱是否為 `erh`）；以 **PR #94 engine 修正合併後的 sha**（或現階段先用 `feat-hackthon-agents` HEAD sha，合併後再改）加入：
  `erh @ git+https://github.com/dennislee928/Ethic-Latex@<sha>`
- 保留 `_bootstrap.py` 的 sys.path fallback（monorepo 內開發仍可用）。
- README setup 改寫成 standalone repo 版本：`pip install -e .[dev]`、`pytest tests -q`，並註明 PyPI `erh` 為替代來源。
- 若根目錄不可 pip 安裝，退路：在 README 明確寫兩步安裝（先 `pip install erh` 或 git clone Ethic-Latex + 設 `ERH_ENGINE_PATH`），並在 plan 執行時回報。

### P3 — B1 本機測試 + Bedrock live smoke test（A3 已綠，現在就能做）

```bash
python -m venv .venv && source .venv/bin/activate
pip install numpy scipy networkx fastapi requests pydantic
pip install -e 'hackathon/erh-guardian-agent[dev]'
pytest hackathon/erh-guardian-agent/tests -q        # 預期 7 passed
erh-guardian demo                                    # 離線
export AWS_REGION=us-west-2 ERH_GUARDIAN_MODEL=global.anthropic.claude-sonnet-4-6
erh-guardian chat                                    # 真打 Bedrock
```
- 驗收 = issue B1：安全任務回 risk_score/erh_satisfied/α；`intern-admin` 高風險 remediation 被 GuardianGate 攔下、輸入 `n` 不執行。
- 卡點對照：`ThrottlingException` → 改 `global.anthropic.claude-haiku-4-5-20251001-v1:0`。

### P4 — D1 架構圖匯出

- 建 `hackathon/erh-guardian-agent/docs/`。
- 用本地 `npx -y @mermaid-js/mermaid-cli` 渲染兩張圖（不依賴 mermaid.live）：
  1. `.claude/implementation.plan.md` §4 全系統圖 → `docs/architecture.svg` + `docs/architecture.png`（白底、寬 ≥1600px）
  2. README 的 GuardianGate 流程圖 → `docs/guardian-gate.svg` + `.png`
- README 改成直接引用圖片（保留 mermaid 原始碼在 `docs/*.mmd`），並把 §4 全系統圖帶進 README（目前只有簡化版）。

### P5 — UI 小補（B3 前置）

- `ui/.env.example`：`VITE_API_URL=https://erh-guardian-mcp.<account>.workers.dev`（註明 base URL、不要接 `/mcp`、build-time 注入）。
- `ui/src/vite-env.d.ts` 補 `VITE_API_URL` 型別。

### P6 — PR #94 縮成 engine-only

- 從 `main` 開新分支 `engine-bedrock-fixes`，只帶：`erh_engine` Bedrock provider、over-refusal 修正 + 2 個 engine 測試、`6df4205`（networkx）與 `a936de0`（httpx）兩個 CI 修正。用 `git checkout feat-hackthon-agents -- erh_engine/ .github/workflows/<相關檔>` 取內容，不 rewrite 歷史。
- **`feat-hackthon-agents` 分支保持原樣不動**（C1 的 subtree split 要用它的完整歷史）。
- PR #94 改 base branch 或關閉重開為 engine-only PR（執行時以 `gh pr edit`/`gh pr create` 操作，關舊開新需在 PR 留言說明）。
- Ethic-Latex 的 `.claude/implementation.plan.md` 等 hackathon 文件隨 hackathon/ 一起留在新 repo，不進 main。

### P7 — C1 抽獨立 repo（半人工：`gh repo create` 需使用者確認）

- 依 issue C1 的 subtree split 流程：`git subtree split --prefix=hackathon/erh-guardian-agent -b erh-guardian-split` → 新 repo `dennislee928/erh-guardian-agent`（public、MIT、topics 照 issue）。
- push 前先在 split 分支上確認 P1/P2/P4/P5 的改動都已包含。
- **fresh clone 實測** README setup（`pip install -e .[dev]` → pytest 7 passed）——issue R4 明講這是最容易失分的一步。
- 驗最早 commit 落在 Aug 10–Sep 14 窗口：`git log --reverse --date=iso --format='%ad %s' | head -3`。
- disclosure 段落補上 PR 連結（engine-only PR）。

### P8 — B2–B4 部署（半人工：`wrangler login` 與 `gh repo create` 需使用者互動）

依 issue B2/B3/B4 指令執行：d1 create → 貼 `database_id` → migrate local/remote → `wrangler secret put MCP_AUTH_TOKEN` → deploy → `/health` 200、無 token 打 `/mcp` 得 401、GET `/api/*` 公開可讀 → UI build（`VITE_API_URL`=worker base）→ pages deploy → 面板顯示 profile/decisions → `ERH_GUARDIAN_MCP_URL`(+`/mcp`) + `ERH_GUARDIAN_MCP_TOKEN` 跑 `erh-guardian chat`，驗 4 個 MCP tools 被發現、高風險 decision 出現在線上面板。

### 不做（明確排除）

- Worker/UI 自動化測試（issue 未要求，時間換給 D 系列）；B5 AgentCore 維持 9/11 go/no-go，不在本計畫。

## 關鍵檔案

| 檔案 | 動作 |
|---|---|
| `hackathon/erh-guardian-agent/mcp-worker/src/index.ts` | P1 auth guard |
| `hackathon/erh-guardian-agent/src/erh_guardian/mcp_link.py` | P1 token header |
| `hackathon/erh-guardian-agent/pyproject.toml` | P2 git dep |
| `hackathon/erh-guardian-agent/README.md` | P2 setup 改寫、P4 圖片引用 |
| `hackathon/erh-guardian-agent/docs/`（新） | P4 圖檔 |
| `hackathon/erh-guardian-agent/ui/.env.example`（新）、`ui/src/vite-env.d.ts` | P5 |
| `hackathon/erh-guardian-agent/mcp-worker/wrangler.jsonc` | P8 database_id |

## Verification

1. `pytest hackathon/erh-guardian-agent/tests -q` → 7 passed（P1/P2 改完各跑一次）
2. `cd mcp-worker && npm run typecheck` → 過
3. `wrangler dev` 本地：無 token 時 `/mcp` 仍可用（dev 模式）+ console 警告；設 `MCP_AUTH_TOKEN` 後無 token 401、帶 token 200
4. P3 live smoke test：GuardianGate 攔阻場景實跑成功（這就是影片要拍的畫面）
5. P7 fresh clone：README 指令逐行照跑到 7 passed
6. P8 部署後：`/health` 200、401/200 auth 行為、面板載入資料、decision 即時出現

## 時程對齊（今天 9/3）

- 9/3–9/4：P1–P3（B1 smoke test 今天就能跑）
- 9/5–9/7：P4–P5、P8 部署、P6 PR 調整
- 9/8 前：使用者送 credits 表單（A4）
- 9/10 前：P7 抽 repo + fresh clone 驗證
