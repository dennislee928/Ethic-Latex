"""
Moral Interference Simulation (§1.4).

Simulates cognitive dissonance / conflicting societal narratives through
quantum superposition.  An agent is represented as a qubit whose |0> axis
is the "pro" narrative and |1> axis is the "con" narrative.  Conflicting
narratives contribute amplitudes with phases; the interference pattern of
these amplitudes gives the probabilistic measurement outcome (support
probability) after any number of narratives.

The core primitive is an array of NARRATIVES = (amplitude, phase) tuples
applied through a Mach-Zehnder-like chain that generalises the classical
two-slit experiment to an arbitrary number of ethical stances.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import numpy as np

__all__ = [
    "Narrative",
    "interference_amplitude",
    "measurement_probability",
    "societal_measurement",
    "two_slit_morality",
    "moral_interference_pattern",
]


@dataclass(frozen=True)
class Narrative:
    """A single moral narrative: magnitude (weight) and phase (ethical valence)."""
    amplitude: float     # non-negative magnitude
    phase: float         # radians; 0 = pro, pi = con


def interference_amplitude(narratives: Sequence[Narrative]) -> complex:
    """Sum the complex amplitudes of a bundle of narratives."""
    return complex(sum(n.amplitude * np.exp(1j * n.phase) for n in narratives))


def measurement_probability(narratives: Sequence[Narrative]) -> float:
    """|sum_k a_k e^{i phi_k}|^2 / sum_k a_k^2 (normalised support probability)."""
    if not narratives:
        return 0.0
    amp = interference_amplitude(narratives)
    coherent = float(abs(amp) ** 2)
    incoherent = float(sum(n.amplitude ** 2 for n in narratives))
    if incoherent == 0:
        return 0.0
    return coherent / (coherent + incoherent) if (coherent + incoherent) > 0 else 0.0


def societal_measurement(
    pro_narratives: Sequence[Narrative],
    con_narratives: Sequence[Narrative],
) -> Tuple[float, float]:
    """
    Two-channel measurement: returns (P_pro, P_con) after interference.

    Normalises so that P_pro + P_con = 1.
    """
    a_pro = interference_amplitude(pro_narratives)
    a_con = interference_amplitude(con_narratives)
    p_pro_raw = float(abs(a_pro) ** 2)
    p_con_raw = float(abs(a_con) ** 2)
    total = p_pro_raw + p_con_raw
    if total <= 0.0:
        return 0.5, 0.5
    return p_pro_raw / total, p_con_raw / total


def two_slit_morality(
    phase_difference: float,
    amp_a: float = 1.0,
    amp_b: float = 1.0,
) -> float:
    """
    Classical two-slit interference, reused for two competing narratives.
    Returns the combined amplitude squared (support intensity) at a given
    relative phase.
    """
    a = amp_a
    b = amp_b * np.exp(1j * phase_difference)
    return float(abs(a + b) ** 2)


def moral_interference_pattern(
    amp_a: float = 1.0,
    amp_b: float = 1.0,
    n_points: int = 200,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Sweep phase difference from 0 to 2pi and return (phases, intensity)
    showing a classic cosine fringe - the moral "screen" for a referendum
    between two competing ethics.
    """
    phases = np.linspace(0.0, 2.0 * np.pi, n_points)
    intensity = np.array([two_slit_morality(p, amp_a, amp_b) for p in phases])
    return phases, intensity
