"""
Pytest configuration: ensure project root and simulation are importable without sys.path hacks.

Run tests from project root: pytest tests/
"""

import sys
from pathlib import Path

# Add project root so simulation and erh packages are importable
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
