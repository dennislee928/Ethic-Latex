@echo off
REM Run Robot Framework tests for Jupyter notebooks (Windows)

cd /d "%~dp0"

echo ======================================================================
echo RUNNING NOTEBOOK TESTS WITH ROBOT FRAMEWORK
echo ======================================================================
echo.

REM Check if Robot Framework is installed
where robot >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Robot Framework not found!
    echo.
    echo Install with:
    echo   pip install robotframework robotframework-jupyterlibrary
    echo.
    echo Or install all dependencies:
    echo   pip install -r ..\requirements.txt
    pause
    exit /b 1
)

echo Found robot
echo.

REM Create output directory if it doesn't exist
if not exist notebooks\output mkdir notebooks\output

REM Run tests
echo Running notebook tests...
robot ^
    --outputdir notebooks\output ^
    --log notebooks\output\log.html ^
    --report notebooks\output\report.html ^
    --xunit notebooks\output\xunit.xml ^
    notebooks\notebook_tests.robot

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo SUCCESS: All notebook tests passed!
    echo ======================================================================
    echo.
    echo Test results:
    echo   - Log: notebooks\output\log.html
    echo   - Report: notebooks\output\report.html
) else (
    echo.
    echo ======================================================================
    echo FAILURE: Some tests failed. Check notebooks\output\log.html for details.
    echo ======================================================================
)

pause
exit /b %errorlevel%

