# Expand Plan 44 子任務稽核報告

## 完成狀態總覽

| 區塊 | 已完成 | 待修正／增强 |
|------|--------|--------------|
| Quantum (q1–q10) | 10 | 0 |
| Real Data (r1–r12) | 12 | 2 bug |
| Visualization (v1–v11) | 11 | 1 enhance |
| Paper (p1–p6) | 6 | 0 |
| Integration (i1–i5) | 5 | 0 |
| **總計** | **44** | **3** |

---

## 已發現問題

### 1. **[BUG] social_i_qa 資料集載入錯誤** (r4)

- **現狀**：`load_dataset("social_i_qa", "social_i_qa")` 可能失敗
- **正確**：`load_dataset("allenai/social_i_qa")`（HuggingFace 官方路徑）
- **欄位**：`answer` 應改為 `answerA`/`answerB`/`answerC` 或 `label`

### 2. **[BUG] Firecrawl API 不相容** (r6)

- **現狀**：使用 `FirecrawlApp` 與 `scrape_url()`，新 SDK 已改為 `Firecrawl` 與 `scrape()`
- **問題**：`AttributeError: 'FirecrawlApp' object has no attribute 'scrape_url'`
- **建議**：同時支援新舊 API，或改為使用 `Firecrawl.scrape()`

### 3. **[ENHANCE] ingestion 路徑解析** (r10/r11)

- **現狀**：`_erh_root = Path(__file__).resolve().parents[4]` 假設 monorepo 結構
- **風險**：若 backend 單獨部署（無上層 Ethic-Latex），會找不到 `simulation`
- **建議**：加入 fallback 或環境變數 `ERH_PROJECT_ROOT`

### 4. **[ENHANCE] plot_normalized_error_growth 邊界情況**

- **現狀**：`np.max(ratio) * 0.8` 在 ratio 全為負或全為 0 時可能產生不當註解位置
- **建議**：使用 `np.nanmax(np.abs(ratio))` 或加入邊界檢查

---

## 尚未實作但可接受

- **p4 標題**：Plan 寫「4.3 Empirical Feasibility」；LaTeX 使用「4.3 Empirical Validation Framework」，語意一致。
- **API 路徑**：Plan 寫 `/ingest/huggingface`；實際為 `/ingestion/huggingface`（與現有 router 前綴一致）。
