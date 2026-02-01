"""
Ethical Riemann Hypothesis Core Module

Shared core implementation used by both simulation/ and erh/ packages.
This module contains the core logic for ERH simulations and analysis.
"""

__version__ = "0.1.0"

# Ensure this module is importable
from pathlib import Path
import sys

# Add erh_core to path if not already present
erh_core_path = Path(__file__).parent
if str(erh_core_path) not in sys.path:
    sys.path.insert(0, str(erh_core_path))

__all__ = ["core", "analysis"]

