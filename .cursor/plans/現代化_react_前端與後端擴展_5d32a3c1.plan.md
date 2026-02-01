---
name: 現代化 React 前端與後端擴展
overview: ""
todos: []
isProject: false
---

# 現代化 React 前端與後端擴展

## 目標

構建一個現代化的、生產就緒的 React 前端應用，擴展 FastAPI 後端以支持 LaTeX 驗證、模擬和安全性分析，並建立完整的 Docker 容器化環境。

## 當前狀況

- **前端**：Next.js 14（基礎實現，需要完全重構）
- **後端**：FastAPI（已有基本 API，需要擴展）
- **數據庫**：SQLite（需要遷移到 PostgreSQL）
- **容器化**：無（需要添加 Docker 支持）

## 實施方案

### 階段 1：前端架構設置

#### 1.1 初始化 Vite + React 項目

**目標**：創建新的 Vite + React 18 + TypeScript 項目結構

**步驟**：

1. 在 `erh-security-app/` 下創建新的 `frontend-vite/` 目錄
2. 使用 `npm create vite@latest frontend-vite -- --template react-ts` 初始化項目
3. 配置 Vite 以支持路徑別名和環境變量
4. 設置 TypeScript 配置（`tsconfig.json`）

**文件結構**：

```
frontend-vite/
├── src/
│   ├── api/              # API 客戶端定義
│   ├── components/       # 可重用 UI 組件
│   │   ├── editor/       # LaTeX 編輯器組件
│   │   ├── dashboard/    # 儀表板組件
│   │   ├── layout/       # 布局組件
│   │   └── ui/           # shadcn/ui 組件
│   ├── hooks/            # 自定義 React hooks
│   ├── pages/            # 頁面級組件
│   ├── store/            # 全局狀態管理
│   └── types/            # TypeScript 類型定義
├── public/
├── package.json
├── vite.config.ts
└── tsconfig.json
```

#### 1.2 安裝和配置核心依賴

**依賴安裝**：

- `react` 18+, `react-dom` 18+
- `@tanstack/react-query` (數據獲取和緩存)
- `zustand` 或 `jotai` (狀態管理)
- `react-router-dom` (路由)
- `axios` (HTTP 客戶端)
- `tailwindcss`, `postcss`, `autoprefixer`
- `shadcn/ui` 組件庫
- `react-katex` 或 `react-mathjax` (LaTeX 渲染)
- `recharts` 或 `@visx/visx` (數據可視化)
- `lucide-react` (圖標)
- `monaco-editor` (代碼編輯器)

**配置文件**：

- `tailwind.config.js` - Tailwind CSS 配置
- `components.json` - shadcn/ui 配置
- `.env` - 環境變量（API 基礎 URL）

### 階段 2：shadcn/ui 設置和基礎組件

#### 2.1 初始化 shadcn/ui

**步驟**：

1. 運行 `npx shadcn-ui@latest init`
2. 安裝核心組件：Button, Card, Input, Select, Tabs, Dialog, Badge
3. 配置主題（實驗室風格：深色背景、高對比度）

#### 2.2 創建基礎布局組件

**組件**：

- `Layout.tsx` - 主布局（側邊欄 + 主內容區）
- `Sidebar.tsx` - 導航側邊欄
- `Header.tsx` - 頂部導航欄
- `PageWrapper.tsx` - 頁面容器

### 階段 3：API 層和類型定義

#### 3.1 創建 API 客戶端

**文件**：`src/api/client.ts`

- 配置 Axios 實例（基礎 URL、攔截器）
- 錯誤處理中間件
- 請求/響應類型定義

#### 3.2 定義 API 端點

**文件**：`src/api/endpoints/`

- `health.ts` - 健康檢查
- `latex.ts` - LaTeX 驗證端點
- `simulation.ts` - 模擬端點
- `analysis.ts` - 分析端點（擴展現有）
- `security.ts` - 安全性報告端點

#### 3.3 TypeScript 類型定義

**文件**：`src/types/`

- `api.ts` - API 請求/響應類型
- `latex.ts` - LaTeX 相關類型
- `simulation.ts` - 模擬數據類型
- `security.ts` - 安全性相關類型

### 階段 4：核心頁面實現

#### 4.1 對齊編輯器頁面（Alignment Editor）

**文件**：`src/pages/Editor.tsx`

**功能**：

- 分屏界面（左：Monaco Editor，右：LaTeX 預覽 + 驗證分數）
- 實時 LaTeX 渲染（使用 react-katex）
- 語法高亮和錯誤標記
- 與後端驗證 API 集成
- 保存/加載功能

**組件**：

- `LatexEditor.tsx` - Monaco Editor 包裝器
- `LatexPreview.tsx` - LaTeX 渲染組件
- `ValidationPanel.tsx` - 驗證結果顯示
- `SecurityBadge.tsx` - 安全性狀態徽章

#### 4.2 安全性與倫理儀表板

**文件**：`src/pages/Dashboard.tsx`

**功能**：

- 風險熱圖（可視化倫理規則的"薄弱"區域）
- Linter 統計圖表（最常見的安全警告）
- 活動摘要（來自後端的實時日誌）
- ERH 指標概覽

**組件**：

- `RiskHeatmap.tsx` - 風險熱圖可視化
- `LinterStats.tsx` - Linter 統計圖表
- `ActivityFeed.tsx` - 活動摘要組件
- `ERHMetricsCard.tsx` - ERH 指標卡片

#### 4.3 模擬（Psychohistory）可視化器

**文件**：`src/pages/Simulation.tsx`

**功能**：

- 交互式時間線/圖表顯示倫理規則隨時間的演變
- 圖像集成（自動獲取並顯示 Python 生成的 PNG/SVG）
- 播放控制（逐步查看模擬結果）
- 參數調整界面

**組件**：

- `SimulationTimeline.tsx` - 時間線可視化
- `SimulationPlayer.tsx` - 播放控制組件
- `ParameterControls.tsx` - 參數調整界面
- `FigureViewer.tsx` - 圖像查看器

#### 4.4 設置頁面

**文件**：`src/pages/Settings.tsx`

**功能**：

- SDK 配置管理
- API 密鑰管理
- 主題設置
- 數據導出/導入

### 階段 5：後端擴展

#### 5.1 重構後端目錄結構

**新結構**：

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── rules.py      # LaTeX 規則 CRUD
│   │   │   │   ├── verify.py     # LaTeX 驗證（與 erh_core 集成）
│   │   │   │   ├── simulate.py   # 模擬端點
│   │   │   │   ├── analysis.py   # 分析端點（擴展現有）
│   │   │   │   └── security.py   # 安全性報告
│   │   │   └── api.py            # API 路由器
│   ├── core/                     # 應用配置和安全
│   ├── models/                   # SQLAlchemy 模型
│   ├── schemas/                  # Pydantic 模式
│   ├── services/                 # 業務邏輯層（橋接到 erh_core）
│   │   ├── latex_service.py      # LaTeX 驗證服務
│   │   ├── simulation_service.py # 模擬服務
│   │   └── security_service.py   # 安全性分析服務
│   ├── db/                       # 數據庫連接
│   └── main.py                   # FastAPI 入口點
├── tests/
├── Dockerfile
├── .env
└── requirements.txt
```

#### 5.2 數據庫遷移到 PostgreSQL

**步驟**：

1. 更新 `app/core/db.py` 以支持 PostgreSQL
2. 創建 Alembic 遷移文件
3. 更新 `app/core/models.py` 以添加新表：
  - `Users` - 用戶認證
  - `LatexRules` - 存儲 LaTeX 規則
  - `SecurityReports` - 安全性報告
  - `Simulations` - 模擬歷史
4. 更新環境變量配置

**新模型**：

- `User` - 用戶表（id, email, hashed_password）
- `LatexRule` - LaTeX 規則表（id, title, content, owner_id, created_at）
- `SecurityReport` - 安全性報告表（id, rule_id, risk_score, violations JSON）
- `Simulation` - 模擬表（id, status, result_path, timestamp）

#### 5.3 實現新的 API 端點

**端點實現**：

1. **LaTeX 驗證** (`/api/v1/verify`)
  - `POST /api/v1/verify` - 驗證 LaTeX 代碼
  - 與 `erh_core` 集成進行驗證
  - 返回驗證結果和安全性評分
2. **規則管理** (`/api/v1/rules`)
  - `GET /api/v1/rules` - 獲取所有規則
  - `POST /api/v1/rules` - 創建新規則
  - `PUT /api/v1/rules/{id}` - 更新規則
  - `DELETE /api/v1/rules/{id}` - 刪除規則
3. **模擬** (`/api/v1/simulate`)
  - `POST /api/v1/simulate` - 運行模擬
  - `GET /api/v1/simulate/{id}` - 獲取模擬結果
  - 與 `simulation/` 模組集成
4. **安全性報告** (`/api/v1/security`)
  - `GET /api/v1/security/reports` - 獲取報告列表
  - `POST /api/v1/security/analyze` - 分析規則安全性

#### 5.4 服務層實現

**服務文件**：

- `services/latex_service.py` - 封裝 `erh_core` 驗證邏輯
- `services/simulation_service.py` - 封裝 `simulation/` 模擬邏輯
- `services/security_service.py` - 安全性分析邏輯

### 階段 6：Docker 容器化

#### 6.1 後端 Dockerfile

**文件**：`erh-security-app/backend/Dockerfile`

- 基於 Python 3.11-slim
- 安裝系統依賴（PostgreSQL 客戶端）
- 複製並安裝 Python 依賴
- 暴露端口 8000

#### 6.2 前端 Dockerfile

**文件**：`erh-security-app/frontend-vite/Dockerfile`

- 多階段構建（構建階段 + 生產階段）
- 使用 Node.js 18+
- 構建 Vite 應用
- 使用 Nginx 提供靜態文件

#### 6.3 Docker Compose 配置

**文件**：`docker-compose.yml`（項目根目錄）

**服務**：

- `db` - PostgreSQL 15
- `api` - FastAPI 後端
- `frontend` - React 前端

**配置**：

- 環境變量管理
- 卷掛載（數據持久化）
- 網絡配置
- 健康檢查

### 階段 7：高級功能組件

#### 7.1 LaTeX 編輯器組件

**組件**：`components/editor/LatexEditor.tsx`

- Monaco Editor 集成
- 語法高亮（LaTeX）
- 自動完成
- 錯誤標記
- 與驗證 API 實時同步

#### 7.2 規則樹組件

**組件**：`components/RuleTree.tsx`

- 樹形視圖顯示 `.cursor/rules` 和功能
- 可展開/折疊節點
- 點擊導航到對應規則
- 搜索功能

#### 7.3 SDK 控制台組件

**組件**：`components/SDKConsole.tsx`

- 終端界面
- 執行 js-sdk 命令
- 顯示輸出結果
- 命令歷史

#### 7.4 模擬播放器組件

**組件**：`components/SimulationPlayer.tsx`

- 播放控制（播放/暫停/步進）
- 時間軸滑塊
- 參數顯示
- 結果可視化

### 階段 8：狀態管理和數據獲取

#### 8.1 設置 TanStack Query

**配置**：

- QueryClient 設置
- 默認查詢選項
- 錯誤處理
- 緩存策略

#### 8.2 自定義 Hooks

**Hooks**：

- `useSimulation.ts` - 模擬數據獲取
- `useLatexVerification.ts` - LaTeX 驗證
- `useSecurityReports.ts` - 安全性報告
- `useRules.ts` - 規則管理

#### 8.3 全局狀態管理

**使用 Zustand 或 Jotai**：

- 用戶認證狀態
- UI 狀態（側邊欄展開/折疊）
- 編輯器狀態
- 主題設置

### 階段 9：路由和導航

#### 9.1 路由配置

**使用 React Router**：

- `/` - 儀表板
- `/editor` - LaTeX 編輯器
- `/simulation` - 模擬可視化
- `/settings` - 設置
- `/rules` - 規則管理

#### 9.2 導航組件

**組件**：

- `Navigation.tsx` - 主導航
- `Breadcrumbs.tsx` - 麵包屑導航
- `Sidebar.tsx` - 側邊欄導航

### 階段 10：測試和文檔

#### 10.1 前端測試

- 單元測試（Vitest）
- 組件測試（React Testing Library）
- E2E 測試（Playwright 或 Cypress）

#### 10.2 後端測試

- 單元測試（pytest）
- API 測試（FastAPI TestClient）
- 集成測試

#### 10.3 文檔

- API 文檔（Swagger/OpenAPI）
- 前端組件文檔（Storybook）
- 部署文檔
- 開發者指南

## 關鍵文件清單

### 需要創建的前端文件

- `frontend-vite/src/api/client.ts` - API 客戶端
- `frontend-vite/src/pages/Dashboard.

