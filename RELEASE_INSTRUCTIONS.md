# Release Instructions for v0.9-pre-submission

This document provides step-by-step instructions for creating the pre-submission release.

## Prerequisites

1. Ensure all PDFs are compiled and up-to-date
2. Ensure all figures are generated in `figures/` directory
3. Ensure all supplementary material is in place

## Step 1: Prepare Release Files

### On Linux/macOS:
```bash
bash scripts/prepare_release.sh
```

### On Windows:
```cmd
scripts\prepare_release.bat
```

This will create a `release_v0.9-pre-submission/` directory with:
- PDF files (English and Chinese)
- Supplementary material archive
- Release notes

## Step 2: Create Git Tag

```bash
git tag -a v0.9-pre-submission -m "Pre-submission version: unified terminology, enhanced tables, added supplementary material references"
git push origin v0.9-pre-submission
```

## Step 3: Create GitHub Release

1. Go to: https://github.com/dennislee928/Ethic-Latex/releases/new
2. Select tag: `v0.9-pre-submission`
3. Title: `v0.9-pre-submission - Pre-Submission Version`
4. Description: Copy from `release_v0.9-pre-submission/RELEASE_NOTES.md`
5. Attach files:
   - `ethical_riemann_hypothesis_en.pdf`
   - `ethical_riemann_hypothesis_zh.pdf`
   - `supplementary_material.tar.gz`
6. Publish release

## Manual Alternative

If you prefer to create the release manually:

1. **Compile PDFs** (if not already done):
   ```bash
   # Compile English version
   pdflatex ethical_riemann_hypothesis_en.tex
   bibtex ethical_riemann_hypothesis_en
   pdflatex ethical_riemann_hypothesis_en.tex
   pdflatex ethical_riemann_hypothesis_en.tex
   
   # Compile Chinese version (if needed)
   xelatex ethical_riemann_hypothesis_zh.tex
   ```

2. **Create supplementary material archive**:
   ```bash
   tar -czf supplementary_material.tar.gz \
       docs/EXPERIMENT_REPORTS.md \
       simulation/output/ \
       data/ \
       figures/ \
       README_for_reviewers.md \
       docs/PSYCHOHISTORY_TECHNICAL.md
   ```

3. **Create GitHub release** with the three files above

## Verification Checklist

Before creating the release, verify:
- [ ] English PDF compiles without errors
- [ ] Chinese PDF compiles without errors (if submitting)
- [ ] All figures are present in `figures/` directory
- [ ] `docs/EXPERIMENT_REPORTS.md` is up-to-date
- [ ] `README_for_reviewers.md` is accurate
- [ ] All terminology is unified (ERH-style bound, etc.)
- [ ] Table 4 includes new columns
- [ ] Real-data table is present in Section 6.6

