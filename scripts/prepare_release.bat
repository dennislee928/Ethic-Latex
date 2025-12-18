@echo off
REM Script to prepare v0.9-pre-submission release (Windows version)
REM This script helps prepare files for GitHub release

set VERSION=v0.9-pre-submission
set RELEASE_DIR=release_%VERSION%

echo Preparing release: %VERSION%

REM Create release directory
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"

REM Copy PDFs (assuming they are generated)
if exist "ethical_riemann_hypothesis_en.pdf" (
    copy "ethical_riemann_hypothesis_en.pdf" "%RELEASE_DIR%\"
    echo [OK] Copied English PDF
) else (
    echo [WARNING] ethical_riemann_hypothesis_en.pdf not found. Please compile first.
)

if exist "ethical_riemann_hypothesis_zh.pdf" (
    copy "ethical_riemann_hypothesis_zh.pdf" "%RELEASE_DIR%\"
    echo [OK] Copied Chinese PDF
) else (
    echo [WARNING] ethical_riemann_hypothesis_zh.pdf not found. Please compile first.
)

echo.
echo Release preparation complete!
echo Release files will be in: %RELEASE_DIR%\
echo.
echo Next steps:
echo 1. Review the files
echo 2. Create a GitHub release tag: git tag -a %VERSION% -m "Pre-submission version"
echo 3. Push the tag: git push origin %VERSION%
echo 4. Create a GitHub release and upload files



