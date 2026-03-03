---
name: ERH Phase 4 Verification & Polish
overview: 端到端驗證、CI 整合補齊、run_phase_transition_exp 納入 build_thesis、驗證腳本。
todos:
  - id: p4-1
    content: build_thesis 加入 run_phase_transition_exp 產出 phase_transition.png
    status: completed
  - id: p4-2
    content: build_thesis Prepare Figures（phase_transition 已存 simulation/output/figures）
    status: completed
  - id: p4-3
    content: run_full_pipeline FULL=1 選項加入 generate_all_figures
    status: completed
  - id: p4-4
    content: run_verification_phase4.py 端到端驗證腳本
    status: completed
isProject: false
---

# ERH Phase 4: Verification & Polish

## 對應 update.plan Phase 4 與 cursor.plan Part E

- **E2** 更新 LaTeX：引用 batch 產生的新圖表
- **E3** 端到端驗證：batch → 圖表 → LaTeX 編譯
- **E4** pytest 全數通過

## 目標

1. 確保 build_thesis 能產出 phase_transition.png（LaTeX \IfFileExists 需要）
2. 端到端驗證腳本：batch → phase transition → report → (optional) figures
3. 文檔與 run_full_pipeline 一致性

## 現況

- build_thesis 執行 generate_all_figures（產 comparison_table_rows.tex、results_summary.txt）
- build_thesis 不執行 run_phase_transition_exp → phase_transition.png 可能缺失
- run_full_pipeline 已含 phase transition + report
- run_quantum_phase_transition 與 run_phase_transition_exp 為不同腳本
