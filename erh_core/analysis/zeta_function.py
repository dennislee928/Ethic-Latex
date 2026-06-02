"""
Ethical Zeta Function Module

This module implements the "ethical zeta function" - a generating function
inspired by the Riemann zeta function that encodes the distribution of ethical primes.

It also provides spectrum analysis via FFT to detect periodic patterns in judgment errors.

PyJulia bridge
--------------
When PyJulia is available, calls to `ethical_zeta` are forwarded to the
compiled Julia implementation in ERH.ZetaFunction for improved performance.
All other functions fall back to the pure-Python implementations in
`_zeta_pure.py`, which is always imported as the base layer.
"""

# ---------------------------------------------------------------------------
# Try to load the Julia bridge.
# ---------------------------------------------------------------------------
try:
    from julia.api import Julia
    _jl = Julia(compiled_modules=False)
    from julia import Main as _jlmain
    import os as _os
    _jlmain.eval(
        'push!(LOAD_PATH, "%s")'
        % _os.path.join(_os.path.dirname(__file__), "../../julia")
    )
    _jlmain.eval("using ERH")
    _JULIA_AVAILABLE = True
except Exception:
    _JULIA_AVAILABLE = False

# ---------------------------------------------------------------------------
# Always import the pure-Python implementations as the base layer.
# ---------------------------------------------------------------------------
from ._zeta_pure import *  # noqa: F401, F403  (re-export everything)
from ._zeta_pure import (  # explicit imports for IDE/type-checker clarity
    build_m_sequence,
    ethical_zeta_product,
    ethical_zeta_sum,
    find_approximate_zeros,
    compute_spectrum,
    compute_power_spectrum,
    analyze_spectrum_peaks,
    compute_zeta_grid,
    detect_periodic_bias,
)

# ---------------------------------------------------------------------------
# Override with Julia implementations when available.
# ---------------------------------------------------------------------------
if _JULIA_AVAILABLE:
    def ethical_zeta(s, primes):
        """
        Compute the ethical zeta function using the Julia implementation.

        Parameters
        ----------
        s : complex
            Complex argument.
        primes : iterable
            Ethical primes (objects with a `.c` attribute).

        Returns
        -------
        complex
            Value of ζ_E(s) computed by ERH.ZetaFunction in Julia.
        """
        return _jlmain.eval("ERH.ZetaFunction.ethical_zeta_product")(
            s, list(primes)
        )
