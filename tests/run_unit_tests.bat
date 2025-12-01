@echo off
REM Run unit tests for psychohistory integration modules

cd /d "%~dp0"

echo ======================================================================
echo RUNNING UNIT TESTS FOR PSYCHOHISTORY INTEGRATION
echo ======================================================================
echo.

REM Check if pytest is available
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pytest not found. Install with: pip install pytest
    exit /b 1
)

echo Using pytest command: python -m pytest
echo.

REM Run tests
echo Running unit tests...
python -m pytest ^
    test_temporal_erh.py ^
    test_agent_framework.py ^
    test_social_network.py ^
    test_meta_monitor.py ^
    test_hybrid_model.py ^
    test_psychohistory_integration.py ^
    -v ^
    --tb=short

if errorlevel 1 (
    echo.
    echo ======================================================================
    echo FAILURE: Some tests failed. Check output above for details.
    echo ======================================================================
    exit /b 1
) else (
    echo.
    echo ======================================================================
    echo SUCCESS: All unit tests passed!
    echo ======================================================================
)


