"""
Ethical Riemann Hypothesis (ERH) SDK
====================================

A Python package for simulating and analyzing ethical decision-making systems
through the lens of the Riemann Hypothesis.

Modules:
    core: Core simulation logic (Action Space, Judges, Primes).
    analysis: Statistical analysis tools (Zeta function, Error metrics).
    client: HTTP Client for remote API interaction.
"""

__version__ = "0.1.0"

# Ensure erh_core is in the path
import sys
from pathlib import Path

erh_core_path = Path(__file__).parent.parent / "erh_core"
if erh_core_path.exists() and str(erh_core_path) not in sys.path:
    sys.path.insert(0, str(erh_core_path))

# Lazy imports to avoid heavy dependencies on init if desired
# but for SDK usability, we often expose main classes here.

# These will resolve once we populate the submodules
# from erh.core.action_space import generate_world, Action
# from erh.core.judgement_system import BiasedJudge, NoisyJudge
# from erh.core.ethical_primes import select_ethical_primes
