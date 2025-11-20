"""
Quick test to verify Streamlit app imports work correctly
Run: python test_streamlit_app.py
"""

import sys
import os

# Add simulation directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'simulation'))

try:
    # Test imports
    print("Testing imports...")
    
    from core.action_space import generate_world
    print("[OK] core.action_space")
    
    from core.judgement_system import BiasedJudge
    print("[OK] core.judgement_system")
    
    from core.ethical_primes import select_ethical_primes
    print("[OK] core.ethical_primes")
    
    from analysis.zeta_function import build_m_sequence
    print("[OK] analysis.zeta_function")
    
    import streamlit as st
    print("[OK] streamlit")
    
    print("\n[SUCCESS] All imports working! Streamlit app should run correctly.")
    print("\nTo test the app locally:")
    print("  cd simulation")
    print("  streamlit run app.py")
    
except ImportError as e:
    print(f"\n[ERROR] Import failed: {e}")
    print("\nMake sure you have installed all dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

