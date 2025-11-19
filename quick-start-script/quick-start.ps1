# Ethical Riemann Hypothesis - Quick Start Script (PowerShell)
# This script can be run from anywhere

# Get the script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "Project root: $ProjectRoot"
Write-Host "Changing to project root..." -ForegroundColor Green
Set-Location $ProjectRoot

# Check if we're in the right directory
if (-not (Test-Path "simulation")) {
    Write-Host "ERROR: 'simulation' directory not found!" -ForegroundColor Red
    Write-Host "Please ensure the script is in the correct location."
    exit 1
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "STEP 1: Quick Example" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Set-Location simulation
python run_example.py

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "STEP 2: Generate All Figures (optional - requires matplotlib)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Checking if matplotlib is installed..."
try {
    python -c "import matplotlib" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "matplotlib found. Generating figures..." -ForegroundColor Green
        python generate_all_figures.py
    } else {
        throw "matplotlib not found"
    }
} catch {
    Write-Host "WARNING: matplotlib not installed. Skipping figure generation." -ForegroundColor Yellow
    Write-Host "Install with: pip install matplotlib seaborn" -ForegroundColor Yellow
}

Set-Location $ProjectRoot

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "STEP 3: Jupyter Notebooks (optional)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "To open Jupyter notebooks, run:"
Write-Host "  cd simulation/notebooks" -ForegroundColor Yellow
Write-Host "  jupyter notebook" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or install Jupyter first: pip install jupyter" -ForegroundColor Yellow

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "STEP 4: Compile LaTeX Paper (optional - requires LaTeX)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
if (Get-Command pdflatex -ErrorAction SilentlyContinue) {
    Write-Host "LaTeX found. Compiling paper..." -ForegroundColor Green
    pdflatex ethical_riemann_hypothesis.tex
    bibtex ethical_riemann_hypothesis
    pdflatex ethical_riemann_hypothesis.tex
    pdflatex ethical_riemann_hypothesis.tex
    Write-Host "Paper compiled successfully!" -ForegroundColor Green
} else {
    Write-Host "WARNING: pdflatex not found. Skipping LaTeX compilation." -ForegroundColor Yellow
    Write-Host "Install a LaTeX distribution (e.g., MiKTeX, TeX Live)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Quick start complete!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

