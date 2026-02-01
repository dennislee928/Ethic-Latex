"""
ERH-on-Security domain layer.

This package maps DevSecOps data (from GitLab and internal DB tables)
into ERH-style variables and metrics.
"""

from .code_complexity import calculate_code_complexity

__all__ = ["calculate_code_complexity"]
