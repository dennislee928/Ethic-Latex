---
name: ERH Architecture Consolidation & Thesis Improvement
overview: 整合論文審稿意見、架構重整（erh/erh_core/erh-security-app 三重冗餘）、量子 Ising 模型增強、run_simulation_batch 與 EVS 實作。
todos:
  - id: a1-1
    content: 論文 A1.1 新增「近似真實道德值 V(a)」小節
    status: pending
  - id: a1-2
    content: 論文 A1.2 擴充 c(a) 操作型定義
    status: pending
  - id: a2-1
    content: 論文 A2.1 新增「ERH 作為必要條件」小節
    status: pending
  - id: a2-2
    content: 論文 A2.2 擴充 Comparative Analysis Table
    status: pending
  - id: a3-1
    content: 論文 A3.1 擴充 ζ_E(s) 零點/極點解釋
    status: pending
  - id: a3-2
    content: 論文 A3.2 連結量子相變與 ζ_E 極點
    status: pending
  - id: a4-1
    content: 論文 A4.1 插入三張關鍵圖（log-log、倫理質數、比較）
    status: pending
  - id: a4-2
    content: 論文 A4.2 補齊 fig:comparison 引用
    status: pending
  - id: a4-3
    content: 論文 A4.3 確保 generate_all_figures 在 LaTeX 編譯前執行
    status: pending
  - id: b1-1
    content: 架構 B1.1 分析 erh/ vs erh_core/ 差異
    status: pending
  - id: b1-2
    content: 架構 B1.2 確立 erh_core 為可安裝包
    status: pending
  - id: b2-1
    content: 架構 B2.1 將 erh/core 改為 re-export 或刪除重複
    status: pending
  - id: b3-1
    content: 架構 B3.1 修改 erh-security-app requirements.txt 添加 -e ../..
    status: pending
  - id: b3-2
    content: 架構 B3.2 審查 erh_security 是否為單純重複
    status: pending
  - id: b3-3
    content: 架構 B3.3 更新 metrics.py import 為 erh_core
    status: pending
  - id: b4-1
    content: 架構 B4 驗證 pytest backend 與 tests 通過
    status: pending
  - id: c1-1
    content: 量子 C1.1 新增 measure_social_tension() API
    status: pending
  - id: c1-2
    content: 量子 C1.2 確認 Hamiltonian 符合 Ising 模型
    status: pending
  - id: c2-1
    content: 量子 C2.1 確認 hybrid_model 寫入 quantum_energy
    status: pending
  - id: c3-1
    content: 量子 C3.1 新增 plot_social_tension_vs_time
    status: pending
  - id: c3-2
    content: 量子 C3.2 LaTeX 新增 Quantum Ising Model 小節
    status: pending
  - id: d1-1
    content: 腳本 D1.1 新增 ABMSimulator 模式 --mode abm
    status: pending
  - id: d1-2
    content: 腳本 D1.2 實作 run_single_trial ABMSimulator worker
    status: pending
  - id: d2-1
    content: 腳本 D2.1 新增 calculate_evs() 於 statistics.py
    status: pending
  - id: d3-1
    content: 腳本 D3.1 新增 plot_phase_transition_error_vs_complexity
    status: pending
  - id: d4-1
    content: 腳本 D4 確認 simulation.yml 使用 batch --instances 4
    status: pending
  - id: e1
    content: 文檔 E1 更新 README 架構說明
    status: pending
  - id: e2
    content: 文檔 E2–E4 端到端驗證與測試通過
    status: pending
isProject: true
---

# 蜃景交易所 (Mirage Exchange) — AI 輔助開發計畫書

> 依據 README.md 與 structure.md 產出之實作計畫。本專案為高併發分散式研究用，請勿用於非法商業用途。

## 目標與範圍

- **目標：** 建立可本地一鍵啟動的蜃景交易所雛形，涵蓋極短線拍賣、身份洗牌、死間開關三大機制。
- **範圍：** Monorepo 結構，含 Frontend (Next.js)、Gateway/Sentinel (Go)、Engine/Identity (Rust)、共用 packages、Docker Compose。

## Phase 1：專案骨架與共用套件

1. **目錄結構**
  - `apps/frontend`、`apps/gateway`、`apps/engine`、`apps/identity`、`apps/sentinel`
  - `packages/redis-lua`、`packages/proto`、`packages/types`
  - 根目錄 `docker-compose.yml`、必要時 `package.json`（workspaces）或各 app 獨立管理
2. **packages/redis-lua**
  - 極短線拍賣用 Lua：ZSet 競標、防超賣與原子結標（5 秒視窗）。
  - 腳本檔命名清晰（如 `auction_bid.lua`、`auction_settle.lua`），可被 Go/Rust 載入執行。
3. **packages/proto**
  - 定義 Gateway ↔ Engine、Gateway ↔ Identity 的 gRPC（或先 HTTP + JSON）介面。
  - 拍賣下單/查詢、身份取得/刷新等 message 與 service。
4. **packages/types**
  - TypeScript 型別：拍賣狀態、出價、身份 Token、WS 事件等，供 Frontend 與 Gateway 對齊。

## Phase 2：Go 服務 — Gateway 與 Sentinel

1. **apps/gateway**
  - Go + Gin（或標準庫），WebSocket 端點，連線管理（含 10 秒身份洗牌觸發）。
  - 轉發拍賣請求至 Engine、身份請求至 Identity（gRPC 或 HTTP）。
  - 訂閱 Redis Pub/Sub，將拍賣狀態/即時事件推給前端。
  - 讀取 `packages/redis-lua` 腳本或透過 Engine 間接使用 Redis。
2. **apps/sentinel**
  - Go 常駐程式，訂閱 Redis Keyspace Notifications（過期事件）。
  - 當約定 key 過期時觸發「焦土政策」或「玉石俱焚」邏輯（可先日誌 + 清空約定 key，不真刪業務資料）。
  - 可設定環境變數指定 Redis 位址與觸發 key 前綴。

## Phase 3：Rust 服務 — Engine 與 Identity

1. **apps/engine**
  - Rust 專案，提供 gRPC/HTTP API：接收下單、執行 Lua（ZSet 競標/結標）、回傳結果。
  - 依賴 `packages/redis-lua` 或內嵌腳本，使用 redis-rs 執行 EVAL。
  - 可選：排行榜 ZRange 查詢介面。
2. **apps/identity**
  - Rust 專案，提供 gRPC/HTTP API：發放/刷新虛擬 ID（Token），寫入 Redis Set/Hash。
  - 支援 Gateway 每 10 秒為連線更換虛擬 ID 之需求。

## Phase 4：前端與整合

1. **apps/frontend**
  - Next.js（App Router），賽博龐克終端風格 UI，Tailwind + Framer Motion。
  - WebSocket 連線至 Gateway，訂閱拍賣即時狀態與身份更新。
  - 頁面：登入/大廳（拍賣列表）、單場 5 秒極短線競標、簡易狀態展示。
2. **docker-compose.yml**
  - Redis（含 keyspace notifications 啟用）、Gateway、Sentinel、Engine、Identity、Frontend。
    - 依賴順序與網路、環境變數對齊 README 與上述服務。

## Phase 5：收尾與文件

1. **README 更新**
  - 補充 `docker-compose up -d` 與必要環境變數、預設埠位。
    - 簡短說明三大機制如何在本雛形中體現。
2. **CI（可選）**
  - 各服務單元測試、Lua 腳本與 Proto 同步檢查；前端 build 通過。

---

## 實作順序摘要


| 順序  | 項目             | 產出                           |
| --- | -------------- | ---------------------------- |
| 1   | 目錄與計畫書         | 本檔案 + apps/*, packages/* 空結構 |
| 2   | redis-lua      | 拍賣競標/結標 Lua 腳本               |
| 3   | proto          | 拍賣與身份 API 定義                 |
| 4   | types          | TS 型別與 WS 事件型別               |
| 5   | gateway        | Go WebSocket + 轉發 + Pub/Sub  |
| 6   | sentinel       | Go Keyspace 訂閱與觸發邏輯          |
| 7   | engine         | Rust 拍賣 API + Lua 執行         |
| 8   | identity       | Rust 虛擬 ID API               |
| 9   | frontend       | Next.js 賽博龐克 UI + WS         |
| 10  | docker-compose | 一鍵啟動所有服務                     |
| 11  | README         | 啟動說明與機制對照                    |


