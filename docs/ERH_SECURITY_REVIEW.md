# erh_security 審查 (B3.2)

## 目的

審查 `erh-security-app/backend/app/erh_security/` 是否為單純重複或應用層適配器。

## 模組說明

| 檔案 | 用途 | 結論 |
|------|------|------|
| code_complexity.py | 計算程式碼複雜度（DevSecOps 用） | **應用層適配器**：將 GitLab/程式碼結構映射為 ERH 複雜度 |
| mapping.py | ErhSample、build_erh_dataset、compute_complexity 等 | **應用層適配器**：將 DB 模型映射為 ERH 分析所需格式 |
| metrics.py | compute_delta、is_mistake、analyze_erh_structure | **應用層適配器**：呼叫 erh_core 的 ethical_primes，介面為 ErhSample |

## 結論

- **非單純重複**：erh_security 為 ERH-on-Security PoC 的應用層適配器
- **應保留**：需將 DevSecOps 資料映射為 ERH 分析輸入
- **依賴**：metrics.py 已改為優先 import erh_core.core.ethical_primes（B3.3）
