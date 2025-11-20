@echo off
REM Ethical Riemann Hypothesis - Quick Start Script (Windows Batch)
REM This script can be run from anywhere

REM Get the script directory
set "SCRIPT_DIR=%~dp0"
REM Get project root (parent directory)
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"

echo Project root: %PROJECT_ROOT%
echo Changing to project root...
cd /d "%PROJECT_ROOT%"

REM Check if we're in the right directory
if not exist "simulation" (
    echo ERROR: 'simulation' directory not found!
    echo Please ensure the script is in the correct location.
    exit /b 1
)

echo.
echo ======================================================================
echo STEP 1: Quick Example
echo ======================================================================
cd simulation
python run_example.py

echo.
echo ======================================================================
echo STEP 2: Generate All Figures (optional - requires matplotlib)
echo ======================================================================
echo Checking if matplotlib is installed...
python -c "import matplotlib" 2>nul
if %errorlevel% equ 0 (
    echo matplotlib found. Generating figures...
    python generate_all_figures.py
) else (
    echo WARNING: matplotlib not installed. Skipping figure generation.
    echo Install with: pip install matplotlib seaborn
)

cd /d "%PROJECT_ROOT%"

echo.
echo ======================================================================
echo STEP 3: Jupyter Notebooks (optional)
echo ======================================================================
echo To open Jupyter notebooks, run:
echo   cd simulation/notebooks
echo   jupyter notebook
echo.
echo Or install Jupyter first: pip install jupyter

echo.
echo ======================================================================
echo STEP 4: Compile LaTeX Paper (optional - requires LaTeX)
echo ======================================================================
where pdflatex >nul 2>&1
if %errorlevel% equ 0 (
    echo LaTeX found. Compiling paper...
    pdflatex ethical_riemann_hypothesis.tex
    bibtex ethical_riemann_hypothesis
    pdflatex ethical_riemann_hypothesis.tex
    pdflatex ethical_riemann_hypothesis.tex
    echo Paper compiled successfully!
) else (
    echo WARNING: pdflatex not found. Skipping LaTeX compilation.
    echo Install a LaTeX distribution (e.g., MiKTeX, TeX Live)
)

echo.
echo ======================================================================
echo Quick start complete!
echo ======================================================================

