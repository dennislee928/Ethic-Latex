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
        'paper_fig1_pi_b_e.pdf': {
            'label': 'fig:pi_b_e',
            'caption_en': 'Distribution functions $\\Pi(x)$, $B(x)$, and $E(x)$ for the Biased Judge.',
            'caption_zh': '偏見判斷者的分布函數 $\\Pi(x)$、$B(x)$ 和 $E(x)$。',
            'section': 'results'
        },
        'paper_fig2_error_growth.pdf': {
            'label': 'fig:error_growth',
            'caption_en': 'Error growth analysis showing $|E(x)|$ vs. complexity $x$ in log-log scale.',
            'caption_zh': '誤差增長分析，顯示對數-對數尺度下 $|E(x)|$ 與複雜度 $x$ 的關係。',
            'section': 'results'
        },
        'paper_fig3_judge_comparison.pdf': {
            'label': 'fig:judge_comparison',
            'caption_en': 'Comparison of error growth across different judgment systems.',
            'caption_zh': '不同判斷系統間誤差增長的比較。',
            'section': 'results'
        },
        'paper_fig4_exponent_comparison.pdf': {
            'label': 'fig:exponent_comparison',
            'caption_en': 'Estimated growth exponent $\\alpha$ by judge type.',
            'caption_zh': '各判斷者類型的估計增長指數 $\\alpha$。',
            'section': 'results'
        },
        'paper_fig5_spectrum.pdf': {
            'label': 'fig:spectrum',
            'caption_en': 'Frequency spectrum of the ethical zeta function.',
            'caption_zh': '倫理 zeta 函數的頻譜。',
            'section': 'results'
        },
        'paper_fig6_zeros.pdf': {
            'label': 'fig:zeros',
            'caption_en': 'Distribution of zeros of the ethical zeta function in the complex plane.',
            'caption_zh': '倫理 zeta 函數在複平面中的零點分布。',
            'section': 'results'
        },
        'paper_fig7_complexity_dist.pdf': {
            'label': 'fig:complexity_dist',
            'caption_en': 'Distribution of action complexities in the generated moral action space.',
            'caption_zh': '生成道德行動空間中行動複雜度的分布。',
            'section': 'framework'
        },
        'paper_fig8_quantum_judge.pdf': {
            'label': 'fig:quantum_judge',
            'caption_en': '$\\Pi(x)$, $B(x)$, and $E(x)$ for the Quantum Judge.',
            'caption_zh': '量子判斷者的 $\\Pi(x)$、$B(x)$ 與 $E(x)$。',
            'section': 'results'
        },
        # PNG figures from simulation workflow and build_thesis (build_thesis_gated)
        'alpha_comparison_real_vs_simulated.png': {
            'label': 'fig:alpha_real_vs_simulated',
            'caption_en': 'Real-world growth exponent $\\alpha$ vs simulated Conservative judge. Compares Adult Income and COMPAS empirical $\\alpha$ with the simulated Conservative judge from ERH framework.',
            'caption_zh': '真實世界增長指數 $\\alpha$ 與模擬保守判斷者比較。將 Adult Income 與 COMPAS 的實證 $\\alpha$ 與 ERH 框架下模擬的保守判斷者進行對照。',
            'section': 'supplementary'
        },
        'mistake_rate_comparison.png': {
            'label': 'fig:mistake_rate_comparison',
            'caption_en': 'Mistake rate by complexity distribution. Comparison across zipf, uniform, and power-law distributions from the simulation campaign.',
            'caption_zh': '各複雜度分布的錯誤率比較。來自模擬活動的 zipf、uniform 與 power-law 分布比較。',
            'section': 'supplementary'
        },
        'alpha_comparison.png': {
            'label': 'fig:alpha_comparison',
            'caption_en': 'Error growth exponent $\\alpha$ distribution by complexity distribution. Box plot showing estimated $\\alpha$ across zipf, uniform, and power-law with ERH limit line at $0.5$.',
            'caption_zh': '各複雜度分布的誤差增長指數 $\\alpha$ 分布。箱形圖顯示 zipf、uniform 與 power-law 下的估計 $\\alpha$，ERH 界限線為 $0.5$。',
            'section': 'supplementary'
        },
        'evs_over_time.png': {
            'label': 'fig:evs_over_time',
            'caption_en': 'Ethical Viability Score (EVS) over time and by complexity distribution. Left: EVS vs run index; Right: EVS bar chart by distribution type.',
            'caption_zh': '倫理可行性分數（EVS）隨時間與複雜度分布。左圖：EVS 與執行序號；右圖：各分布類型的 EVS 長條圖。',
            'section': 'supplementary'
        },
        'llm_stress_test_Pi_E.png': {
            'label': 'fig:llm_stress_test',
            'caption_en': 'LLM stress test: $\\Pi(x)$ and $E(x)$ from OpenAI/Anthropic API evaluation. Empirical curves from LLM-based moral judgment under repeated action evaluation.',
            'caption_zh': 'LLM 壓力測試：OpenAI/Anthropic API 評估的 $\\Pi(x)$ 與 $E(x)$。來自重複行動評估下 LLM 道德判斷的實證曲線。',
            'section': 'supplementary'
        }
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

def integrate_figures_into_latex(latex_path, figures, lang='en'):
    """Insert figures into LaTeX file at appropriate locations."""
    if not os.path.exists(latex_path):
        print(f"Warning: LaTeX file not found: {latex_path}")
        return
    
    with open(latex_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip results/framework insertion if main PDF figures already exist (avoid duplication)
    results_figures = [f for f, i in figures.items() if i.get('section') in ('results', 'framework')]
    results_already_in = any(f"figures/{f}" in content for f in results_figures) if results_figures else False
    
    # Find the results section
    if lang == 'en':
        results_marker = r"% Figures will be inserted here by the figure integration script"
        section_label = r"\\section\{Results"
    else:
        results_marker = r"% 圖表將由圖表整合腳本插入此處"
        section_label = r"\\section\{實驗結果"
    
    # Insert figures in results section (skip if already present)
    if results_marker in content and not results_already_in:
        figure_insertions = []
        for fig_file, info in figures.items():
            if info['section'] == 'results':
                figure_insertions.append(insert_figure_latex(fig_file, info, lang))
        
        if figure_insertions:
            replacement = results_marker + "\n\n" + "\n".join(figure_insertions)
            content = content.replace(results_marker, replacement)
            print(f"Inserted {len(figure_insertions)} figures into results section")
    
    # Insert framework figures
    if lang == 'en':
        framework_marker = r"\\subsection\{Fourier Spectrum Analysis\}"
    else:
        framework_marker = r"\\subsection\{傅立葉頻譜分析\}"
    
    framework_figures = []
    for fig_file, info in figures.items():
        if info['section'] == 'framework':
            framework_figures.append(insert_figure_latex(fig_file, info, lang))
    
    if framework_figures and framework_marker in content and not results_already_in:
        # Insert before Fourier section
        insertion = "\n".join(framework_figures) + "\n\n" + framework_marker
        content = content.replace(framework_marker, insertion)
        print(f"Inserted {len(framework_figures)} figures into framework section")
    
    # Insert supplementary pipeline figures (PNG from build_thesis_gated workflow)
    supp_marker_en = r"% Supplementary pipeline figures will be inserted here by integrate_figures.py"
    supp_marker_zh = r"% 補充流程圖表將由 integrate_figures.py 插入此處"
    supp_marker = supp_marker_en if lang == 'en' else supp_marker_zh
    supp_files = [f for f, info in figures.items() if info.get('section') == 'supplementary']
    supp_already_in = any(f"figures/{f}" in content for f in supp_files) if supp_files else False
    supp_figures = [insert_figure_latex(f, info, lang) for f, info in figures.items() if info.get('section') == 'supplementary']
    if supp_figures and supp_marker in content and not supp_already_in:
        content = content.replace(supp_marker, supp_marker + "\n\n" + "\n".join(supp_figures))
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

