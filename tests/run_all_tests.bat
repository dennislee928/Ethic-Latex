@echo off
REM Run all tests: unit tests + notebook tests

cd /d "%~dp0"

echo ======================================================================
echo RUNNING ALL TESTS
echo ======================================================================
echo.

SET EXIT_CODE=0

REM Run unit tests
echo Step 1: Running unit tests...
echo ----------------------------------------------------------------------
call run_unit_tests.bat
if errorlevel 1 (
    SET EXIT_CODE=1
)

echo.
echo.

REM Run notebook tests
echo Step 2: Running notebook tests...
echo ----------------------------------------------------------------------
call run_notebook_tests.bat
if errorlevel 1 (
    SET EXIT_CODE=1
)

echo.
echo ======================================================================
if %EXIT_CODE%==0 (
    echo SUCCESS: All tests passed!
) else (
    echo FAILURE: Some tests failed.
)
echo ======================================================================

exit /b %EXIT_CODE%

