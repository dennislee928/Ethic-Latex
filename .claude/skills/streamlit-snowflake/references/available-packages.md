# Available Packages for Streamlit in Snowflake

Streamlit in Snowflake only supports packages from the **Snowflake Anaconda Channel**. External channels (conda-forge, pip) are not supported.

## Checking Available Packages

### SQL Query

```sql
-- List all available Python packages
SELECT
    package_name,
    version,
    language
FROM information_schema.packages
WHERE language = 'python'
ORDER BY package_name;

-- Search for specific package
SELECT *
FROM information_schema.packages
WHERE language = 'python'
AND package_name ILIKE '%plotly%';

-- Get latest version of a package
SELECT
    package_name,
    MAX(version) as latest_version
FROM information_schema.packages
WHERE language = 'python'
AND package_name = 'streamlit'
GROUP BY package_name;
```

### Using REPODATA Function

```sql
-- Get full package metadata
SELECT *
FROM TABLE(SNOWFLAKE.SNOWPARK.GET_ANACONDA_PACKAGES_REPODATA('linux-64'))
WHERE name ILIKE '%pandas%';
```

### Web Tool

Use the community package explorer:
**[Snowpark Python Packages Explorer](https://snowpark-python-packages.streamlit.app/)**

## Common Available Packages

### Data Processing
- `pandas` - DataFrames and data manipulation
- `numpy` - Numerical computing
- `scipy` - Scientific computing
- `polars` - Fast DataFrame library

### Visualization
- `streamlit` (1.22.0 default, 1.35.0 available)
- `plotly` - Interactive charts
- `altair` (4.0) - Declarative visualization
- `matplotlib` - Static plots
- `seaborn` - Statistical visualization

### Machine Learning
- `scikit-learn` - ML algorithms
- `xgboost` - Gradient boosting
- `lightgbm` - Gradient boosting
- `statsmodels` - Statistical models

### Snowflake
- `snowflake-snowpark-python` - Snowpark API
- `snowflake-connector-python` - Direct connector

### Utilities
- `pillow` - Image processing
- `requests` - HTTP library (limited use in SiS)
- `pyyaml` - YAML parsing
- `python-dateutil` - Date utilities

## Package Limitations

### Not Available
- Packages from conda-forge
- Packages requiring native compilation not in channel
- Custom/private packages
- Packages with system dependencies

### Version Constraints
- Some packages have specific version requirements
- Check compatibility with Snowpark version
- Streamlit versions: 1.22.0 (default), up to 1.35.0

## Adding Packages to environment.yml

```yaml
name: sf_env
channels:
  - snowflake  # REQUIRED - only channel

dependencies:
  - streamlit=1.35.0   # Always pin version
  - pandas
  - plotly
  - scikit-learn
  # Check availability before adding more
```

## Troubleshooting

### "PackageNotFoundError"
- Package not in Snowflake channel
- Check spelling and case
- Use SQL query to verify availability

### Version Conflicts
- Some packages have interdependencies
- Try removing version pins
- Check Snowpark compatibility

### Package Not Loading
- Restart app after environment.yml changes
- Check for syntax errors in YAML
- Verify `channels: - snowflake` is present
