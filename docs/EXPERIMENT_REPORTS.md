# Experiment and Test Reports

This document aggregates selected reports produced by the ERH simulation framework, real-data case studies, and psychohistory integration tests.

In the summary tables, the column **Within ERH-style bound?** refers to whether the estimated growth exponent $\alpha$ stays at or below an ERH-style worst-case target (roughly $\alpha \approx 0.5$). A "No" entry in these tables indicates that the system's error grows *more slowly* than the worst-case bound (i.e., it is overly conservative), not that it explodes beyond the bound.


---

## simulation/output/psychohistory_tests/test_summary.txt


======================================================================
PSYCHOHISTORY SIMULATION TEST REPORT
======================================================================

Total Tests: 43
Passed: 40
Failed: 1
Success Rate: 93.0%
Total Time: 144.89s

Timestamp: 2025-12-01T17:02:57.552629

======================================================================
DETAILED RESULTS
======================================================================

Test: param_sweep_agents10_toporandom_steps5
  Status: PASSED
  Time: 0.18s

Test: param_sweep_agents10_toporandom_steps10
  Status: PASSED
  Time: 0.25s

Test: param_sweep_agents10_toporandom_steps20
  Status: PASSED
  Time: 0.43s

Test: param_sweep_agents10_toposmall_world_steps5
  Status: PASSED
  Time: 0.14s

Test: param_sweep_agents10_toposmall_world_steps10
  Status: PASSED
  Time: 0.25s

Test: param_sweep_agents10_toposmall_world_steps20
  Status: PASSED
  Time: 0.56s

Test: param_sweep_agents10_toposcale_free_steps5
  Status: PASSED
  Time: 0.19s

Test: param_sweep_agents10_toposcale_free_steps10
  Status: PASSED
  Time: 0.27s

Test: param_sweep_agents10_toposcale_free_steps20
  Status: PASSED
  Time: 0.52s

Test: param_sweep_agents50_toporandom_steps5
  Status: PASSED
  Time: 0.65s

Test: param_sweep_agents50_toporandom_steps10
  Status: PASSED
  Time: 0.80s

Test: param_sweep_agents50_toporandom_steps20
  Status: PASSED
  Time: 2.20s

Test: param_sweep_agents50_toposmall_world_steps5
  Status: PASSED
  Time: 0.51s

Test: param_sweep_agents50_toposmall_world_steps10
  Status: PASSED
  Time: 1.36s

Test: param_sweep_agents50_toposmall_world_steps20
  Status: PASSED
  Time: 2.92s

Test: param_sweep_agents50_toposcale_free_steps5
  Status: PASSED
  Time: 0.79s

Test: param_sweep_agents50_toposcale_free_steps10
  Status: PASSED
  Time: 1.28s

Test: param_sweep_agents50_toposcale_free_steps20
  Status: PASSED
  Time: 2.23s

Test: param_sweep_agents100_toporandom_steps5
  Status: PASSED
  Time: 0.96s

Test: param_sweep_agents100_toporandom_steps10
  Status: PASSED
  Time: 1.43s

Test: param_sweep_agents100_toporandom_steps20
  Status: PASSED
  Time: 3.33s

Test: param_sweep_agents100_toposmall_world_steps5
  Status: PASSED
  Time: 0.92s

Test: param_sweep_agents100_toposmall_world_steps10
  Status: PASSED
  Time: 1.41s

Test: param_sweep_agents100_toposmall_world_steps20
  Status: PASSED
  Time: 3.62s

Test: param_sweep_agents100_toposcale_free_steps5
  Status: PASSED
  Time: 1.53s

Test: param_sweep_agents100_toposcale_free_steps10
  Status: PASSED
  Time: 3.07s

Test: param_sweep_agents100_toposcale_free_steps20
  Status: PASSED
  Time: 4.78s

Test: param_sweep_agents200_toporandom_steps5
  Status: PASSED
  Time: 1.69s

Test: param_sweep_agents200_toporandom_steps10
  Status: PASSED
  Time: 4.77s

Test: param_sweep_agents200_toporandom_steps20
  Status: PASSED
  Time: 8.49s

Test: param_sweep_agents200_toposmall_world_steps5
  Status: PASSED
  Time: 1.90s

Test: param_sweep_agents200_toposmall_world_steps10
  Status: PASSED
  Time: 4.58s

Test: param_sweep_agents200_toposmall_world_steps20
  Status: PASSED
  Time: 12.73s

Test: param_sweep_agents200_toposcale_free_steps5
  Status: PASSED
  Time: 2.17s

Test: param_sweep_agents200_toposcale_free_steps10
  Status: PASSED
  Time: 5.75s

Test: param_sweep_agents200_toposcale_free_steps20
  Status: PASSED
  Time: 8.83s

Test: long_term_steps50
  Status: UNSTABLE
  Time: 6.15s

Test: long_term_steps100
  Status: UNSTABLE
  Time: 10.51s

Test: stress_agents200
  Status: PASSED
  Time: 8.70s

Test: stress_agents500
  Status: PASSED
  Time: 24.56s

Test: boundary_minimal
  Status: FAILED
  Error: k>n, choose smaller k or larger n

Test: boundary_small
  Status: PASSED
  Time: 0.05s

Test: boundary_large_agents
  Status: PASSED
  Time: 7.19s


---

## tests/PSYCHOHISTORY_TESTS_README.md


# Psychohistory Integration Tests

## 概述

本文檔說明心理史學整合 ERH 模型的測試實施，包括單元測試、整合測試和模擬測試。

## 已完成的修復

### 1. 導入錯誤修復

**問題**: 測試文件導入時出現 "attempted relative import beyond top-level package" 錯誤

**解決方案**:
- ✅ 修復 `simulation/core/hybrid_model.py` 中的相對導入
- ✅ 修復 `simulation/core/abm_simulator.py` 中的相對導入
- ✅ 修復 `simulation/analysis/opinion_dynamics.py` 中的相對導入
- ✅ 增強測試文件的導入驗證和錯誤處理

**驗證**: 所有測試文件現在可以正確導入
```bash
python tests/verify_tests.py
# 結果: 所有 6 個測試文件導入成功
```

## 測試文件

### 單元測試

1. **test_temporal_erh.py** - 時間序列 ERH 函數測試
2. **test_agent_framework.py** - Agent 框架測試
3. **test_social_network.py** - 社會網絡測試
4. **test_meta_monitor.py** - 元層監控測試
5. **test_hybrid_model.py** - 混合模型測試
6. **test_psychohistory_integration.py** - 整合測試

### 模擬測試腳本

1. **scripts/run_psychohistory_simulations.py** - Python 測試運行器
   - 參數掃描測試（多個參數組合）
   - 長時間模擬測試（50-100 時間步）
   - 壓力測試（200-500 agents）
   - 邊界情況測試

2. **scripts/run_psychohistory_tests.sh** - Shell 測試腳本
   - 支持快速模式 (`--quick`)
   - 完整測試模式

## GitHub Actions 整合

### build_thesis.yml

已添加以下步驟：
1. **執行心理史學整合 notebook** (`08_psychohistory_integration.ipynb`)
2. **運行單元測試** - 所有心理史學相關測試
3. **運行模擬測試** - 快速模式（參數掃描）

### single_sh_based_build_thesis.yml

已添加：
1. **運行單元測試** - 在構建腳本執行前
2. **運行模擬測試** - 快速模式

### build_thesis.sh

已更新：
1. 添加 `08_psychohistory_integration.ipynb` 到 notebook 列表
2. 添加步驟 6.5：運行心理史學模擬測試（快速模式）

## 運行測試

### 本地運行

**單元測試**:
```bash
cd tests
bash run_unit_tests.sh  # Linux/macOS
# 或
run_unit_tests.bat      # Windows
```

**模擬測試**:
```bash
# 快速模式（僅參數掃描）
bash scripts/run_psychohistory_tests.sh --quick

# 完整模式（所有測試）
bash scripts/run_psychohistory_tests.sh
```

**所有測試**:
```bash
cd tests
bash run_all_tests.sh
```

### CI/CD

測試會在以下情況自動運行：
- Push 到 main/master 分支
- Pull Request
- 手動觸發 (workflow_dispatch)

## 測試覆蓋範圍

### 參數掃描測試
- Agent 數量: 10, 50, 100, 200
- 網絡拓撲: random, small_world, scale_free
- 時間步數: 5, 10, 20
- **總計**: ~36 個測試組合

### 長時間模擬測試
- 時間步數: 50, 100
- 驗證系統穩定性

### 壓力測試
- Agent 數量: 200, 500
- 驗證大規模模擬性能

### 邊界情況測試
- 最小配置 (1 agent, 1 time step)
- 小規模配置 (5 agents, 2 time steps)
- 大規模配置 (1000 agents, 5 time steps)

## 測試輸出

測試結果保存在：
- `simulation/output/psychohistory_tests/test_report.json` - JSON 格式詳細報告
- `simulation/output/psychohistory_tests/test_summary.txt` - 文本格式摘要

## 注意事項

1. **CI 環境**: 使用快速模式 (`--quick`) 以節省時間
2. **本地開發**: 可以運行完整測試以獲得全面覆蓋
3. **超時設置**: 長時間模擬可能需要較長時間，考慮增加超時
4. **資源使用**: 大規模模擬（500+ agents）需要較多內存

## 故障排除

### 導入錯誤
如果遇到導入錯誤，確保：
1. `simulation/` 目錄在 `PYTHONPATH` 中
2. 所有依賴已安裝: `pip install -r requirements.txt`

### 測試失敗
檢查：
1. 測試輸出日誌
2. JSON 報告中的錯誤信息
3. 確保輸出目錄可寫入

### CI 失敗
- 檢查 GitHub Actions 日誌
- 驗證所有依賴已正確安裝
- 確認測試超時設置足夠
