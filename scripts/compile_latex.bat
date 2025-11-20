@echo off
REM Compile LaTeX Paper (Windows)

echo ======================================================================
echo COMPILING LATEX PAPER
echo ======================================================================
echo.

where pdflatex >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pdflatex not found!
    echo.
    echo Please install a LaTeX distribution:
    echo   - MiKTeX: https://miktex.org/
    echo   - Or TeX Live: https://www.tug.org/texlive/
    pause
    exit /b 1
)

echo Found pdflatex
echo.

echo [1/4] First pdflatex pass...
pdflatex -interaction=nonstopmode ethical_riemann_hypothesis.tex >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Completed
) else (
    echo   [WARNING] Completed with warnings
)

where bibtex >nul 2>&1
if %errorlevel% equ 0 (
    echo [2/4] Running BibTeX...
    bibtex ethical_riemann_hypothesis >nul 2>&1
    if %errorlevel% equ 0 (
        echo   [OK] Completed
    ) else (
        echo   [WARNING] Completed with warnings
    )
) else (
    echo [2/4] BibTeX not found, skipping bibliography
)

echo [3/4] Second pdflatex pass...
pdflatex -interaction=nonstopmode ethical_riemann_hypothesis.tex >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Completed
) else (
    echo   [WARNING] Completed with warnings
)

echo [4/4] Third pdflatex pass...
pdflatex -interaction=nonstopmode ethical_riemann_hypothesis.tex >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Completed
) else (
    echo   [WARNING] Completed with warnings
)

echo.
if exist ethical_riemann_hypothesis.pdf (
    echo ======================================================================
    echo SUCCESS! Paper compiled: ethical_riemann_hypothesis.pdf
    echo ======================================================================
    dir ethical_riemann_hypothesis.pdf
) else (
    echo ======================================================================
    echo ERROR: PDF not generated. Check ethical_riemann_hypothesis.log
    echo ======================================================================
    exit /b 1
)

