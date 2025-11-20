# Quick Start Scripts

This directory contains quick start scripts for different platforms.

## Available Scripts

### For Linux/macOS/Git Bash (Bash)
```bash
./quick-start.sh
```

### For Windows PowerShell
```powershell
.\quick-start.ps1
```

### For Windows Command Prompt
```cmd
quick-start.bat
```

## What These Scripts Do

All scripts perform the following steps:

1. **Quick Example** - Run `simulation/run_example.py` to see a basic demonstration
2. **Generate Figures** (optional) - Run `simulation/generate_all_figures.py` if matplotlib is installed
3. **Jupyter Notebooks** (optional) - Instructions for opening notebooks
4. **Compile LaTeX** (optional) - Compile the paper if LaTeX is installed

## Requirements

### Required
- Python 3.10+
- Core dependencies: `numpy`, `scipy`, `pandas`

### Optional
- `matplotlib`, `seaborn` - For figure generation
- `jupyter` - For interactive notebooks
- LaTeX distribution (MiKTeX, TeX Live) - For paper compilation

## Installation

First, install Python dependencies:

```bash
pip install -r ../requirements.txt
```

## Usage

### From Project Root
```bash
# Bash/Git Bash
bash quick-start-script/quick-start.sh

# PowerShell
powershell -ExecutionPolicy Bypass -File quick-start-script/quick-start.ps1

# Windows CMD
quick-start-script\quick-start.bat
```

### From Script Directory
The scripts automatically detect the project root, so you can run them from anywhere:

```bash
cd quick-start-script
./quick-start.sh  # or .ps1 or .bat
```

## Troubleshooting

### "simulation directory not found"
- Make sure you're running from the project root or the script directory
- Check that the project structure is intact

### "matplotlib not found"
- Install with: `pip install matplotlib seaborn`
- Or skip figure generation (it's optional)

### "jupyter not found"
- Install with: `pip install jupyter`
- Or manually open notebooks from `simulation/notebooks/`

### "pdflatex not found"
- Install a LaTeX distribution:
  - Windows: [MiKTeX](https://miktex.org/)
  - macOS: [MacTeX](https://www.tug.org/mactex/)
  - Linux: `sudo apt-get install texlive-full` (or similar)

### Path Issues on Windows
- Use PowerShell or Git Bash for better path handling
- Ensure Python is in your PATH
- Use forward slashes in paths when using Git Bash

## Manual Steps

If the scripts don't work, you can run steps manually:

```bash
# Step 1: Quick example
cd simulation
python run_example.py

# Step 2: Generate figures (if matplotlib installed)
python generate_all_figures.py

# Step 3: Jupyter notebooks
cd notebooks
jupyter notebook

# Step 4: Compile LaTeX (from project root)
cd ../..
pdflatex ethical_riemann_hypothesis.tex
bibtex ethical_riemann_hypothesis
pdflatex ethical_riemann_hypothesis.tex
pdflatex ethical_riemann_hypothesis.tex
```

