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

# 🚀  Cursor AI 開發指引：MediCanna AI 實作計畫

## Phase 1: 專案基礎建設與版本控制 (Project Setup)

- 1. 建立根目錄 `medicanna-ai-system` 並執行 `git init`。
- 1. 建立根目錄下的 `.gitignore` 檔案，忽略 node_modules, target, venv, .env 等檔案。
- 1. 建立 `ml-python-engine` 資料夾。
- 1. 建立 `backend-rust-gateway` 資料夾。
- 1. 建立 `frontend-angular` 資料夾。
- 1. 在根目錄建立空白的 `docker-compose.yml` 為日後部署做準備。

## Phase 2: AI 大腦 - Python 數據預處理 (Data Preprocessing)

- 1. 進入 `ml-python-engine`，建立 Python 虛擬環境 (`python -m venv venv`)。
- 1. 建立 `requirements.txt`：加入 `pandas`, `scikit-learn`, `spacy`, `fastapi`, `uvicorn`, `joblib`。
- 1. 在 `data/` 內放入 Kaggle 下載的大麻品種資料集 (`strains_dataset.csv`)。
- 1. 建立 `train_pipeline.py` 腳本，引入 pandas 讀取 CSV 檔案。
- 1. 實作缺失值填補：針對數值欄位（如 Rating）填補平均值或中位數。
- 1. 提取文本特徵：將 `Effects` (療效) 和 `Flavor` (風味) 欄位的字串合併為新的 `combined_text` 欄位。
- 1. 下載並載入 SpaCy 的英文語言模型 (`en_core_web_sm`) 用於文本標註。
- 1. 撰寫 NLP 清洗函式：將 `combined_text` 轉小寫、去除標點符號與停用詞 (Stop Words)。

## Phase 3: AI 大腦 - 機器學習與分群模型 (Model Training)

- 1. 在 `train_pipeline.py` 中引入 `TfidfVectorizer`，將清洗後的文字轉換為 TF-IDF 矩陣。
- 1. 針對化學成分分類（Type: Indica/Sativa/Hybrid），使用 One-Hot Encoding 進行轉換。
- 1. 將 TF-IDF 特徵矩陣與類別數值矩陣合併，形成最終的訓練資料矩陣。
- 1. 引入 `KMeans` 演算法，設定初始的分群數 (例如 `n_clusters=5`)。
- 1. 將訓練資料餵入 KMeans 模型進行擬合 (Fit)。
- 1. 撰寫評估腳本：計算每個 Cluster 的特徵中心，並列印出各群集最常出現的關鍵字（療效/副作用）以驗證邏輯。
- 1. 使用 `joblib` 將訓練好的 KMeans 模型儲存至 `models/kmeans_model.pkl`。
- 1. 使用 `joblib` 將配置好的 TfidfVectorizer 儲存至 `models/tfidf_vectorizer.pkl`。
- 1. 將帶有 Cluster Label 的新資料集匯出為 `data/clustered_strains.csv`。

## Phase 4: AI 大腦 - FastAPI 服務化 (Python API)

- 1. 建立 `main.py` 並初始化 FastAPI 應用程式 (`app = FastAPI()`)。
- 1. 在應用程式啟動事件 (Lifespan) 中，載入那兩個 `.pkl` 模型檔案以及分類好的 CSV 資料。
- 1. 建立 Pydantic 模型 `SymptomRequest`，包含 `symptoms` (字串) 與 `avoid_effects` (字串列表)。
- 1. 建立 Pydantic 模型 `RecommendationResponse` 作為回傳格式。
- 1. 實作 POST 路由 `/api/predict`：接收前端症狀，利用 TF-IDF 將症狀轉為向量。
- 1. 計算該症狀向量屬於哪一個 KMeans 群集 (Cluster)。
- 1. 從該群集中篩選出排除 `avoid_effects` 且評分最高的 Top 3 品種，格式化為 JSON 回傳。

## Phase 5: 強力中樞 - Rust API Gateway 建置 (Rust Setup)

- 1. 進入 `backend-rust-gateway`，執行 `cargo init`。
- 1. 在 `Cargo.toml` 中加入依賴：`axum`, `tokio`, `serde`, `serde_json`, `reqwest`, `tower-http` (CORS)。
- 1. 建立 `src/models.rs`，定義與 Python FastAPI 對接的 Request/Response 結構 (Structs)，並加上 `#[derive(Serialize, Deserialize)]`。
- 1. 建立 `src/services.rs`，撰寫一個非同步函式 `fetch_recommendations_from_ml`。
- 1. 在該函式中使用 `reqwest::Client` 打向 Python 的 `http://localhost:8000/api/predict` 端點。

## Phase 6: 強力中樞 - Rust 路由與邏輯 (Rust Routing)

- 1. 建立 `src/handlers.rs`，實作處理前端請求的 Handler 函式 `get_recommendation_handler`。
- 1. 在 Handler 中接收 JSON Payload，進行基礎資料驗證 (如字串不可為空)。
- 1. 呼叫 `services::fetch_recommendations_from_ml`，並處理網路超時或目標服務離線的錯誤 (Error Handling)。
- 1. 在 `src/main.rs` 中設定 Axum 路由 (Router)，綁定 `/api/v1/recommend` 到剛剛的 Handler。
- 1. 設定 CORS (Cross-Origin Resource Sharing)，允許來自 Angular 開發伺服器 (`http://localhost:4200`) 的請求。
- 1. 啟動 Tokio 運行時，讓 Rust 監聽在 Port 8080。

## Phase 7: 前端體驗 - Angular 專案初始化與結構 (Angular Setup)

- 1. 在根目錄外層，使用 Angular CLI 建立專案：`ng new frontend-angular --routing --style=scss`。
- 1. 進入專案，安裝 Material UI：`ng add @angular/material`。
- 1. 建立核心服務：`ng generate service services/api`，負責與 Rust Gateway 通訊。
- 1. 建立介面 (Interface) 定義檔 `src/app/models/strain.interface.ts`，對齊 Rust 回傳的資料結構。

## Phase 8: 前端體驗 - 介面實作 (UI Components)

- 1. 建立組件：`ng generate component components/symptom-form` (輸入表單區塊)。
- 1. 建立組件：`ng generate component components/recommendation-list` (結果展示區塊)。
- 1. 建立組件：`ng generate component components/strain-card` (單一藥品卡片)。
- 1. 在 `symptom-form` 中，使用 Angular Reactive Forms 建立包含「所需療效」與「避免副作用(Checkboxes)」的表單。
- 1. 實作表單提交流輯：在組件層級訂閱 `ApiService`，發送資料至 Rust (Port 8080)。
- 1. 在發送請求期間，實作一個 Loading 狀態標數 (Spinner)。
- 1. 將回傳的 Top 3 藥品資料透過 `@Input()` 傳遞給 `recommendation-list` 與 `strain-card` 進行渲染。
- 1. 美化 UI：使用 Angular Material 的 Card 組件展示藥品名稱、評分、主要療效與化學成分標籤。

## Phase 9: 整合與部署準備 (Integration & Docker)

- 1. 測試連線：啟動 Python (8000), Rust (8080), Angular (4200)，從網頁送出請求，確認端到端 (End-to-End) 資料流暢通。
- 1. 在 Python 目錄下撰寫 `Dockerfile` (基於 `python:3.10-slim`)，開放 Port 8000。
- 1. 在 Rust 目錄下撰寫 `Dockerfile` (使用 Multi-stage build 以縮小體積)，開放 Port 8080。
- 1. 在 Angular 目錄下撰寫 `Dockerfile` (基於 Nginx 編譯靜態資源)，開放 Port 80。
- 1. 回到根目錄的 `docker-compose.yml`，定義 `frontend`, `gateway`, `ml-engine` 三個服務，並設定對應的 Ports 與內部網路 (Network)。
- 1. 執行 `docker-compose up --build` 確保整個微服務集群能夠一鍵順利啟動。
- 1. 撰寫簡單的測試腳本 (Shell 或 Postman Collection) 驗證生產環境 API 端點是否正常回應。
- 1. 整理root folder的readme.md

