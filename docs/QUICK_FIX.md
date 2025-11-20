# Quick Fix Guide

## Jupyter Command Not Found - FIXED!

**Problem:** `jupyter: command not found` even though Jupyter is installed

**Solution:** Use Python module syntax instead:

```bash
python -m jupyter notebook
```

This always works, even if the `jupyter` command is not in PATH.

## Updated Scripts

All scripts now automatically try:
1. `jupyter` command (if in PATH)
2. `python -m jupyter` (fallback - always works)
3. `python3 -m jupyter` (alternative)

## How to Start Jupyter Now

### Method 1: Use the Fixed Script
```bash
bash start_jupyter.sh
```

### Method 2: Direct Command (Recommended)
```bash
cd simulation/notebooks
python -m jupyter notebook
```

### Method 3: From Project Root
```bash
cd simulation/notebooks
python -m jupyter notebook
```

## LaTeX Compilation

If `pdflatex` is not found:

1. **Install LaTeX:**
   - Windows: Download [MiKTeX](https://miktex.org/)
   - After installation, restart terminal

2. **Or use the compile script:**
   ```bash
   bash compile_latex.sh
   ```

3. **Or compile manually (after installing LaTeX):**
   ```bash
   pdflatex ethical_riemann_hypothesis.tex
   bibtex ethical_riemann_hypothesis
   pdflatex ethical_riemann_hypothesis.tex
   pdflatex ethical_riemann_hypothesis.tex
   ```

## Verification

**Check Jupyter:**
```bash
python -m jupyter --version
```

**Check all files exist:**
```bash
python verify_outputs.py
```

**Test core functionality:**
```bash
cd simulation
python run_example.py
```

## Summary

✅ **Jupyter:** Use `python -m jupyter notebook`  
✅ **LaTeX:** Install MiKTeX first, then compile  
✅ **All files:** Verified and exist in `simulation/output/figures/`

