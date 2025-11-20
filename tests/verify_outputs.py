"""
Verify that all expected output files exist
"""
import os

print("=" * 70)
print("VERIFYING GENERATED OUTPUT FILES")
print("=" * 70)
print()

base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "simulation", "output")
expected_files = [
    "figures/paper_fig1_pi_b_e.pdf",
    "figures/paper_fig2_error_growth.pdf",
    "figures/paper_fig3_judge_comparison.pdf",
    "figures/paper_fig4_exponent_comparison.pdf",
    "figures/paper_fig5_spectrum.pdf",
    "figures/paper_fig6_zeros.pdf",
    "figures/paper_fig7_complexity_dist.pdf",
    "judge_comparison_report.md",
    "results_summary.txt"
]

all_exist = True
for file_path in expected_files:
    full_path = os.path.join(base_dir, file_path)
    exists = os.path.exists(full_path)
    status = "[OK]" if exists else "[MISSING]"
    
    if exists:
        size = os.path.getsize(full_path)
        size_kb = size / 1024
        print(f"{status} {file_path:50s} ({size_kb:.1f} KB)")
    else:
        print(f"{status} {file_path:50s}")
        all_exist = False

print()
if all_exist:
    print("=" * 70)
    print("SUCCESS: All expected files exist!")
    print("=" * 70)
else:
    print("=" * 70)
    print("WARNING: Some files are missing. Run generate_all_figures.py")
    print("=" * 70)

