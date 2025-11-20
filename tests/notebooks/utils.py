"""
Utility functions for notebook testing
"""
import os
import json
from pathlib import Path


def get_project_root():
    """Get the project root directory"""
    current = Path(__file__).resolve()
    # Go up from tests/notebooks/utils.py to project root
    return current.parent.parent.parent


def get_notebook_path(notebook_name):
    """Get full path to a notebook file"""
    project_root = get_project_root()
    return project_root / "simulation" / "notebooks" / f"{notebook_name}.ipynb"


def get_output_path(relative_path):
    """Get full path to an output file"""
    project_root = get_project_root()
    return project_root / relative_path


def parse_expected_outputs():
    """Parse expected_outputs.txt and return a dictionary"""
    project_root = get_project_root()
    expected_file = project_root / "tests" / "notebooks" / "expected_outputs.txt"
    
    outputs = {}
    with open(expected_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('|')
            if len(parts) >= 2:
                notebook = parts[0]
                file_path = parts[1]
                min_size = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                description = parts[3] if len(parts) > 3 else ""
                
                if notebook not in outputs:
                    outputs[notebook] = []
                
                outputs[notebook].append({
                    'path': file_path,
                    'min_size': min_size,
                    'description': description
                })
    
    return outputs


def verify_output_file(file_path, min_size=0):
    """Verify that an output file exists and meets size requirements"""
    full_path = get_output_path(file_path)
    
    if not full_path.exists():
        return False, f"File does not exist: {file_path}"
    
    size = full_path.stat().st_size
    if size < min_size:
        return False, f"File too small: {file_path} ({size} bytes < {min_size} bytes)"
    
    return True, f"File verified: {file_path} ({size} bytes)"


def load_notebook(notebook_path):
    """Load a notebook JSON file"""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def count_code_cells(notebook):
    """Count the number of code cells in a notebook"""
    count = 0
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            count += 1
    return count


def has_outputs(notebook):
    """Check if notebook has any cell outputs"""
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            outputs = cell.get('outputs', [])
            if outputs:
                return True
    return False

