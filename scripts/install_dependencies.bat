@echo off
REM Ethical Riemann Hypothesis - Dependency Installation Script (Windows Batch)
REM This script installs all required and optional dependencies

echo ======================================================================
echo ETHICAL RIEMANN HYPOTHESIS - DEPENDENCY INSTALLATION
echo ======================================================================
echo.

REM Check Python
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.10+ first.
    exit /b 1
)
python --version

REM Check pip
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip not found. Please install pip first.
    exit /b 1
)

echo.
echo ======================================================================
echo STEP 1: Core Dependencies (Required)
echo ======================================================================
echo Installing: numpy, scipy, pandas
python -m pip install --upgrade pip
python -m pip install numpy scipy pandas

if %errorlevel% neq 0 (
    echo ERROR: Failed to install core dependencies
    exit /b 1
)
echo [OK] Core dependencies installed

echo.
echo ======================================================================
echo STEP 2: Visualization Dependencies (Required for figures)
echo ======================================================================
echo Installing: matplotlib, seaborn, plotly
python -m pip install matplotlib seaborn plotly

if %errorlevel% neq 0 (
    echo WARNING: Failed to install visualization dependencies
    echo Figures will not be generated, but core functionality will work
) else (
    echo [OK] Visualization dependencies installed
)

echo.
echo ======================================================================
echo STEP 3: Jupyter Notebook Dependencies (Optional)
echo ======================================================================
set /p installJupyter="Install Jupyter notebooks? (y/n): "
if /i "%installJupyter%"=="y" (
    python -m pip install jupyter ipywidgets
    if %errorlevel% equ 0 (
        echo [OK] Jupyter installed
    ) else (
        echo WARNING: Failed to install Jupyter
    )
) else (
    echo Skipping Jupyter installation
)

echo.
echo ======================================================================
echo STEP 4: Development Tools (Optional)
echo ======================================================================
set /p installDev="Install development tools (black, pytest)? (y/n): "
if /i "%installDev%"=="y" (
    python -m pip install black pytest
    if %errorlevel% equ 0 (
        echo [OK] Development tools installed
    ) else (
        echo WARNING: Failed to install development tools
    )
) else (
    echo Skipping development tools
)

echo.
echo ======================================================================
echo Verification
echo ======================================================================
echo Testing imports...
python -c "import numpy; print('[OK] numpy', numpy.__version__)" 2>nul || echo [FAIL] numpy
python -c "import scipy; print('[OK] scipy', scipy.__version__)" 2>nul || echo [FAIL] scipy
python -c "import pandas; print('[OK] pandas', pandas.__version__)" 2>nul || echo [FAIL] pandas
python -c "import matplotlib; print('[OK] matplotlib', matplotlib.__version__)" 2>nul || echo [FAIL] matplotlib
python -c "import seaborn; print('[OK] seaborn')" 2>nul || echo [FAIL] seaborn
python -c "import plotly; print('[OK] plotly', plotly.__version__)" 2>nul || echo [FAIL] plotly
python -c "import jupyter; print('[OK] jupyter')" 2>nul || echo [SKIP] jupyter not installed (optional)

echo.
echo ======================================================================
echo Installation Complete!
echo ======================================================================
echo.
echo Next steps:
echo   1. Run: quick-start-script\quick-start.bat
echo   2. Or: cd simulation ^&^& python run_example.py
echo.

