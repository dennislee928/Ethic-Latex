"""
Ethical Riemann Hypothesis Simulation Framework

A computational framework for modeling moral judgment errors through
Riemann-inspired mathematical structures.
"""

__version__ = "0.1.0"
__author__ = "Ethical AI Research"

# Ensure erh_core is in the path
import sys
from pathlib import Path

erh_core_path = Path(__file__).parent.parent / "erh_core"
if erh_core_path.exists() and str(erh_core_path) not in sys.path:
    sys.path.insert(0, str(erh_core_path))

from . import core
from . import analysis
from . import visualization

__all__ = ["core", "analysis", "visualization"]
