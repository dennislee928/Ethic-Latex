-- =============================================================================
-- Snowflake Anaconda Channel Package Queries
-- Run these in Snowsight or via Snowflake CLI
-- =============================================================================

-- -----------------------------------------------------------------------------
-- List all available Python packages
-- -----------------------------------------------------------------------------
SELECT
    package_name,
    version,
    language
FROM information_schema.packages
WHERE language = 'python'
ORDER BY package_name, version DESC;


-- -----------------------------------------------------------------------------
-- Search for specific package (case-insensitive)
-- -----------------------------------------------------------------------------
-- Replace 'plotly' with your package name
SELECT *
FROM information_schema.packages
WHERE language = 'python'
AND package_name ILIKE '%plotly%'
ORDER BY version DESC;


-- -----------------------------------------------------------------------------
-- Get latest version of a package
-- -----------------------------------------------------------------------------
SELECT
    package_name,
    MAX(version) as latest_version
FROM information_schema.packages
WHERE language = 'python'
AND package_name = 'streamlit'  -- Replace with package name
GROUP BY package_name;


-- -----------------------------------------------------------------------------
-- Check if specific version is available
-- -----------------------------------------------------------------------------
SELECT *
FROM information_schema.packages
WHERE language = 'python'
AND package_name = 'streamlit'
AND version = '1.35.0';


-- -----------------------------------------------------------------------------
-- List commonly used packages with versions
-- -----------------------------------------------------------------------------
SELECT
    package_name,
    MAX(version) as latest_version
FROM information_schema.packages
WHERE language = 'python'
AND package_name IN (
    'streamlit',
    'pandas',
    'numpy',
    'plotly',
    'altair',
    'matplotlib',
    'scikit-learn',
    'xgboost',
    'snowflake-snowpark-python',
    'pillow',
    'scipy'
)
GROUP BY package_name
ORDER BY package_name;


-- -----------------------------------------------------------------------------
-- Get package metadata using REPODATA function
-- (More detailed info including dependencies)
-- -----------------------------------------------------------------------------
SELECT *
FROM TABLE(SNOWFLAKE.SNOWPARK.GET_ANACONDA_PACKAGES_REPODATA('linux-64'))
WHERE name = 'streamlit'
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Count available packages by category
-- (Approximate based on naming patterns)
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN package_name ILIKE '%ml%' OR package_name ILIKE '%sklearn%' THEN 'Machine Learning'
        WHEN package_name ILIKE '%plot%' OR package_name ILIKE '%chart%' OR package_name ILIKE '%viz%' THEN 'Visualization'
        WHEN package_name ILIKE '%sql%' OR package_name ILIKE '%db%' THEN 'Database'
        WHEN package_name ILIKE '%test%' OR package_name ILIKE '%pytest%' THEN 'Testing'
        ELSE 'Other'
    END as category,
    COUNT(DISTINCT package_name) as package_count
FROM information_schema.packages
WHERE language = 'python'
GROUP BY category
ORDER BY package_count DESC;
