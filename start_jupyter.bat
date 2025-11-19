@echo off
REM Start Jupyter Notebook Server (Windows)

cd simulation\notebooks

echo ======================================================================
echo STARTING JUPYTER NOTEBOOK SERVER
echo ======================================================================
echo.
echo Notebook directory: %CD%
echo.
echo The Jupyter interface will open in your browser.
echo Press Ctrl+C to stop the server.
echo.
echo ======================================================================
echo.

where jupyter >nul 2>&1
if %errorlevel% equ 0 (
    jupyter notebook
) else (
    echo ERROR: Jupyter not found!
    echo.
    echo Install Jupyter with:
    echo   pip install jupyter ipywidgets
    echo.
    echo Or use:
    echo   install_dependencies.bat
    pause
    exit /b 1
)

