# erh/ vs erh_core/ 差異分析 (B1.1)

## 目的

確立 `erh_core` 為 Single Source of Truth，釐清 `erh/` 與 `erh_core/` 的模組差異。

## 模組對照

| 模組 | erh/core/ | erh_core/core/ | 說明 |
|------|-----------|----------------|------|
| action_space | ✓ | ✓ | 重複；erh_core 為 canonical |
| judgement_system | ✓ | ✓ | 重複 |
| ethical_primes | ✓ | ✓ | 重複；erh 多 ethical_primality_test |
| agent | ✓ | ✓ | 重複 |
| social_network | ✓ | ✓ | 重複 |
| meta_monitor | ✓ | ✓ | 重複 |
| abm_simulator | ✓ | ✓ | 重複 |
| hybrid_model | ✓ | ✓ | 重複 |
| temporal_erh | ✓ | ✓ | 重複 |
| scenario_generator | ✓ | ✗ | **erh 獨有** |
| adaptive_threshold | ✗ | ✓ | erh_core 獨有 |
| axioms | ✗ | ✓ | erh_core 獨有 |
| fuzzy_judgment | ✗ | ✓ | erh_core 獨有 |
| output_writer | ✗ | ✓ | erh_core 獨有 |
| prime_dependency_graph | ✗ | ✓ | erh_core 獨有 |
| probabilistic_values | ✗ | ✓ | erh_core 獨有 |

## 結論

- **erh_core** 為更完整的核心，含額外模組（axioms, output_writer, prime_dependency_graph 等）
- **erh** 獨有 `scenario_generator`（action_to_scenario_text, actions_to_prompts）
- **建議**：erh/core 對重疊模組改為 re-export erh_core；保留 scenario_generator 從 erh 本機導入
