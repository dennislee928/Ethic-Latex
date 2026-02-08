---
name: ERH Phase 3 Architecture & Thesis
overview: 延續 Phase 2 完成架構重整、論文審稿強化、量子 LaTeX 小節。對應 cursor.plan.md Part A–E，補齊剩餘項目。
todos:
  - id: p3-a1
    content: A1 強化 V(a)/c(a) 操作定義：補 HuggingFace Oracle、程式引用
    status: in_progress
  - id: p3-a2
    content: A2 ERH 必要條件、比較表（已有骨架，確保 generate 可填）
    status: pending
  - id: p3-a3
    content: A3 ζ_E 零點/極點（已有 line 274，確認完整）
    status: pending
  - id: p3-a4
    content: A4 fig:comparison、圖表（已有，驗證 generate_all_figures）
    status: pending
  - id: p3-b
    content: B3 metrics.py 已用 erh_core；驗證 B4 pytest
    status: pending
  - id: p3-c
    content: C3 plot_social_tension_vs_time、Quantum Ising LaTeX（已有）
    status: pending
  - id: p3-d
    content: D run_simulation_batch、simulation.yml 驗證
    status: pending
  - id: p3-e
    content: E README 架構說明
    status: pending
isProject: false
---

# ERH Phase 3: Architecture & Thesis Improvement

## 與 Phase 2 的銜接

Phase 2 已完成：
- Quantum Core: compute_ground_state, NumPyMinimumEigensolver
- HuggingFace Oracle, OracleDrivenJudge, csv_proxy
- Phase transition: run_phase_transition_exp.py, plot_phase_transition
- Pipeline: generate_comprehensive_report, CI phase-transition job, run_full_pipeline.sh

## Phase 3 目標（對應 cursor.plan.md）

1. **Part A 論文**：V(a)/c(a) 操作定義、ERH 必要非充分、ζ_E 零點/極點、圖表
2. **Part B 架構**：erh_core 為 SSOT、erh-security-app 依賴
3. **Part C 量子**：measure_social_tension、plot_social_tension_vs_time、LaTeX
4. **Part D Pipeline**：run_simulation_batch --mode abm、EVS、phase transition
5. **Part E 文檔**：README 架構說明

## 現況檢查

| 項目 | 狀態 |
|------|------|
| measure_social_tension() | ✅ simulator.py |
| calculate_evs() | ✅ statistics.py |
| plot_social_tension_vs_time | ✅ plots.py |
| plot_phase_transition_error_vs_complexity | ✅ plots.py |
| run_simulation_batch --mode abm | ✅ |
| erh-security-app -e ../.. | ✅ requirements.txt |
| metrics.py erh_core | ✅ |
| fig:comparison, ERH 必要條件 | ✅ LaTeX |
| Approximating V(a) | ✅ LaTeX 3.2 |
| Operationalizing c(a) | ✅ LaTeX 3.4 |

## 待補項目

1. **A1**：在「Approximating V(a)」小節加入 HuggingFaceEthicalOracle 與 load_from_csv 並存說明
2. **A2**：確保 generate_comprehensive_report 或 compare_judges 可產出填表用數據
3. **B4**：pytest 驗證
4. **E1**：README 架構說明更新
