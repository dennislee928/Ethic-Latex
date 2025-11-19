# Usage Guide

## Quick Verification

First, verify that all output files exist:

```bash
python verify_outputs.py
```

You should see all 9 files listed with `[OK]` status.

## Starting Jupyter Notebooks

### Option 1: Use the Script (Recommended)
```bash
# Bash/Git Bash
bash start_jupyter.sh

# Windows
start_jupyter.bat
```

### Option 2: Manual Start
```bash
cd simulation/notebooks
jupyter notebook
```

### Option 3: JupyterLab (Modern Interface)
```bash
cd simulation/notebooks
jupyter lab
```

**Note:** The notebooks will automatically open in your default web browser. If it doesn't open automatically, look for a URL like `http://localhost:8888` in the terminal output.

## Compiling LaTeX Paper

### Option 1: Use the Script (Recommended)
```bash
# Bash/Git Bash
bash compile_latex.sh

# Windows
compile_latex.bat
```

### Option 2: Manual Compilation
```bash
pdflatex ethical_riemann_hypothesis.tex
bibtex ethical_riemann_hypothesis
pdflatex ethical_riemann_hypothesis.tex
pdflatex ethical_riemann_hypothesis.tex
```

**Note:** You need a LaTeX distribution installed:
- **Windows**: [MiKTeX](https://miktex.org/)
- **macOS**: [MacTeX](https://www.tug.org/mactex/)
- **Linux**: `sudo apt-get install texlive-full`

## Troubleshooting

### Jupyter Issues

**Problem:** Jupyter doesn't start
- **Solution:** Install Jupyter: `pip install jupyter ipywidgets`

**Problem:** Import errors in notebooks
- **Solution:** Make sure you're running from `simulation/notebooks/` directory
- The notebooks automatically add the parent directory to Python path

**Problem:** Kernel not found
- **Solution:** 
  ```bash
  pip install ipykernel
  python -m ipykernel install --user
  ```

### LaTeX Issues

**Problem:** `pdflatex: command not found`
- **Solution:** Install a LaTeX distribution (see above)

**Problem:** Compilation errors
- **Solution:** Check `ethical_riemann_hypothesis.log` for detailed error messages
- Common issues:
  - Missing packages: Install via your LaTeX distribution's package manager
  - Bibliography errors: Make sure `references.bib` exists
  - Figure errors: Make sure figures are in the `figures/` directory

**Problem:** PDF not generated
- **Solution:** 
  1. Check the log file for errors
  2. Make sure all required LaTeX packages are installed
  3. Try compiling with verbose output: `pdflatex ethical_riemann_hypothesis.tex` (without `-interaction=nonstopmode`)

## File Locations

### Generated Outputs
- **Figures**: `simulation/output/figures/`
- **Reports**: `simulation/output/`
- **Paper PDF**: `ethical_riemann_hypothesis.pdf` (after compilation)

### Source Files
- **Notebooks**: `simulation/notebooks/`
- **Python Code**: `simulation/core/`, `simulation/analysis/`, `simulation/visualization/`
- **LaTeX Paper**: `ethical_riemann_hypothesis.tex`
- **Bibliography**: `references.bib`

## Next Steps

1. **Explore the notebooks** - Start with `01_basic_simulation.ipynb`
2. **Generate your own figures** - Modify parameters in the notebooks
3. **Read the paper** - Compile the LaTeX document
4. **Extend the framework** - Add your own judgment systems or analysis methods

