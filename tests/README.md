# Testing Documentation

This directory contains test files for the Ethical Riemann Hypothesis project.

## Structure

```
tests/
├── notebooks/              # Notebook tests (Robot Framework)
│   ├── notebook_tests.robot    # Main test suite
│   ├── resources/              # Test resources
│   ├── output/                 # Test output (logs, reports)
│   ├── expected_outputs.txt    # List of expected output files
│   └── utils.py                # Python utility functions
├── test_streamlit_app.py   # Streamlit app import test
├── verify_outputs.py       # Output file verification
└── README.md              # This file
```

## Notebook Testing with Robot Framework

The notebook tests use Robot Framework with the JupyterLibrary to execute and verify Jupyter notebooks.

### Prerequisites

Install Robot Framework and dependencies:

```bash
pip install -r ../requirements.txt
```

Or install manually:

```bash
pip install robotframework robotframework-jupyterlibrary robotframework-pythonlibcore
```

### Running Tests

**Linux/macOS:**
```bash
cd tests
bash run_notebook_tests.sh
```

**Windows:**
```cmd
cd tests
run_notebook_tests.bat
```

**Direct Robot Framework command:**
```bash
robot --outputdir tests/notebooks/output tests/notebooks/notebook_tests.robot
```

### What Gets Tested

Each notebook test verifies:

1. **Execution Success**: The notebook can be executed without errors
2. **Output Files**: Expected output files (PDFs, CSVs, etc.) are generated
3. **File Sizes**: Output files meet minimum size requirements (non-empty)
4. **Key Results**: Critical variables and results are present

### Test Coverage

The following notebooks are tested:

- `01_basic_simulation.ipynb` - Basic simulation and core concepts
- `02_judge_comparison.ipynb` - Judge comparison and reporting
- `03_zeta_zeros.ipynb` - Zeta function zero analysis
- `04_parameter_sensitivity.ipynb` - Parameter sensitivity analysis
- `05_generate_paper_figures.ipynb` - Paper figure generation
- `06_baseline_comparison.ipynb` - Baseline function comparison
- `07_zeta_zeros_deep_analysis.ipynb` - Deep zeta zero analysis

### Test Output

After running tests, check:

- `tests/notebooks/output/log.html` - Detailed execution log
- `tests/notebooks/output/report.html` - Test report with statistics
- `tests/notebooks/output/xunit.xml` - XML format for CI/CD integration

### Expected Outputs

The `expected_outputs.txt` file lists all expected output files for each notebook, including:

- PDF figures (plots, visualizations)
- CSV data files
- Markdown reports
- Text summaries

Each output file has a minimum size requirement to ensure it's not empty.

## Other Tests

### Streamlit App Test

Test that the Streamlit app can be imported correctly:

```bash
python tests/test_streamlit_app.py
```

### Output Verification

Verify that all expected output files exist:

```bash
python tests/verify_outputs.py
```

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Notebook Tests
  run: |
    pip install -r requirements.txt
    cd tests
    bash run_notebook_tests.sh
```

## Troubleshooting

### Robot Framework Not Found

If you get "robot: command not found", ensure Robot Framework is installed:

```bash
pip install robotframework robotframework-jupyterlibrary
```

### Jupyter Server Issues

If notebook execution fails, ensure Jupyter is properly installed:

```bash
pip install jupyter ipykernel
```

### Missing Output Files

If tests fail due to missing output files:

1. Run the notebooks manually first to generate outputs
2. Check that output directories exist: `simulation/output/figures/`
3. Verify notebook execution completes successfully

### Timeout Issues

If tests timeout, you can increase the timeout in `notebook_tests.robot`:

```robot
*** Variables ***
${NOTEBOOK_TIMEOUT}    1200s  # Increase from 600s
```

## Contributing

When adding new notebooks:

1. Add test case to `notebook_tests.robot`
2. Add expected outputs to `expected_outputs.txt`
3. Update this README with new notebook information

