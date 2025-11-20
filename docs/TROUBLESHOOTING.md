# Troubleshooting Guide

## Common Issues and Solutions

### 1. Jupyter Command Not Found

**Problem:** `jupyter: command not found` even though Jupyter is installed

**Cause:** On Windows, when packages are installed with `--user`, the scripts go to a directory not in PATH.

**Solutions:**

**Option A: Use Python module syntax (Recommended)**
```bash
python -m jupyter notebook
```

**Option B: Add Scripts to PATH**
1. Find your Python Scripts directory:
   ```bash
   python -c "import site; print(site.USER_BASE + '/Scripts')"
   ```
2. Add it to your PATH environment variable
3. Restart terminal

**Option C: Use the provided scripts**
```bash
bash start_jupyter.sh
# or
start_jupyter.bat
```

### 2. LaTeX Not Found

**Problem:** `pdflatex: command not found`

**Solution:** Install a LaTeX distribution:
- **Windows**: [MiKTeX](https://miktex.org/) (recommended)
- **macOS**: [MacTeX](https://www.tug.org/mactex/)
- **Linux**: `sudo apt-get install texlive-full`

After installation, restart your terminal.

**Alternative:** Use the compile script:
```bash
bash compile_latex.sh
# or
compile_latex.bat
```

### 3. Import Errors in Notebooks

**Problem:** `ModuleNotFoundError` when running notebooks

**Solutions:**

1. **Make sure you're in the right directory:**
   ```bash
   cd simulation/notebooks
   ```

2. **Check Python path:**
   The notebooks automatically add the parent directory. If it fails:
   ```python
   import sys
   sys.path.insert(0, '..')
   ```

3. **Install missing packages:**
   ```bash
   pip install -r ../requirements.txt
   ```

### 4. Unicode Encoding Errors

**Problem:** `UnicodeEncodeError: 'cp950' codec can't encode character`

**Solution:** This is already fixed in the code. If you still see it:
- The code now uses ASCII-safe characters
- If errors persist, set environment variable:
  ```bash
  export PYTHONIOENCODING=utf-8
  ```

### 5. Relative Import Errors

**Problem:** `ImportError: attempted relative import beyond top-level package`

**Solution:** This is already fixed. The code handles both relative and absolute imports automatically.

### 6. Matplotlib Backend Issues

**Problem:** Plots don't display or errors about display

**Solution:** The scripts use `matplotlib.use('Agg')` for non-interactive mode. For notebooks:
```python
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg' on Windows
```

### 7. File Not Found Errors

**Problem:** Scripts can't find files

**Solution:** Always run scripts from the project root:
```bash
cd D:\GitHub\Ethic-Latex
bash quick-start-script/quick-start.sh
```

### 8. PATH Issues on Windows

**Problem:** Commands not found even though installed

**Common causes:**
- Python Scripts directory not in PATH
- Multiple Python installations
- Virtual environment not activated

**Solutions:**

1. **Use Python module syntax:**
   ```bash
   python -m pip install jupyter
   python -m jupyter notebook
   ```

2. **Find where scripts are installed:**
   ```bash
   python -c "import site; print(site.USER_BASE)"
   ```

3. **Add to PATH manually:**
   - Windows: System Properties → Environment Variables
   - Add: `C:\Users\YourName\AppData\Roaming\Python\Python314\Scripts`

### 9. Verification

**Check if everything is installed:**
```bash
python verify_outputs.py
```

**Test imports:**
```python
python -c "from simulation.core import generate_world; print('OK')"
```

**Test Jupyter:**
```bash
python -m jupyter --version
```

### 10. Getting Help

If you encounter other issues:

1. **Check error messages carefully** - they often contain the solution
2. **Verify Python version:** `python --version` (should be 3.10+)
3. **Check package versions:** `pip list | grep jupyter`
4. **Try in a fresh terminal** - sometimes PATH changes need a restart
5. **Use Python module syntax** - `python -m <module>` always works

## Quick Reference

### Starting Jupyter (when command not found)
```bash
# Method 1: Use Python module
python -m jupyter notebook

# Method 2: Use script
bash start_jupyter.sh

# Method 3: Direct path (if you know it)
C:\Users\YourName\AppData\Roaming\Python\Python314\Scripts\jupyter.exe notebook
```

### Compiling LaTeX (when command not found)
```bash
# Method 1: Use script
bash compile_latex.sh

# Method 2: Install LaTeX first
# Windows: Download MiKTeX installer
# Then: pdflatex ethical_riemann_hypothesis.tex
```

### Verifying Installation
```bash
# Check Python
python --version

# Check packages
python -c "import numpy, scipy, pandas, matplotlib, jupyter; print('All OK')"

# Check files
python verify_outputs.py
```

## Still Having Issues?

1. **Check the logs:**
   - Python errors: Look at the full traceback
   - LaTeX errors: Check `ethical_riemann_hypothesis.log`

2. **Try minimal test:**
   ```bash
   cd simulation
   python run_example.py
   ```
   If this works, the core framework is fine.

3. **Reinstall if needed:**
   ```bash
   pip uninstall jupyter
   pip install jupyter
   ```

4. **Check system requirements:**
   - Python 3.10+
   - Sufficient disk space
   - Write permissions in project directory

