@echo off
REM Start Jupyter Notebook Server (Windows)

cd ..\simulation\notebooks

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

REM Try multiple ways to start Jupyter
where jupyter >nul 2>&1
if %errorlevel% equ 0 (
    jupyter notebook
) else (
    python -c "import notebook" >nul 2>&1
    if %errorlevel% equ 0 (
        echo Using: python -m notebook
        python -m notebook
    ) else (
        python -c "import jupyterlab" >nul 2>&1
        if %errorlevel% equ 0 (
            echo Using: python -m jupyterlab (JupyterLab instead)
            python -m jupyterlab
        ) else (
            echo ERROR: Jupyter not found!
            echo.
            echo Install Jupyter with:
            echo   pip install jupyter ipywidgets
            echo.
            echo Or use:
            echo   scripts\install_dependencies.bat
            echo.
            echo Note: If Jupyter is installed but command not found,
            echo try: python -m notebook
            pause
            exit /b 1
        )
    )
)

