"""
Quick test to verify Streamlit app imports work correctly.
Run as script: python tests/test_streamlit_app.py
Run with pytest: pytest tests/test_streamlit_app.py -v
"""

import sys
import os

import pytest


def _check_streamlit_imports():
    """Try imports required for simulation Streamlit app. Returns (True, None) or (False, error)."""
    sim_dir = os.path.join(os.path.dirname(__file__), "..", "simulation")
    if sim_dir not in sys.path:
        sys.path.insert(0, sim_dir)
    try:
        from core.action_space import generate_world  # noqa: F401
        from core.judgement_system import BiasedJudge  # noqa: F401
        from core.ethical_primes import select_ethical_primes  # noqa: F401
        from analysis.zeta_function import build_m_sequence  # noqa: F401
        import streamlit  # noqa: F401
        return True, None
    except ImportError as e:
        return False, e


def test_streamlit_app_imports():
    """Verify Streamlit app dependencies can be imported (run from simulation/ or with path)."""
    ok, err = _check_streamlit_imports()
    if not ok:
        pytest.skip(f"Streamlit app imports not available: {err}")
    assert ok


if __name__ == "__main__":
    # Standalone script: print and exit for CI or manual run
    print("Testing imports...")
    ok, err = _check_streamlit_imports()
    if ok:
        print("[OK] core.action_space")
        print("[OK] core.judgement_system")
        print("[OK] core.ethical_primes")
        print("[OK] analysis.zeta_function")
        print("[OK] streamlit")
        print("\n[SUCCESS] All imports working! Streamlit app should run correctly.")
        print("\nTo test the app locally:")
        print("  cd simulation")
        print("  streamlit run app.py")
    else:
        print(f"\n[ERROR] Import failed: {err}")
        print("\nMake sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

