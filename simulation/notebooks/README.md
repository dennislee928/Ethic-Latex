# Jupyter Notebooks

This directory contains interactive Jupyter notebooks for exploring the Ethical Riemann Hypothesis framework.

## Starting Jupyter

### Method 1: From Project Root
```bash
cd simulation/notebooks
jupyter notebook
```

### Method 2: Using Quick Start Script
```bash
bash quick-start-script/quick-start.sh
# When prompted, Jupyter will start automatically
```

### Method 3: JupyterLab (Modern Interface)
```bash
cd simulation/notebooks
jupyter lab
```

## Notebooks

1. **01_basic_simulation.ipynb** - Introduction and basic concepts
2. **02_judge_comparison.ipynb** - Comparing different judgment systems
3. **03_zeta_zeros.ipynb** - Exploring the ethical zeta function zeros
4. **04_parameter_sensitivity.ipynb** - Parameter sensitivity analysis
5. **05_generate_paper_figures.ipynb** - Generate all paper figures

## Troubleshooting

### Import Errors
If you see import errors, make sure you're running the notebook from the `simulation/notebooks/` directory. The notebooks automatically add the parent directory to the Python path.

### Kernel Issues
If the kernel doesn't start:
1. Check Python installation: `python --version`
2. Install ipykernel: `pip install ipykernel`
3. Register kernel: `python -m ipykernel install --user`

### Path Issues
The notebooks use relative imports. If imports fail:
1. Make sure you're in the `simulation/notebooks/` directory
2. Check that the `simulation/` directory structure is intact
3. Try restarting the kernel and running all cells

## Output

Notebooks will generate outputs in:
- `../output/figures/` - Generated plots
- `../output/` - Reports and data files

