# Installation Guide

This guide will help you install all dependencies for the Ethical Riemann Hypothesis project.

## Quick Installation

### Option 1: Use Installation Script (Recommended)

**For Linux/macOS/Git Bash:**
```bash
bash install_dependencies.sh
```

**For Windows PowerShell:**
```powershell
.\install_dependencies.ps1
```

**For Windows CMD:**
```cmd
install_dependencies.bat
```

### Option 2: Manual Installation

```bash
pip install -r requirements.txt
```

**Note:** The `latex` package in requirements.txt is commented out because it's not a valid Python package. LaTeX rendering requires a system LaTeX installation (see below).

## Dependency Categories

### Required (Core Functionality)
- **numpy** (>=1.24.0) - Numerical computing
- **scipy** (>=1.10.0) - Scientific computing
- **pandas** (>=2.0.0) - Data manipulation

### Required for Figures
- **matplotlib** (>=3.7.0) - Plotting library
- **seaborn** (>=0.12.0) - Statistical visualization
- **plotly** (>=5.14.0) - Interactive plots

### Optional
- **jupyter** (>=1.0.0) - Jupyter notebooks
- **ipywidgets** (>=8.0.0) - Interactive widgets
- **black** (>=23.0.0) - Code formatter
- **pytest** (>=7.3.0) - Testing framework

## System Requirements

### Python
- **Python 3.10 or later** is required
- Check your version: `python --version`

### LaTeX (Optional, for paper compilation)
LaTeX is **not** a Python package. Install separately:

- **Windows**: [MiKTeX](https://miktex.org/)
- **macOS**: [MacTeX](https://www.tug.org/mactex/)
- **Linux**: 
  ```bash
  sudo apt-get install texlive-full  # Ubuntu/Debian
  sudo yum install texlive-scheme-full  # CentOS/RHEL
  ```

## Troubleshooting

### "pip: command not found"
Install pip first:
```bash
python -m ensurepip --upgrade
# or
python -m pip install --upgrade pip
```

### "Permission denied" errors
Use `--user` flag:
```bash
pip install --user -r requirements.txt
```

### Matplotlib installation fails
On some systems, matplotlib requires additional system libraries:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**macOS:**
```bash
brew install python-tk
```

**Windows:**
Usually works out of the box, but if issues occur, try:
```bash
pip install --upgrade matplotlib --no-cache-dir
```

### NumPy/SciPy installation fails
These packages may require compilation. Try:

1. **Use pre-built wheels:**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install numpy scipy
   ```

2. **Install from conda (if available):**
   ```bash
   conda install numpy scipy
   ```

3. **Use system package manager:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-numpy python3-scipy
   ```

### Version conflicts
If you have version conflicts:

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Import errors after installation
If packages install but imports fail:

1. **Check Python path:**
   ```python
   import sys
   print(sys.path)
   ```

2. **Reinstall problematic package:**
   ```bash
   pip uninstall <package-name>
   pip install <package-name>
   ```

3. **Verify installation:**
   ```python
   python -c "import numpy; print(numpy.__version__)"
   ```

## Verification

After installation, verify everything works:

```bash
cd simulation
python run_example.py
```

You should see output like:
```
[1/5] Generating action space...
      Created 500 actions
...
Results:
  Estimated exponent α: 1.292
  ERH satisfied:       No ✗
```

## Minimal Installation

If you only want to run the core simulation (no figures):

```bash
pip install numpy scipy pandas
```

Then run:
```bash
cd simulation
python run_example.py
```

Figures will be skipped automatically if matplotlib is not installed.

## Development Installation

For full development environment:

```bash
pip install -r requirements.txt
pip install black pytest jupyter ipywidgets
```

## Docker Installation (Future)

A Dockerfile may be added in the future for containerized installation.

## Getting Help

If you encounter issues:

1. Check Python version: `python --version` (should be 3.10+)
2. Check pip version: `pip --version`
3. Try upgrading pip: `pip install --upgrade pip`
4. Check error messages carefully
5. Search for specific error messages online
6. Open an issue on GitHub with:
   - Python version
   - Operating system
   - Full error message
   - Steps to reproduce

## Next Steps

After successful installation:

1. **Run quick example:**
   ```bash
   bash quick-start-script/quick-start.sh
   ```

2. **Explore notebooks:**
   ```bash
   cd simulation/notebooks
   jupyter notebook
   ```

3. **Generate figures:**
   ```bash
   cd simulation
   python generate_all_figures.py
   ```

4. **Read the paper:**
   - Compile LaTeX: `pdflatex ethical_riemann_hypothesis.tex`
   - Or view the source: `ethical_riemann_hypothesis.tex`

