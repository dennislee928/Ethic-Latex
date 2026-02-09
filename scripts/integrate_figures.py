#!/usr/bin/env python3
"""
Integrate generated figures into LaTeX documents.

This script automatically inserts figures into the correct sections
of both English and Chinese LaTeX files.:)
"""

import os
import re
import glob
import sys

def find_figures(figures_dir):
    """Find all PDF and PNG figures in the figures directory."""
    if not os.path.exists(figures_dir):
        return {}
    
    figure_map = {
        # PDF figures from generate_all_figures.py (build_thesis workflow)
        'paper_fig1_pi_b_e.pdf': {'label': 'fig:pi_b_e', 'caption_en': 'Distribution functions $\\Pi(x)$, $B(x)$, and $E(x)$ for the Biased Judge.', 'caption_zh': '偏見判斷者的分布函數 $\\Pi(x)$、$B(x)$ 和 $E(x)$。', 'section': 'results'},
        'paper_fig2_error_growth.pdf': {'label': 'fig:error_growth', 'caption_en': 'Error growth analysis showing $|E(x)|$ vs. complexity $x$ in log-log scale.', 'caption_zh': '誤差增長分析，顯示對數-對數尺度下 $|E(x)|$ 與複雜度 $x$ 的關係。', 'section': 'results'},
        'paper_fig3_judge_comparison.pdf': {'label': 'fig:judge_comparison', 'caption_en': 'Comparison of error growth across different judgment systems.', 'caption_zh': '不同判斷系統間誤差增長的比較。', 'section': 'results'},
        'paper_fig4_exponent_comparison.pdf': {'label': 'fig:exponent_comparison', 'caption_en': 'Estimated growth exponent $\\alpha$ by judge type.', 'caption_zh': '各判斷者類型的估計增長指數 $\\alpha$。', 'section': 'results'},
        'paper_fig5_spectrum.pdf': {'label': 'fig:spectrum', 'caption_en': 'Frequency spectrum of the ethical zeta function.', 'caption_zh': '倫理 zeta 函數的頻譜。', 'section': 'results'},
        'paper_fig6_zeros.pdf': {'label': 'fig:zeros', 'caption_en': 'Distribution of zeros of the ethical zeta function in the complex plane.', 'caption_zh': '倫理 zeta 函數在複平面中的零點分布。', 'section': 'results'},
        'paper_fig7_critical_bound.pdf': {'label': 'fig:critical_bound', 'caption_en': 'Critical bound: $|E(x)|$ vs.$x$ in log-log scale with ERH reference $C\\cdot x^{1/2}$ overlay.', 'caption_zh': '臨界界線：$|E(x)|$ 與 $x$ 的對數-對數圖，含 ERH 參考線 $C\\cdot x^{1/2}$。', 'section': 'results'},
        'paper_fig8_ethical_primes_map.pdf': {'label': 'fig:ethical_primes_map', 'caption_en': 'Ethical primes in action space: 2D scatter (complexity vs. importance), colored by error magnitude.', 'caption_zh': '行動空間中的倫理質數：二維散點圖（複雜度 vs. 重要性），依誤差大小著色。', 'section': 'results'},
        'paper_fig7_complexity_dist.pdf': {'label': 'fig:complexity_dist', 'caption_en': 'Distribution of action complexities in the generated moral action space.', 'caption_zh': '生成道德行動空間中行動複雜度的分布。', 'section': 'framework'},
        'paper_fig8_quantum_judge.pdf': {'label': 'fig:quantum_judge', 'caption_en': '$\\Pi(x)$, $B(x)$, and $E(x)$ for the Quantum Judge.', 'caption_zh': '量子判斷者的 $\\Pi(x)$、$B(x)$ 與 $E(x)$。', 'section': 'results'},
        'paper_fig9_normalized_oscillation.pdf': {'label': 'fig:normalized_oscillation', 'caption_en': 'Normalized oscillation $E(x)/\\sqrt{x}$. If ERH holds, the curve remains bounded.', 'caption_zh': '正規化振盪 $E(x)/\\sqrt{x}$。若 ERH 成立，曲線保持有界。', 'section': 'results'},
        'paper_fig10_phase_transition_h.pdf': {'label': 'fig:phase_transition_h', 'caption_en': 'Quantum phase transition: magnetization vs. transverse field $h$. Critical $h_c$ marks ordered $\\to$ disordered.', 'caption_zh': '量子相變：磁化 vs. 橫場 $h$。臨界 $h_c$ 標記有序 $\\to$ 無序。', 'section': 'quantum'},
        'paper_fig11_prime_ladder.pdf': {'label': 'fig:prime_ladder', 'caption_en': 'Ethical prime ladder: $\\Pi(x)$ step function with $Li(x)$ smooth overlay.', 'caption_zh': '倫理質數階梯：$\\Pi(x)$ 階梯函數與 $Li(x)$ 平滑疊加。', 'section': 'results'},
        'von_neumann_entropy_over_time.pdf': {'label': 'fig:von_neumann_entropy', 'caption_en': 'Von Neumann entropy $S(\\rho)$ over time: echo-chamber indicator. Low entropy: high consensus; high entropy: no consensus.', 'caption_zh': 'Von Neumann 熵 $S(\\rho)$ 隨時間：迴聲室指標。低熵：高共識；高熵：無共識。', 'section': 'quantum'},
        # PNG figures from simulation workflow and build_thesis (build_thesis_gated)
        'phase_transition.png': {'label': 'fig:phase_transition', 'caption_en': 'Moral phase transition: as conflict density (complexity) increases, ground-state fidelity drops. The collapse point marks the pole of the Ethical Zeta Function.', 'caption_zh': '道德相變：隨衝突密度（複雜度）增加，基態保真度下降。崩潰點標記倫理 Zeta 函數的極點。', 'section': 'quantum'},
        'alpha_comparison_real_vs_simulated.png': {'label': 'fig:alpha_real_vs_simulated', 'caption_en': 'Real-world growth exponent $\\alpha$ vs simulated Conservative judge. Compares Adult Income and COMPAS empirical $\\alpha$ with the simulated Conservative judge from ERH framework.', 'caption_zh': '真實世界增長指數 $\\alpha$ 與模擬保守判斷者比較。將 Adult Income 與 COMPAS 的實證 $\\alpha$ 與 ERH 框架下模擬的保守判斷者進行對照。', 'section': 'compas'},
        'compas_erh_bound.png': {'label': 'fig:compas_erh_bound', 'caption_en': 'COMPAS adherence to Riemann bound. Log-log plot of $|E(x)|$ vs. complexity $x$ with theoretical bound $C\\cdot x^{0.5}$. Error growth exponent $\\alpha\\approx-0.32$ indicates sublinear growth consistent with ERH.', 'caption_zh': 'COMPAS 與 Riemann 界線的符合度。$|E(x)|$ 與複雜度 $x$ 的對數-對數圖，含理論界線 $C\\cdot x^{0.5}$。誤差增長指數 $\\alpha\\approx-0.32$ 表示與 ERH 一致的次線性增長。', 'section': 'compas'},
        'alpha_comparison_bar.png': {'label': 'fig:alpha_comparison_bar', 'caption_en': 'Structural similarity: $\\alpha$ comparison across Radical, Conservative (synthetic), COMPAS, and Adult Income (real-world). COMPAS $\\approx-0.32$ highlighted.', 'caption_zh': '結構相似性：Radical、Conservative（模擬）、COMPAS、Adult Income（真實）的 $\\alpha$ 比較。COMPAS $\\approx-0.32$ 標示。', 'section': 'compas'},
        'universal_error_growth.png': {'label': 'fig:universal_error_growth', 'caption_en': 'Universal Error Growth Laws. Simulated Agent curves (Biased Judge) and COMPAS real data on the same log-log plot. When the curves overlap, the theory\'s universality is visually confirmed.', 'caption_zh': '普適誤差增長定律。模擬智能體曲線（偏見判斷者）與 COMPAS 真實數據同繪於對數-對數圖。當兩條線重合時，理論的普適性得以視覺化驗證。', 'section': 'compas'},
        'mistake_rate_comparison.png': {'label': 'fig:mistake_rate_comparison', 'caption_en': 'Mistake rate by complexity distribution. Comparison across zipf, uniform, and power-law distributions from the simulation campaign.', 'caption_zh': '各複雜度分布的錯誤率比較。來自模擬活動的 zipf、uniform 與 power-law 分布比較。', 'section': 'results'},
        'alpha_comparison.png': {'label': 'fig:alpha_comparison', 'caption_en': 'Error growth exponent $\\alpha$ distribution by complexity distribution. Box plot showing estimated $\\alpha$ across zipf, uniform, and power-law with ERH limit line at $0.5$.', 'caption_zh': '各複雜度分布的誤差增長指數 $\\alpha$ 分布。箱形圖顯示 zipf、uniform 與 power-law 下的估計 $\\alpha$，ERH 界限線為 $0.5$。', 'section': 'results'},
        'evs_over_time.png': {'label': 'fig:evs_over_time', 'caption_en': 'Ethical Viability Score (EVS) over time and by complexity distribution. Left: EVS vs run index; Right: EVS bar chart by distribution type.', 'caption_zh': '倫理可行性分數（EVS）隨時間與複雜度分布。左圖：EVS 與執行序號；右圖：各分布類型的 EVS 長條圖。', 'section': 'results'},
        'normalized_error_oscillation.png': {'label': 'fig:normalized_oscillation', 'caption_en': 'Normalized error oscillation $E(x)/\\sqrt{x}$ with confidence interval. COMPAS data.', 'caption_zh': '正規化誤差振盪 $E(x)/\\sqrt{x}$ 與信賴區間。COMPAS 數據。', 'section': 'supplementary'},
        'llm_stress_test_Pi_E.png': {'label': 'fig:llm_stress_test', 'caption_en': 'LLM stress test: $\\Pi(x)$ and $E(x)$ from OpenAI/Anthropic API evaluation. Empirical curves from LLM-based moral judgment under repeated action evaluation.', 'caption_zh': 'LLM 壓力測試：OpenAI/Anthropic API 評估的 $\\Pi(x)$ 與 $E(x)$。來自重複行動評估下 LLM 道德判斷的實證曲線。', 'section': 'supplementary'},
        'latest_quantum_circuit.png': {'label': 'fig:quantum_circuit_supp', 'caption_en': 'Quantum circuit representing ethical Hilbert space: $U3$ gates encode Bloch sphere positions, $R_{ZZ}$ gates model social entanglement.', 'caption_zh': '代表倫理 Hilbert 空間的量子電路：$U3$ 門編碼 Bloch 球面位置，$R_{ZZ}$ 門模型社會糾纏。', 'section': 'supplementary'},
        'latest_quantum_distribution.png': {'label': 'fig:quantum_dist_supp', 'caption_en': 'Probability distribution of ethical states after quantum simulation. Peaks indicate highly probable societal configurations.', 'caption_zh': '量子模擬後倫理態的機率分布。峰值表示高機率社會配置。', 'section': 'supplementary'},
    }
    
    found_figures = {}
    for fig_file, info in figure_map.items():
        fig_path = os.path.join(figures_dir, fig_file)
        if os.path.exists(fig_path):
            found_figures[fig_file] = info

    return found_figures

def insert_figure_latex(fig_file, info, lang='en'):
    """Generate LaTeX code for a figure."""
    if lang == 'en':
        caption = info['caption_en']
    else:
        caption = info['caption_zh']
    
    label = info['label']
    
    latex_code = f"""\\begin{{figure}}[htbp]
  \\centering
  \\includegraphics[width=0.8\\textwidth]{{figures/{fig_file}}}
  \\caption{{{caption}}}
  \\label{{{label}}}
\\end{{figure}}
"""
    return latex_code

def _insert_figure_if_exists(fig_file, info, lang):
    """Generate LaTeX with \\IfFileExists for optional figures."""
    caption = info['caption_en'] if lang == 'en' else info['caption_zh']
    label = info['label']
    return f"""\\begin{{figure}}[htbp]
  \\centering
  \\IfFileExists{{figures/{fig_file}}}{{
    \\includegraphics[width=0.8\\textwidth]{{figures/{fig_file}}}
  }}{{
    \\IfFileExists{{simulation/output/figures/{fig_file}}}{{
      \\includegraphics[width=0.8\\textwidth]{{simulation/output/figures/{fig_file}}}
    }}{{
      \\fbox{{\\parbox{{0.7\\textwidth}}{{\\centering Figure {fig_file} (run pipeline to generate).}}}}
    }}
  }}
  \\caption{{{caption}}}
  \\label{{{label}}}
\\end{{figure}}
"""


def integrate_figures_into_latex(latex_path, figures, lang='en'):
    """Insert figures into LaTeX file at appropriate locations."""
    if not os.path.exists(latex_path):
        print(f"Warning: LaTeX file not found: {latex_path}")
        return

    with open(latex_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip results/framework insertion if main PDF figures already exist (avoid duplication)
    results_figures = [f for f, i in figures.items() if i.get('section') in ('results', 'framework')]
    results_already_in = any(f"figures/{f}" in content or f"simulation/output/figures/{f}" in content for f in results_figures) if results_figures else False

    # Insert figures in results section (skip if already present)
    if not results_already_in:
        results_marker = r"% Figures will be inserted here by the figure integration script" if lang == 'en' else r"% 圖表將由圖表整合腳本插入此處"
        if results_marker in content:
            figure_insertions = [_insert_figure_if_exists(f, i, lang) for f, i in figures.items() if i.get('section') == 'results']
            if figure_insertions:
                replacement = results_marker + "\n\n" + "\n".join(figure_insertions)
                content = content.replace(results_marker, replacement)
                print(f"Inserted {len(figure_insertions)} figures into results section")

    # Insert framework figures
    framework_marker = r"\subsection{Fourier Spectrum Analysis}" if lang == 'en' else r"\subsection{傅立葉頻譜分析}"
    framework_figures = [(f, i) for f, i in figures.items() if i.get('section') == 'framework']
    if framework_figures and framework_marker in content and not results_already_in:
        insertion = "\n".join(_insert_figure_if_exists(f, i, lang) for f, i in framework_figures) + "\n\n" + framework_marker
        content = content.replace(framework_marker, insertion)
        print(f"Inserted {len(framework_figures)} figures into framework section")

    # Insert quantum figures (phase transition, von Neumann entropy, etc.)
    quantum_marker = r"% Quantum pipeline figures (phase transition, von Neumann entropy) will be inserted here by integrate_figures.py" if lang == 'en' else r"% 量子流程圖表（相變、Von Neumann 熵）將由 integrate_figures.py 插入此處"
    quantum_figures = [(f, i) for f, i in figures.items() if i.get('section') == 'quantum']
    if quantum_figures and quantum_marker in content:
        quantum_insertions = "\n".join(_insert_figure_if_exists(f, i, lang) for f, i in quantum_figures)
        content = content.replace(quantum_marker, quantum_marker + "\n\n" + quantum_insertions)
        print(f"Inserted {len(quantum_figures)} quantum figures")

    # Insert COMPAS figures
    compas_marker = r"% COMPAS pipeline figures will be inserted here by integrate_figures.py" if lang == 'en' else r"% COMPAS 流程圖表將由 integrate_figures.py 插入此處"
    compas_figures = [(f, i) for f, i in figures.items() if i.get('section') == 'compas']
    if compas_figures and compas_marker in content:
        compas_insertions = "\n".join(_insert_figure_if_exists(f, i, lang) for f, i in compas_figures)
        content = content.replace(compas_marker, compas_marker + "\n\n" + compas_insertions)
        print(f"Inserted {len(compas_figures)} COMPAS figures")

    # Insert supplementary pipeline figures
    supp_marker = r"% Supplementary pipeline figures will be inserted here by integrate_figures.py" if lang == 'en' else r"% 補充流程圖表將由 integrate_figures.py 插入此處"
    supp_figures = [(f, i) for f, i in figures.items() if i.get('section') == 'supplementary']
    if supp_figures and supp_marker in content:
        supp_insertions = "\n".join(_insert_figure_if_exists(f, i, lang) for f, i in supp_figures)
        content = content.replace(supp_marker, supp_marker + "\n\n" + supp_insertions)
        print(f"Inserted {len(supp_figures)} supplementary pipeline figures")

    with open(latex_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Successfully integrated figures into {latex_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    figures_dir = os.path.join(base_dir, "figures")
    latex_path_en = os.path.join(base_dir, "ethical_riemann_hypothesis_en.tex")
    latex_path_zh = os.path.join(base_dir, "ethical_riemann_hypothesis_zh.tex")
    
    print(f"Finding figures in: {figures_dir}")
    figures = find_figures(figures_dir)
    
    if not figures:
        print("Warning: No figures found - this is expected if simulations haven't run yet")
        print("Skipping figure integration")
        sys.exit(0)  # Exit gracefully
    else:
        print(f"Found {len(figures)} figures")
        for fig_file in figures:
            print(f"  - {fig_file}")
    
    print(f"\nIntegrating figures into English LaTeX: {latex_path_en}")
    integrate_figures_into_latex(latex_path_en, figures, lang='en')
    
    print(f"\nIntegrating figures into Chinese LaTeX: {latex_path_zh}")
    integrate_figures_into_latex(latex_path_zh, figures, lang='zh')

