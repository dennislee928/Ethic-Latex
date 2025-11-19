"""
Common utilities for Jupyter notebooks.

Provides robust path setup, import verification, and common helpers.
"""

import sys
import os
from pathlib import Path


def setup_paths():
    """
    Add simulation directory to Python path, works in all environments.
    
    Tries multiple strategies to find the simulation directory:
    1. If in notebooks/, go up one level
    2. If in simulation/, use current
    3. Look for simulation directory in parents
    4. Try relative paths
    5. Fallback to common paths
    
    Returns:
        str: Path to simulation directory, or None if not found
    """
    current_dir = Path(os.getcwd())
    
    # Strategy 1: If in notebooks/, go up one level
    if current_dir.name == 'notebooks':
        simulation_dir = str(current_dir.parent)
        if simulation_dir not in sys.path:
            sys.path.insert(0, simulation_dir)
        return simulation_dir
    
    # Strategy 2: If in simulation/, use current
    if current_dir.name == 'simulation':
        simulation_dir = str(current_dir)
        if simulation_dir not in sys.path:
            sys.path.insert(0, simulation_dir)
        return simulation_dir
    
    # Strategy 3: Look for simulation directory in parents
    for parent in current_dir.parents:
        if parent.name == 'simulation':
            simulation_dir = str(parent)
            if simulation_dir not in sys.path:
                sys.path.insert(0, simulation_dir)
            return simulation_dir
    
    # Strategy 4: Try relative path
    simulation_dir = os.path.join(os.getcwd(), 'simulation')
    if os.path.exists(simulation_dir):
        if simulation_dir not in sys.path:
            sys.path.insert(0, simulation_dir)
        return simulation_dir
    
    # Strategy 5: Try going up from notebooks
    notebooks_dir = os.path.join(os.getcwd(), 'notebooks')
    if os.path.exists(notebooks_dir):
        parent = os.path.dirname(os.path.abspath(notebooks_dir))
        if parent not in sys.path:
            sys.path.insert(0, parent)
        return parent
    
    # Fallback: add common paths
    for path in ['..', '../simulation', 'simulation', os.path.dirname(os.getcwd())]:
        abs_path = os.path.abspath(path)
        if abs_path not in sys.path and os.path.exists(abs_path):
            sys.path.insert(0, abs_path)
    
    return None


def verify_imports(modules):
    """
    Verify that required modules can be imported.
    
    Args:
        modules (list): List of module names to verify (e.g., ['core.action_space'])
    
    Returns:
        dict: Results for each module {'module_name': (success, error_message)}
    """
    results = {}
    for module_name in modules:
        try:
            __import__(module_name)
            results[module_name] = (True, None)
        except ImportError as e:
            results[module_name] = (False, str(e))
    return results


def print_import_status(results):
    """Print import verification results in a readable format."""
    print("Import Status:")
    print("-" * 60)
    for module_name, (success, error) in results.items():
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {module_name}")
        if not success:
            print(f"      Error: {error}")
    print("-" * 60)


def ensure_output_dir(subdir=''):
    """
    Ensure output directory exists.
    
    Args:
        subdir (str): Subdirectory name (e.g., 'figures', 'reports')
    
    Returns:
        str: Path to output directory
    """
    current_dir = Path(os.getcwd())
    
    # Try to find simulation directory
    if current_dir.name == 'notebooks':
        base_dir = current_dir.parent
    elif current_dir.name == 'simulation':
        base_dir = current_dir
    else:
        # Look for simulation in parents
        base_dir = None
        for parent in current_dir.parents:
            if parent.name == 'simulation':
                base_dir = parent
                break
        
        if base_dir is None:
            base_dir = Path(os.getcwd())
    
    output_dir = base_dir / 'output'
    if subdir:
        output_dir = output_dir / subdir
    
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir)

