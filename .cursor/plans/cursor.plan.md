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

# Cursor Plan: ERH 架構重整、量子升級與論文中期改進

## Context

本計畫依據審稿者對實用性 (3/5) 的批評，結合架構與程式碼改進需求：

1. **Code duplication**: Core logic distributed across `erh/`, `erh_core/`, and `erh-security-app/backend/app/erh_security/`
2. **Quantum model**: 目前 quantum simulation 使用 rotation gates (Maps difficulty to θ)；需 physics-based Ising Hamiltonian 以對齊 ERH 論述
3. **Pipeline gaps**: 部分腳本使用不同流程；GitHub Actions 可能未充分利用平行執行
4. **Paper feedback**: 審稿者要求強化 V(a)/c(a) 操作型定義、深化 ERH 分析、ζ_E(s) 解釋、視覺化改進

## Goals

1. **Refactor**: Consolidate core logic into `erh_core` as Single Source of Truth
2. **Quantum**: 確保 SocialDynamicsQuantumSimulator (Ising model) 完整整合；新增 `measure_social_tension()` API
3. **Pipeline**: 增強 `run_simulation_batch.py` 支援 ABMSimulator 模式；新增 EVS 指標
4. **Paper**: 實作審稿意見（V(a)/c(a) 操作定義、ERH 必要 vs 充分、ζ_E 零點/極點、圖表）

---

## Part A: 論文審稿意見改進

### 現況

- 論文已有 [Section 3.4 操作定義](ethical_riemann_hypothesis.tex)（第 328–337 行），簡述 principle conflict count、token-length proxy、ground truth proxy
- 程式已實作 `GroundTruthProxy`（[judgement_system.py](simulation/core/judgement_system.py)）、`calculate_complexity`（[action_space.py](simulation/core/action_space.py)）
- 結論（第 511 行）已點出 ERH 為必要非充分條件及雙指標
- [zeta_function.py](simulation/analysis/zeta_function.py) 已有 `detect_zeros`、`detect_poles`
- `generate_all_figures.py` 產出 `paper_fig2_error_growth.pdf`、`paper_fig7_critical_bound.pdf`、`paper_fig8_ethical_primes_map.pdf`

### A1. 強化 V(a) 與 c(a) 的操作型定義

- **A1.1** 在 [ethical_riemann_hypothesis.tex](ethical_riemann_hypothesis.tex) Formalization 後新增獨立小節「近似真實道德值 V(a)」
  - **問題**：$V(a)$ 為「上帝視角」，實務上不可直接取得
  - **代理方案**：RLHF 人類標註、Bradley-Terry 從 pairwise 推估、`GroundTruthProxy.from_mock_rlhf()` / `load_from_csv()` 對應流程
  - **限制**：代理偏差、不同 proxy 的影響
- **A1.2** 擴充 Section 3.4「Operationalizing Complexity」中的 c(a) 計算
  - 以條列明文化：$c(a)$ = 道德原則衝突數量（例如誠實 vs 不傷害 = 2）
  - Token-length proxy: $\log(1 + \text{word count})$ 作為推理複雜度
  - 引用 [simulation/core/action_space.py](simulation/core/action_space.py) 的 `count_principle_conflicts()`、`calculate_complexity()`

### A2. 深化實驗分析（ERH 必要非充分）

- **A2.1** 在 Results 章節新增小節「ERH 作為必要條件的含義」
  - 說明 ERH 為結構穩定性必要條件，非充分條件
  - 以 Conservative Judge 為例：可滿足 ERH 但準確度低
  - 強調雙重指標：準確度（MAE、F1、Mistake Rate）+ 結構穩定性（α、ERH 滿足與否）
- **A2.2** 在 Comparative Analysis 中擴充 Table 欄位
  - 欄位：Judge | Mistake Rate | MAE | F1 | α | ERH | 綜合解讀
  - 使用 [erh_core/analysis/statistics.py](erh_core/analysis/statistics.py) `compare_judges()` 輸出

### A3. 擴充倫理 Zeta 函數 ζ_E(s) 解釋

- **A3.1** 在 Ethical Zeta Function 小節（約第 247–261 行）後新增 1–2 段
  - **零點 (zeros)**：$E(x) \approx 0$ 的複雜度點，對應判斷系統在該層級的結構性修正
  - **極點 (poles)**：$|E(x)|$ 突增點，對應「道德相變」(Moral Phase Transition)
  - 相變意涵：複雜度跨過臨界點時錯誤可能崩潰式爆發，類似 spin glass frustration
- **A3.2** 連結 Section 3.6 量子相變內容與 ζ_E(s) 極點
  - 引用 `detect_poles()` 定義：$|E(x)| > 3 \times \text{median}(|E|)$ 視為 spike

### A4. 視覺化改進

- **A4.1** 在 Results 章節插入三張關鍵圖


| 圖表                  | 內容                          | 檔案路徑                                |
| ------------------- | --------------------------- | ----------------------------------- |
| 誤差 vs 複雜度 log-log 圖 | $                           | E(x)                                |
| 倫理質數分佈圖             | 行動空間中倫理質數 2D 散佈（複雜度 vs 重要性） | `paper_fig8_ethical_primes_map.pdf` |
| Judge 比較圖           | 多 Judge 的 E(x) 比較           | `paper_fig3_judge_comparison.pdf`   |


- **A4.2** 補齊 `fig:comparison` 引用：將上述其一包成 figure 並設 `\label{fig:comparison}`
- **A4.3** 確保 `generate_all_figures` 在 LaTeX 編譯前執行；LaTeX 使用 `\IfFileExists` 做 fallback

### A5. 論文改進驗證標準

- 論文包含「近似 V(a)」的獨立討論與 proxy 說明
- c(a) 的計算方式以公式或條列明確寫出
- Results 章節包含 ERH 必要非充分與雙指標討論
- ζ_E(s) 零點、極點與道德相變的對應已在正文說明
- 三張關鍵圖已納入並正確引用
- `fig:comparison` 已定義且無未解析引用

---

## Part B: 架構重整（三重冗餘修復）

### B1. 確立 erh_core 為 Single Source of Truth

- **B1.1** 分析 `erh/` vs `erh_core/` 差異
- **B1.2** 確保 [pyproject.toml](pyproject.toml) 的 `packages.find` 包含 `erh_core`

### B2. 處理 erh/ 與 erh_core 重疊

- **B2.1** 將 `erh/core/` 改為 thin re-export 或刪除重複
- **B2.2** 保留 `erh/tools/`、`erh/client.py` 等非重疊模組

### B3. 重構 erh-security-app 依賴

- **B3.1** 修改 [erh-security-app/backend/requirements.txt](erh-security-app/backend/requirements.txt) 新增 `-e ../..`
- **B3.2** 審查 [erh_security/](erh-security-app/backend/app/erh_security/)
- **B3.3** 更新 [metrics.py](erh-security-app/backend/app/erh_security/metrics.py) import 為 `erh_core`

### B4. 驗證架構重整

- 執行 `pytest erh-security-app/backend/tests/` 與 `pytest tests/`

---

## Part C: 量子模擬器「物理化」升級

### C1. SocialDynamicsQuantumSimulator 增強

- **C1.1** 新增 `measure_social_tension(self, interaction_matrix, biases) -> float`
- **C1.2** 確認 Hamiltonian 符合 $H = \sum J_{ij} Z_i Z_j + \sum h_i X_i$

### C2. Hybrid Model 整合

- **C2.1** 將 `social_tension_energy` 寫入 `results['quantum_stability']`
- **C2.2** 新增 `quantum_energy`、`von_neumann_entropy` 至 simulation history

### C3. 視覺化與 LaTeX

- **C3.1** 新增 `plot_social_tension_vs_time()`
- **C3.2** 新增「Quantum Ising Model of Social Conflict」小節

---

## Part D: 自動化腳本與 Pipeline

### D1. run_simulation_batch.py 增強

- **D1.1** 新增 `--mode judge|abm`（預設 `judge`）
- **D1.2** 實作 ABMSimulator worker
- **D1.3** 支援 `--output` 指定輸出 JSON 路徑

### D2. Ethical Viability Score (EVS)

- **D2.1** 新增 `calculate_evs(stability, fairness, polarization)`
- **D2.2** 在 `compare_judges()` 中納入 EVS

### D3–D4. Phase Transition 圖與 GitHub Actions

- **D3.1** 新增 `plot_phase_transition_error_vs_complexity()`
- **D4.1** 確認 simulation.yml 使用 `run_simulation_batch.py --instances 4`

---

## Part E: 文檔與最終驗證

- **E1** 更新 README：新架構、安裝方式、ABMSimulator vs judge 模式
- **E2** 更新 LaTeX：引用 batch 產生的新圖表
- **E3** 端到端驗證：batch → 圖表 → LaTeX 編譯
- **E4** pytest 全數通過

---

## 檔案變更總覽


| 類型    | 檔案                                                                   | 變更                                                |
| ----- | -------------------------------------------------------------------- | ------------------------------------------------- |
| LaTeX | ethical_riemann_hypothesis.tex                                       | A1–A4 論文改進                                        |
| LaTeX | ethical_riemann_hypothesis_en.tex, ethical_riemann_hypothesis_zh.tex | 同步改動（若有）                                          |
| 腳本    | scripts/integrate_figures.py, scripts/update_latex.py                | 圖表整合（若需）                                          |
| 架構    | erh-security-app/backend/requirements.txt                            | 新增 `-e ../..`                                     |
| 架構    | erh-security-app/backend/app/erh_security/metrics.py                 | import 改為 erh_core                                |
| 架構    | erh/core/ 或 erh/                                                     | B1–B2 重整                                          |
| 量子    | simulation/quantum/simulator.py                                      | measure_social_tension()                          |
| 量子    | erh_core/core/hybrid_model.py                                        | quantum_energy 寫入 history                         |
| 腳本    | scripts/run_simulation_batch.py                                      | ABMSimulator 模式、EVS                               |
| 分析    | erh_core/analysis/statistics.py                                      | calculate_evs()                                   |
| 視覺    | simulation/visualization/plots.py                                    | plot_social_tension_vs_time、plot_phase_transition |
| 文檔    | README.md                                                            | 架構說明                                              |


---

## 執行順序建議

```mermaid
flowchart TD
    subgraph paper [論文改進]
        A1[1. 新增 V(a) 近似小節] --> A2[2. 擴充 c(a) 操作定義]
        A2 --> A3[3. 深化 ERH 必要非充分討論]
        A3 --> A4[4. 擴充 Zeta 零點/極點解釋]
        A4 --> A5[5. 補齊 LaTeX 圖表與 fig:comparison]
    end
    subgraph arch [架構重整]
        B1[B1 分析 erh vs erh_core] --> B2[B2 重整 erh/]
        B2 --> B3[B3 更新 erh-security-app]
        B3 --> B4[B4 驗證架構]
    end
    subgraph quantum [量子升級]
        C1[C1 measure_social_tension] --> C2[C2 Hybrid 整合]
        C2 --> C3[C3 視覺化與 LaTeX]
    end
    subgraph pipeline [Pipeline]
        D1[D1 run_simulation_batch] --> D2[D2 EVS]
        D2 --> D3[D3 Phase Transition 圖]
        D3 --> D4[D4 GitHub Actions]
    end
    A5 --> E[E 文檔與驗證]
    B4 --> E
    C3 --> E
    D4 --> E
```



