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

這是一份為 **Cursor** 或其他 AI 編輯器準備的 `cursor.plan.md` 開發計畫書。這份文件針對您要求的「純前端 Next.js 實作」與「身分認證串聯」進行了模組化拆解。

---

# Project Plan: AI-Powered Male Biometric Measurement & Certification System

## 1. 專案概述 (Project Overview)

建構一個基於 Next.js 的純前端應用，利用瀏覽器端 AI 進行男性生殖器尺寸測量，並結合第三方身份驗證（如 Persona）進行「真人屬性認證」。

- **核心技術：** Next.js 14+ (App Router), TensorFlow.js / MediaPipe, Persona SDK.
- **隱私原則：** 影像不離開用戶設備（On-device Processing），僅傳輸測量結果。

---

## 2. 階段一：環境初始化與相機模組 (Environment & Camera Setup)

- **初始化專案**
- 使用 `npx create-next-app@latest` 建立專案。
- 安裝必要依賴：`@tensorflow/tfjs`, `@mediapipe/selfie_segmentation`, `lucide-react`, `canvas-confetti` (用於成功認證動畫)。
- **開發相機引導組件 (`CameraCapture.tsx`)**
- 實作 `getUserMedia` API 調用。
- 建立 UI 遮罩（Overlay），引導用戶將「參考物」（如信用卡）與目標物放置在正確位置。
- 實作「環境光線檢測」與「模糊檢測」邏輯。

---

## 3. 階段二：瀏覽器端 AI 運算 (On-device AI Engine)

- **模型加載與熱啟動**
- 配置 TensorFlow.js 的 WASM 後端以提升運算效能。
- 載入語義分割模型（Semantic Segmentation），用於區分背景、參考物與目標。
- **尺寸測量邏輯實作 (`measurementEngine.ts`)**
- **步驟 A：參考物標定**
- 辨識標準卡片邊緣，計算 $Pixels Per Metric (PPM)$。
- **步驟 B：目標分割與特徵點提取**
- 使用 Mask R-CNN 或自定義節點模型識別目標邊界。
- **步驟 C：幾何修正**
- 實作透視變換（Perspective Transform）校正拍攝角度造成的縮短效應（Foreshortening）。
- **步驟 D：物理單位轉換**
- 根據 $PPM$ 公式計算長度與周長。

---

## 4. 階段三：身份驗證與數據簽名 (Identity & Certification)

- **串接 Persona 客戶端 SDK**
- 在前端嵌入 `Persona.Inquiry` 流程。
- 用戶完成政府證件與人臉掃描，獲取 `inquiry_id`。
- **數據加簽模組 (`certificationProvider.ts`)**
- 實作「數位簽名」邏輯：將 `inquiry_id` + `measurement_result` + `timestamp` 進行哈希運算（HMAC/SHA256）。
- 模擬生成「數位認證證書」JSON 檔案供用戶下載或展示。
- **防作弊機制**
- 實作 Liveness Detection，確保測量過程為即時動態而非靜態照片。

---

## 5. 階段四：隱私與合規防禦 (Privacy & Compliance)

- **端點脫敏處理**
- 實作 `Client-side Blur`：在 UI 展示時，除了測量邊框外，對敏感部位進行像素化處理。
- **零存儲架構確認**
- 確保 `useEffect` 清除緩存，瀏覽器關閉後影像數據不留存於 `localStorage` 或 `IndexedDB`。

---

## 6. 技術指標與驗證 (Technical Specs & Validation)


| 項目         | 目標規格                        | 驗證方式                    |
| ---------- | --------------------------- | ----------------------- |
| **運算延遲**   | < 500ms / frame             | 效能分析器 (Chrome Profiler) |
| **測量誤差**   | $\pm 0.3 \text{ cm}$        | 物理對比測試 (Standard Ruler) |
| **瀏覽器相容性** | iOS Safari / Android Chrome | 行動裝置實機測試                |
| **認證可靠度**  | Persona Verified Status     | Webhook 回調驗證            |


---

## 7. 下一步行動 (Next Steps)

1. **實作相機取景框：** 建立一個能精確提示用戶對齊參考物與目標物的 UI。
2. **原型測試：** 使用非生物物件（如圓柱體與卡片）測試像素與公分轉換的準確性。

---

### 資料來源 (Data Sources)

> 1. **Next.js Documentation:** App Router and Server Components architecture.
> 2. **TensorFlow.js API Reference:** Real-time object detection and segmentation in the browser.
> 3. **Persona Developer Guide:** Identity verification and inquiry workflow integration.
> 4. **OpenCV.js (Geometric Transformations):** Standard algorithms for perspective correction.

**你想先從哪一部分開始？我可以為你撰寫 `measurementEngine.ts` 的核心計算邏輯。**