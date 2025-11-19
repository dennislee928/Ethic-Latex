# Ethical Riemann Hypothesis - Dependency Installation Script (PowerShell)
# This script installs all required and optional dependencies

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "ETHICAL RIEMANN HYPOTHESIS - DEPENDENCY INSTALLATION" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.10+ first." -ForegroundColor Red
    exit 1
}

# Check if pip is available
try {
    $null = Get-Command pip -ErrorAction Stop
} catch {
    Write-Host "ERROR: pip not found. Please install pip first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "STEP 1: Core Dependencies (Required)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Installing: numpy, scipy, pandas" -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install numpy scipy pandas

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install core dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Core dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "STEP 2: Visualization Dependencies (Required for figures)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Installing: matplotlib, seaborn, plotly" -ForegroundColor Yellow
python -m pip install matplotlib seaborn plotly

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Failed to install visualization dependencies" -ForegroundColor Yellow
    Write-Host "Figures will not be generated, but core functionality will work" -ForegroundColor Yellow
} else {
    Write-Host "✓ Visualization dependencies installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "STEP 3: Jupyter Notebook Dependencies (Optional)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
$installJupyter = Read-Host "Install Jupyter notebooks? (y/n)"
if ($installJupyter -eq "y" -or $installJupyter -eq "Y") {
    python -m pip install jupyter ipywidgets
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Jupyter installed" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Failed to install Jupyter" -ForegroundColor Yellow
    }
} else {
    Write-Host "Skipping Jupyter installation" -ForegroundColor Gray
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "STEP 4: Development Tools (Optional)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
$installDev = Read-Host "Install development tools (black, pytest)? (y/n)"
if ($installDev -eq "y" -or $installDev -eq "Y") {
    python -m pip install black pytest
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Development tools installed" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Failed to install development tools" -ForegroundColor Yellow
    }
} else {
    Write-Host "Skipping development tools" -ForegroundColor Gray
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Testing imports..." -ForegroundColor Yellow

try { python -c "import numpy; print('✓ numpy', numpy.__version__)" 2>$null } catch { Write-Host "✗ numpy failed" -ForegroundColor Red }
try { python -c "import scipy; print('✓ scipy', scipy.__version__)" 2>$null } catch { Write-Host "✗ scipy failed" -ForegroundColor Red }
try { python -c "import pandas; print('✓ pandas', pandas.__version__)" 2>$null } catch { Write-Host "✗ pandas failed" -ForegroundColor Red }
try { python -c "import matplotlib; print('✓ matplotlib', matplotlib.__version__)" 2>$null } catch { Write-Host "✗ matplotlib failed" -ForegroundColor Red }
try { python -c "import seaborn; print('✓ seaborn')" 2>$null } catch { Write-Host "✗ seaborn failed" -ForegroundColor Red }
try { python -c "import plotly; print('✓ plotly', plotly.__version__)" 2>$null } catch { Write-Host "✗ plotly failed" -ForegroundColor Red }
try { python -c "import jupyter; print('✓ jupyter')" 2>$null } catch { Write-Host "✗ jupyter not installed (optional)" -ForegroundColor Gray }

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run: .\quick-start-script\quick-start.ps1" -ForegroundColor White
Write-Host "  2. Or: cd simulation; python run_example.py" -ForegroundColor White
Write-Host ""

