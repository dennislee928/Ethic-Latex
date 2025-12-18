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

# Lazy imports to avoid heavy dependencies on init if desired
# but for SDK usability, we often expose main classes here.

# These will resolve once we populate the submodules
# from erh.core.action_space import generate_world, Action
# from erh.core.judgement_system import BiasedJudge, NoisyJudge
# from erh.core.ethical_primes import select_ethical_primes
