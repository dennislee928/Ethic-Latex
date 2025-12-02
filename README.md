# Ethical Riemann Hypothesis

A mathematical framework for analyzing moral judgment errors through an analogy with the Riemann Hypothesis in number theory.

## Project Overview

This project introduces the **Ethical Riemann Hypothesis (ERH)**, which states that in a "healthy" moral judgment system, the error in predicting critical misjudgments grows at most like √x, where x is the complexity of the decision.

### Key Concepts

- **Ethical Primes**: Critical misjudgments that represent fundamental errors
- **Π(x)**: Count of ethical primes up to complexity x
- **E(x) = Π(x) - B(x)**: Error term comparing actual vs expected distribution
- **ERH**: |E(x)| ≤ C·x^(1/2 + ε) for healthy judgment systems

### Analogy with Number Theory

| Number Theory | Ethical Judgment |
|---------------|------------------|
| Prime numbers | Ethical primes (critical misjudgments) |
| π(x) | Π(x) (ethical prime count) |
| Prime Number Theorem | Baseline expectation B(x) |
| Riemann Hypothesis | Ethical Riemann Hypothesis |

## Project Structure

```
Ethic-Latex/
├── simulation/                    # Python simulation framework
│   ├── core/                     # Core modules
│   │   ├── action_space.py      # Action and world generation
│   │   ├── judgement_system.py  # Judge implementations
│   │   └── ethical_primes.py    # Prime selection and analysis
│   ├── analysis/                # Analysis tools
│   │   ├── zeta_function.py    # Ethical zeta function
│   │   └── statistics.py       # Statistical analysis
│   ├── visualization/           # Plotting utilities
│   │   └── plots.py            # All visualization functions
│   ├── notebooks/              # Jupyter notebooks
│   │   ├── 01_basic_simulation.ipynb
│   │   ├── 02_judge_comparison.ipynb
│   │   ├── 03_zeta_zeros.ipynb
│   │   ├── 04_parameter_sensitivity.ipynb
│   │   ├── 05_generate_paper_figures.ipynb
│   │   ├── 06_baseline_comparison.ipynb
│   │   └── 07_zeta_zeros_deep_analysis.ipynb
│   ├── output/                 # Generated outputs
│   │   └── figures/           # Saved figures
│   └── README.md              # Simulation documentation
├── scripts/                    # Utility scripts
│   ├── install_dependencies.*  # Dependency installation
│   ├── start_jupyter.*         # Jupyter server launcher
│   ├── compile_latex.*         # LaTeX compilation
│   └── quick-start-script/     # Quick start scripts
├── docs/                       # Documentation files
│   ├── INSTALL.md             # Installation guide
│   ├── USAGE.md               # Usage guide
│   ├── QUICKSTART.md          # Quick start guide
│   └── ...                    # Other documentation
├── tests/                      # Test files
│   ├── notebooks/             # Notebook tests (Robot Framework)
│   ├── test_streamlit_app.py  # Streamlit app test
│   └── verify_outputs.py     # Output verification
├── figures/                    # Paper figures
├── ethical_riemann_hypothesis.tex  # Main LaTeX paper
├── references.bib             # Bibliography
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```
## DEMO
<img width="1647" height="1003" alt="螢幕擷取畫面 2025-11-19 144633" src="https://github.com/user-attachments/assets/86b7e910-dc49-4d9c-ab6e-bb8dd9dceb2a" />

<img width="1732" height="994" alt="螢幕擷取畫面 2025-11-19 144430" src="https://github.com/user-attachments/assets/f883510f-b0e5-479c-a792-a93b554618be" />

<img width="1688" height="1004" alt="螢幕擷取畫面 2025-11-19 144452" src="https://github.com/user-attachments/assets/421f952c-a732-43fe-8049-6da2dba27e51" />

<img width="1026" height="574" alt="螢幕擷取畫面 2025-11-19 144748" src="https://github.com/user-attachments/assets/b1543552-036f-43b9-a35e-f058d8641683" />

## Installation

### Prerequisites

- Python 3.10 or later
- LaTeX distribution (for compiling the paper)

### Python Setup

```bash
# Clone the repository
git clone <repository-url>
cd Ethic-Latex

# Install dependencies
pip install -r requirements.txt
```

### LaTeX Setup

To compile the paper:

```bash
# Using the provided script (recommended)
bash scripts/compile_latex.sh
# or on Windows:
scripts\compile_latex.bat

# Or manually:
pdflatex ethical_riemann_hypothesis.tex
bibtex ethical_riemann_hypothesis
pdflatex ethical_riemann_hypothesis.tex
pdflatex ethical_riemann_hypothesis.tex
```

## Quick Start

### Running Basic Simulation

```python
from simulation.core import generate_world, BiasedJudge, evaluate_judgement
from simulation.core import select_ethical_primes, compute_Pi_and_error
from simulation.visualization import plot_Pi_B_E

# Generate moral action space
actions = generate_world(num_actions=1000, complexity_dist='zipf')

# Create and apply a judgment system
judge = BiasedJudge(bias_strength=0.2, noise_scale=0.1)
evaluate_judgement(actions, judge, tau=0.3)

# Extract ethical primes
primes = select_ethical_primes(actions, importance_quantile=0.9)

# Compute and plot error distribution
Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
plot_Pi_B_E(x_vals, Pi_x, B_x, E_x)
```

### Running Jupyter Notebooks

```bash
# Using the provided script (recommended)
bash scripts/start_jupyter.sh
# or on Windows:
scripts\start_jupyter.bat

# Or manually:
cd simulation/notebooks
jupyter notebook
```

Start with `01_basic_simulation.ipynb` for an introduction.

## Cloud Deployment

### Quick Deploy Options

**🚀 Streamlit Cloud (Recommended - 5 minutes)**
1. Push to GitHub
2. Visit https://share.streamlit.io
3. Connect repo → Deploy
4. Your app: `https://YOUR_APP.streamlit.app`

**📓 Binder (For Notebooks - 2 minutes)**
1. Push to GitHub
2. Visit: `https://mybinder.org/v2/gh/YOUR_USERNAME/Ethic-Latex/main`
3. Share the URL for live JupyterLab access

**🐳 Docker (Any Platform)**
```bash
docker build -t erh-app .
docker run -p 8501:8501 erh-app streamlit run simulation/app.py --server.port=8501 --server.address=0.0.0.0
```

See **[CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)** for detailed guides on:
- Streamlit Cloud, Binder, Railway, Render
- AWS, GCP, Azure
- Docker deployment
- Security considerations

## Key Results

(To be filled after running simulations)

### Judge Comparison

| Judge Type | Exponent α | ERH Satisfied | Growth Rate |
|------------|-----------|---------------|-------------|
| Biased     | TBD       | TBD           | TBD         |
| Noisy      | TBD       | TBD           | TBD         |
| Conservative| TBD      | TBD           | TBD         |
| Radical    | TBD       | TBD           | TBD         |

### Interpretation

- **α ≈ 0.5**: ERH satisfied, "Riemann-healthy" system
- **α < 0.5**: Better than ERH predicts, very robust
- **0.5 < α < 1**: Suboptimal but not catastrophic
- **α ≥ 1**: Linear or worse growth, systematic degradation

## Documentation

- **Simulation Framework**: See `simulation/README.md`
- **Installation Guide**: See `docs/INSTALL.md`
- **Usage Guide**: See `docs/USAGE.md`
- **Quick Start**: See `docs/QUICKSTART.md`
- **Troubleshooting**: See `docs/TROUBLESHOOTING.md`
- **API Documentation**: See docstrings in individual modules
- **Theory**: See `ethical_riemann_hypothesis.tex`
- **Tutorials**: See Jupyter notebooks in `simulation/notebooks/`
- **Testing**: See `tests/README.md` for notebook testing with Robot Framework

## Applications to AI Ethics

The ERH framework provides:

1. **Quantitative Criterion**: AI systems should satisfy |E(x)| = O(√x)
2. **Bias Detection**: Violations of ERH indicate systematic failures
3. **Fairness Analysis**: Ethical primes highlight critical errors on vulnerable groups
4. **Design Guidelines**: Bounded uncertainty growth, graceful degradation

## Citation

If you use this framework in your research, please cite:

```bibtex
@article{ethical_riemann_hypothesis,
  title={The Ethical Riemann Hypothesis: A Mathematical Framework for Analyzing Moral Judgment Errors},
  author={[To be completed]},
  journal={[To be completed]},
  year={2025}
}
```

## Contributing

This is a research project. Contributions, suggestions, and discussions are welcome.

## License

MIT License

## Contact

admin@dennisleehappy.org

## Acknowledgments

This work draws inspiration from:
- The Riemann Hypothesis and analytic number theory
- AI ethics and fairness literature
- Error analysis in complex systems
- Computational social science

## Future Work

- Apply to real-world AI systems (recidivism prediction, content moderation)
- Develop theoretical proofs for ERH conditions
- Extend to multi-objective ethical frameworks
- Connect to causal inference and counterfactual reasoning
- Explore quantum computing implementations (QASM experiments)

---

**Note**: This is an exploratory research project combining pure mathematics, computational simulation, and AI ethics. The framework is meant to provoke new ways of thinking about moral judgment errors, not to replace existing ethical frameworks.

---
## ERH-on-Security PoC 設計書（GitLab DevSecOps Pipeline）

# ERH-on-Security PoC 設計書
## 主題：GitLab DevSecOps Pipeline 上的「結構性誤判」分析

### 0. 目標與範圍

**目標問題：**

在一個使用 GitLab + SAST/DAST（Semgrep / Snyk 等）的 DevSecOps 流程中：

- 當專案與變更變得愈來愈複雜時，
- 「真正致命的安全誤判」（該擋沒擋、該修沒修）會以什麼速度累積？
- 我們能否用 ERH（Ethical Riemann Hypothesis）風格的指標，量化這種「結構性風險成長」？

**PoC 範圍：**

- 選擇一個或數個 GitLab 專案（例如：後端服務 / security-platform repo）。
- 以「Merge Request + 安全掃描結果 + 事後狀態」作為分析資料來源。
- 不要求真實 incident log 完全齊全，可以先用「是否留下未修正高嚴重度 issue」當作 proxy ground truth。

---

### 1. 目標管線與資料來源

**選定管線：**  
> GitLab Merge Request 安全審查流程（含 CI pipeline security job）

**主要資料來源：**

1. **Merge Request Metadata（透過 GitLab API / 匯出 JSON）**
   - MR 基本資訊（作者、專案、時間、是否合併）。
   - Diff 統計（lines added/deleted、files changed）。
   - 影響的子系統 / 目錄（根據路徑前綴分類）。

2. **Security Scan Artifacts**
   - SAST（例如 Semgrep/Snyk 的 JSON 報告）。
   - Dependency/Container Scanning 結果。
   - 每次 pipeline 對應的漏洞列表（severity、file、location）。

3. **MR 決策與審查資訊**
   - pipeline 是否通過（pass/fail）。
   - MR 是否合併（merged/rejected）。
   - MR 是否附帶「安全例外 / risk acceptance」標註（若有）。

4. **事後 ground truth（先用 proxy）**
   - 合併後在一定時間窗內（例如 30–90 天）：
     - 是否有新的高嚴重度 issue 被發現與此 MR 相關（可用 issue tag / commit link）。
     - 是否有 incident / bug ticket 追溯到該 MR。

---

### 2. ERH 模型到資安語境的映射

**2.1 Action \( a \)**

- 一個 action 定義為：**一個 MR 的「安全決策事件」**。
- 記作 \( a = \text{MR}_i \)。

**2.2 複雜度 \( c(a) \)**

為 MR 的綜合複雜度指標，可以設計為：

- `c_lines`：變更行數（加權 added/deleted）。
- `c_files`：變更檔案數。
- `c_services`：牽涉子系統數（根據目錄/服務 mapping）。
- `c_dep`：新增或變更的 dependency 數量。
- `c_history`：該區域歷史 bug / incident 密度。

PoC 初版可定義：

\[
c(a) = \text{norm}(\log(1 + \text{lines\_changed})) + \lambda_1 \cdot \text{files\_changed} + \lambda_2 \cdot \text{services\_touched}
\]

再正規化到 \([1, 100]\) 便於沿用 ERH code。

**2.3 真實價值 \( V(a) \)**

- \( V(a) \in [-1, 1] \)：此 MR 合併後，從「安全」角度看最終是好還是壞。
- 初版可以用離散值：

  - \( V(a) = +1 \)：  
    - 合併後，沒有留下 Critical/High issue，且事後沒有相關 incident。
  - \( V(a) = -1 \)：  
    - 合併時仍存在未修正的 Critical/High issue，或  
    - 事後出現 incident / 高嚴重度漏洞追溯到此 MR。
  - \( V(a) = 0 \)：  
    - 低嚴重度問題、或影響不明顯。

（之後可以細化成連續值，如依據漏洞數/嚴重度加權。）

**2.4 重要度 \( w(a) \)**

- 代表此 MR 的安全風險權重，可結合：
  - 影響資產 criticality（core payment / PII / internal tool）。
  - 服務暴露程度（public-facing / internal）。
  - 容量 / QPS / 金額等。

PoC 可先定義：

\[
w(a) = \text{asset\_criticality\_score} \times (1 + \text{exposed\_to\_internet?})
\]

再用 log-normal 或 quantile 正規化，選取 top 10% 作為「高重要度」。

**2.5 Judgment System \( J(a) \)**

在這個 PoC 中，我們考慮三類 judge：

1. **Pipeline Judge \( J_{\text{pipe}} \)**  
   - 由 CI pipeline 決定（security jobs）。
   - 定義簡單版本：
     - 所有 security job pass → \( J_{\text{pipe}}(a) = +1 \)
     - security job fail 但被 override → \( J_{\text{pipe}}(a) = 0 \)
     - security job fail 並 block → \( J_{\text{pipe}}(a) = -1 \)

2. **Human Reviewer Judge \( J_{\text{human}} \)**  
   - 由 reviewer 的行為近似：
     - reviewer 要求修正所有 high/critical issue 才批准 → 偏保守。
     - reviewer 常在 high issue 未解時仍批准 → 偏激進。
   - 初版可以用：
     - 最終 merged = 1, rejected = -1, reopening / force push 可視為中間值。

3. **Combined Judge \( J_{\text{combo}} \)**  
   - 將 pipeline 與 human decision 組合，例如：
     \[
     J_{\text{combo}}(a) = \alpha \cdot J_{\text{pipe}}(a) + (1-\alpha) \cdot J_{\text{human}}(a)
     \]
   - 或定義 rule-based scoring（pipeline fail + 人硬 merge → 強烈負分）。

**2.6 Error, Mistake, Ethical Prime**

沿用 ERH 定義：

- \(\Delta(a) = J(a) - V(a)\)
- Mistake 指標：
  \[
  M(a) = 1 \quad \text{if } |\Delta(a)| > \tau, \text{ 否則 } 0
  \]
  - \(\tau\) 初版可設 0.5（重大錯判）。

- Ethical prime（安全語境）：
  - \(M(a) = 1\)（判錯）  
  - \(w(a)\) 在 top quantile（高重要度資產）。  
  - 該 MR 決策對整體安全具「結構性關鍵」，例如：
    - 關閉某個 class 的防禦。
    - 對共用 library 引入漏洞，影響多服務。

實作上可用：

- 在 misjudged actions 中，挑：
  - `w(a) >= w_q`（top 10%）  
  - `c(a) >= c_min`（複雜度區間中高）  
  → 納入 ethical primes 集合 \(P\)。

---

### 3. 資料 Schema 設計

#### 3.1 actions（核心：MR 決策）

```text
Table: actions
- action_id           (PK, MR ID)
- project_id          (string)
- branch              (string)
- author_id           (string)
- created_at          (timestamp)
- merged_at           (timestamp, nullable)
- merge_status        (enum: merged/rejected/open)
- lines_added         (int)
- lines_deleted       (int)
- files_changed       (int)
- services_touched    (string[])  -- 由路徑映射
- dependencies_added  (int)
- dependencies_changed(int)
```

3.2 judgments
Table: judgments
- id                  (PK)
- action_id           (FK -> actions)
- judge_type          (enum: PIPELINE, HUMAN, COMBINED)
- score_raw           (float in [-1,1])   -- J(a)
- decision_label      (enum: allow/block/override)
- pipeline_passed     (bool, nullable for HUMAN)
- reviewers           (string[])
- review_comments     (int)               -- comment 數量
- created_at          (timestamp)

3.3 ground_truth
Table: ground_truth
- action_id           (FK -> actions)
- V                   (float in [-1,1])
- has_post_incident   (bool)
- incident_id         (string, nullable)
- unresolved_high     (bool)   -- merged 時是否有未解的 high/critical
- unresolved_high_cnt (int)
- window_days         (int)    -- 觀察窗長度

3.4 importance
Table: importance
- action_id           (FK -> actions)
- asset_criticality   (enum: LOW/MEDIUM/HIGH/CRITICAL)
- internet_exposed    (bool)
- user_count          (int, nullable)
- business_impact     (float)    -- 估算
- w                   (float)    -- 正規化後的 weight

3.5 derived_metrics（可 materialized 或 on-the-fly）
Table: derived_metrics
- action_id           (FK -> actions)
- c                   (float)   -- normalized complexity
- delta               (float)   -- Δ(a)
- is_mistake          (bool)    -- M(a)
- is_prime            (bool)

4. ERH 分析流程與指標

4.1 Preprocessing

從 GitLab API 抓取：

MRs, pipelines, jobs, security reports（JSON）。

轉換為上述 schema，存入 PostgreSQL 或 parquet。

為每個 action 計算：

𝑐
(
𝑎
)
c(a)、
𝑉
(
𝑎
)
V(a)、
𝑤
(
𝑎
)
w(a)、
𝐽
(
𝑎
)
J(a)、
Δ
(
𝑎
)
Δ(a)、
𝑀
(
𝑎
)
M(a)、prime 標記。

4.2 ERH-style 指標

對每種 judge（PIPELINE / HUMAN / COMBO），分別計算：

Mistake Rate

MR
=
1
𝑁
∑
𝑎
𝑀
(
𝑎
)
MR=
N
1
	​

∑
a
	​

M(a)

平均誤差

MAE
=
1
𝑁
∑
𝑎
∣
Δ
(
𝑎
)
∣
MAE=
N
1
	​

∑
a
	​

∣Δ(a)∣

Ethical Prime Count

∣
𝑃
∣
∣P∣ 及其在高複雜度區間的分佈。

Π(x), B(x), E(x)

𝑥
x：複雜度上界（例如 bucket 1–100）。

Π
(
𝑥
)
Π(x)：複雜度 ≤ x 的 prime 數量。

𝐵
(
𝑥
)
B(x)：某種 baseline / 期望成長（可用線性或 sublinear baseline）。

𝐸
(
𝑥
)
=
Π
(
𝑥
)
−
𝐵
(
𝑥
)
E(x)=Π(x)−B(x)。

Error Growth Exponent α

對 
𝑥
∈
[
𝑥
min
⁡
,
𝑥
max
⁡
]
x∈[x
min
	​

,x
max
	​

] 擬合：

∣
𝐸
(
𝑥
)
∣
∼
𝐶
𝑥
𝛼
∣E(x)∣∼Cx
α

用 log–log 線性回歸，得到 α 與 
𝑅
2
R
2
。

Within ERH-style Bound?

檢查 α 是否「在某個安全上界之下」，例如：

設目標 α_max = 0.5（worst-case 類比），

α ≪ 0.5 視為「結構上非常安全，但要注意整體誤判率」。

5. 預期圖表（PoC 成果）

5.1 Error vs Complexity

圖 1：複雜度 bucket（例如 10 分桶） vs mistake rate（每種 judge 一條折線）。

圖 2：複雜度 bucket vs ethical prime density。

5.2 ERH-style E(x) 與 α

圖 3：對每種 judge，畫出：

𝑥
x（複雜度） vs 
Π
(
𝑥
)
Π(x)

𝑥
x vs baseline 
𝐵
(
𝑥
)
B(x)

𝑥
x vs 
𝐸
(
𝑥
)
E(x)，在 log–log 座標擬合斜率 α。

5.3 結構熱區

圖 4：熱圖（heatmap）：

x 軸：複雜度 bucket。

y 軸：服務/子系統。

色彩：mistake count 或 prime count。

5.4 時間維度（若要 psychohistory extension）

圖 5：E(x, t) 的 2D 熱圖：

x 軸：時間（例如周）。

y 軸：複雜度 bucket。

色彩：|E(x, t)| 或 prime density。

用來視覺化「Seldon-style crisis」——某些時段在高複雜度區段突然爆量。

6. PoC 實作步驟（技術層）

資料擷取

寫一個 gitlab_ingest.py：

使用 GitLab Personal Access Token。

抓取指定 project 的 MR + pipelines + security artifacts。

將 artifacts JSON parse 成統一格式。

資料落地與 schema 實現

建立 PostgreSQL schema 或 SQLite（PoC 可用 SQLite）。

實作 migration / DDL。

ERH Security Adapter

在你既有的 ERH Python code base 中新增：

security_adapter/transform.py：把 DB 裡的 actions → 
𝐴
,
𝑐
(
𝑎
)
,
𝑉
(
𝑎
)
,
𝑤
(
𝑎
)
,
𝐽
(
𝑎
)
A,c(a),V(a),w(a),J(a)。

security_adapter/metrics.py：計算 Δ(a)、M(a)、P、Π(x)、E(x)、α。

分析與可視化

新增 notebook：

notebooks/erh_security_poc.ipynb

呼叫核心 ERH 分析程式，產出：

Summary 表格（類似 Table 4）。

各種圖（matplotlib）。

輸出報告

產出 docs/SECURITY_POC_REPORT.md：

寫入 Summary 表 + 圖片說明。

作為 internal proposal / 未來論文素材。