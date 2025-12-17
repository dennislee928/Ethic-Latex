"""
Quick verification script to check that all test files can be imported correctly.
"""

import sys
import os
from pathlib import Path

# Add simulation to path
simulation_dir = Path(__file__).parent.parent / "simulation"
sys.path.insert(0, str(simulation_dir))

print("=" * 70)
print("VERIFYING TEST FILES")
print("=" * 70)
print()

test_files = [
    "test_temporal_erh.py",
    "test_agent_framework.py",
    "test_social_network.py",
    "test_meta_monitor.py",
    "test_hybrid_model.py",
    "test_psychohistory_integration.py"
]

all_ok = True
for test_file in test_files:
    test_path = Path(__file__).parent / test_file
    if test_path.exists():
        try:
            # Try to import the test module
            spec = __import__(test_file.replace('.py', ''), fromlist=[''])
            print(f"[OK] {test_file:40s} - Import successful")
        except Exception as e:
            print(f"[FAIL] {test_file:40s} - Import failed: {e}")
            all_ok = False
    else:
        print(f"[MISSING] {test_file:40s} - File not found")
        all_ok = False

print()
print("=" * 70)
if all_ok:
    print("SUCCESS: All test files can be imported!")
else:
    print("WARNING: Some test files have issues.")
print("=" * 70)

# Also check if pytest is available
print()
print("Checking pytest availability...")
try:
    import pytest
    print(f"[OK] pytest version: {pytest.__version__}")
except ImportError:
    print("[WARNING] pytest not installed. Install with: pip install pytest")
    all_ok = False

sys.exit(0 if all_ok else 1)


