#!/usr/bin/env python3
"""
Integrate generated figures into LaTeX documents.

This script automatically inserts figures into the correct sections
of both English and Chinese LaTeX files.
"""

import os
import re
import glob

def find_figures(figures_dir):
    """Find all PDF figures in the figures directory."""
    if not os.path.exists(figures_dir):
        return {}
    
    figure_map = {
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
    
    # Find the results section
    if lang == 'en':
        results_marker = r"% Figures will be inserted here by the figure integration script"
        section_label = r"\\section\{Results"
    else:
        results_marker = r"% 圖表將由圖表整合腳本插入此處"
        section_label = r"\\section\{實驗結果"
    
    # Insert figures in results section
    if results_marker in content:
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
    
    if framework_figures and framework_marker in content:
        # Insert before Fourier section
        insertion = "\n".join(framework_figures) + "\n\n" + framework_marker
        content = content.replace(framework_marker, insertion)
        print(f"Inserted {len(framework_figures)} figures into framework section")
    
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
        print("Warning: No figures found!")
    else:
        print(f"Found {len(figures)} figures")
        for fig_file in figures:
            print(f"  - {fig_file}")
    
    print(f"\nIntegrating figures into English LaTeX: {latex_path_en}")
    integrate_figures_into_latex(latex_path_en, figures, lang='en')
    
    print(f"\nIntegrating figures into Chinese LaTeX: {latex_path_zh}")
    integrate_figures_into_latex(latex_path_zh, figures, lang='zh')

