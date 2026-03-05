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

# Cursor 實作計畫：支援 App

## 第一階段：環境初始化

1. 初始化 `server` (Rust):
  - 使用 `cargo init server`
  - 安裝依賴: `axum`, `tokio`, `redis (with tokio-comp)`, `serde`, `tower-http`
2. 初始化 `web` (Next.js):
  - `npx create-next-app@latest web --tailwind --typescript`
  - 安裝 `lucide-react`, `leaflet`, `react-leaflet`

## 第二階段：後端 Redis Geo 邏輯 (Rust)

1. 實作 `GEOADD` 邏輯，將用戶發出的 `Signal` 存入 Redis，Key 設定 TTL (過期時間)。
2. 建立 WebSocket Handler：
  - 用戶連線時，根據其座標加入對應的 Redis Pub/Sub Channel。
  - 當新信號產生，使用 `GEORADIUS` 找出附近用戶並推播訊息。

## 第三階段：前端地圖與即時通訊 (Next.js)

1. 整合 Leaflet 地圖，獲取用戶當前位置。
2. 實作 WebSocket 客戶端：
  - 監聽 `NEW_SIGNAL` 事件，在地圖上渲染「斧頭幫煙花」動畫。
  - 實作 `sendSignal` 函式。

## 第四階段：優化與視覺效果

1. 增加煙花動畫效果（CSS Keyframes）。
2. 加入地圖聚合（Marker Clustering）防止信號過多。

