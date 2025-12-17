"""
Meta-Monitor Module

This module implements the "Second Foundation" meta-layer monitoring system
that continuously tracks ERH error evolution and automatically adjusts parameters
when deviations are detected, analogous to Asimov's Second Foundation that secretly
guides civilization.

Key features:
- Continuous monitoring of E(x,t) trajectories
- Detection of ERH violations
- Automatic parameter adjustment
- Correction mechanism triggers
"""

import numpy as np
from typing import List, Dict, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CorrectionAction(Enum):
    """Types of correction actions."""
    ADJUST_PARAMETERS = "adjust_parameters"
    INTRODUCE_HUMAN_OVERSIGHT = "introduce_human_oversight"
    RESTRICT_ALGORITHM = "restrict_algorithm"
    ALERT = "alert"
    NO_ACTION = "no_action"


@dataclass
class ERHParameters:
    """ERH parameters that can be adjusted."""
    C: float = 1.0  # ERH constant
    epsilon: float = 0.1  # ERH epsilon
    baseline_type: str = 'prime_theorem'
    baseline_params: Dict = field(default_factory=dict)
    
    def copy(self):
        """Create a copy of parameters."""
        return ERHParameters(
            C=self.C,
            epsilon=self.epsilon,
            baseline_type=self.baseline_type,
            baseline_params=self.baseline_params.copy()
        )


@dataclass
class ViolationEvent:
    """Record of an ERH violation event."""
    time: int
    complexity: int
    error_magnitude: float
    erh_bound: float
    violation_ratio: float
    severity: str
    corrected: bool = False
    correction_action: Optional[CorrectionAction] = None


class MetaMonitor:
    """
    Meta-layer monitor for ERH error evolution.
    
    Continuously monitors E(x,t) and automatically adjusts parameters
    when violations are detected, similar to the Second Foundation's
    secret guidance of civilization.
    
    Attributes
    ----------
    erh_params : ERHParameters
        Current ERH parameters
    violation_history : List[ViolationEvent]
        History of detected violations
    correction_history : List[Dict]
        History of corrections applied
    monitoring_active : bool
        Whether monitoring is active
    """
    
    def __init__(
        self,
        initial_params: Optional[ERHParameters] = None,
        violation_threshold: float = 1.5,
        correction_enabled: bool = True
    ):
        """
        Initialize meta-monitor.
        
        Parameters
        ----------
        initial_params : Optional[ERHParameters], default=None
            Initial ERH parameters. If None, uses defaults.
        violation_threshold : float, default=1.5
            Threshold multiplier for violation detection (1.5 = 50% above bound)
        correction_enabled : bool, default=True
            Whether automatic correction is enabled
        """
        self.erh_params = initial_params if initial_params else ERHParameters()
        self.violation_threshold = violation_threshold
        self.correction_enabled = correction_enabled
        self.violation_history = []
        self.correction_history = []
        self.monitoring_active = True
        self.target_exponent = 0.5  # Target for ERH exponent
    
    def monitor(
        self,
        E_xt: np.ndarray,
        time_step: int,
        X_max: int = 100
    ) -> Dict:
        """
        Monitor error evolution and detect violations.
        
        Parameters
        ----------
        E_xt : np.ndarray
            2D error array of shape (time_steps, X_max)
        time_step : int
            Current time step to analyze
        X_max : int, default=100
            Maximum complexity
            
        Returns
        -------
        Dict
            Monitoring results:
            - 'violations_detected': List of violations
            - 'erh_satisfied': Whether ERH is satisfied
            - 'correction_applied': Whether correction was applied
            - 'new_params': Updated parameters (if adjusted)
        """
        if not self.monitoring_active:
            return {'violations_detected': [], 'erh_satisfied': True, 'correction_applied': False}
        
        violations = []
        x_values = np.arange(1, X_max + 1)
        
        # Check each complexity level
        for x_idx, x in enumerate(x_values):
            if time_step < E_xt.shape[0]:
                error_mag = abs(E_xt[time_step, x_idx])
                
                # Compute ERH bound
                erh_bound = self.erh_params.C * (x ** (0.5 + self.erh_params.epsilon))
                threshold = erh_bound * self.violation_threshold
                
                if error_mag > threshold:
                    violation_ratio = error_mag / erh_bound
                    
                    # Determine severity
                    if violation_ratio > 3.0:
                        severity = 'critical'
                    elif violation_ratio > 2.0:
                        severity = 'high'
                    elif violation_ratio > 1.5:
                        severity = 'medium'
                    else:
                        severity = 'low'
                    
                    violation = ViolationEvent(
                        time=time_step,
                        complexity=x,
                        error_magnitude=error_mag,
                        erh_bound=erh_bound,
                        violation_ratio=violation_ratio,
                        severity=severity
                    )
                    violations.append(violation)
                    self.violation_history.append(violation)
        
        # Apply correction if violations detected
        correction_applied = False
        new_params = None
        
        if len(violations) > 0 and self.correction_enabled:
            correction_result = self._apply_correction(violations, E_xt, time_step, X_max)
            correction_applied = correction_result['applied']
            new_params = correction_result.get('new_params')
            
            # Mark violations as corrected
            for violation in violations:
                violation.corrected = correction_applied
                violation.correction_action = correction_result.get('action')
        
        return {
            'violations_detected': violations,
            'erh_satisfied': len(violations) == 0,
            'correction_applied': correction_applied,
            'new_params': new_params
        }
    
    def _apply_correction(
        self,
        violations: List[ViolationEvent],
        E_xt: np.ndarray,
        time_step: int,
        X_max: int
    ) -> Dict:
        """
        Apply correction mechanism based on violations.
        
        Parameters
        ----------
        violations : List[ViolationEvent]
            Detected violations
        E_xt : np.ndarray
            Error array
        time_step : int
            Current time step
        X_max : int
            Maximum complexity
            
        Returns
        -------
        Dict
            Correction result:
            - 'applied': Whether correction was applied
            - 'action': Type of correction action
            - 'new_params': Updated parameters
        """
        if len(violations) == 0:
            return {'applied': False, 'action': CorrectionAction.NO_ACTION}
        
        # Determine severity
        max_severity = max(v.severity for v in violations)
        max_violation_ratio = max(v.violation_ratio for v in violations)
        
        # Choose correction action based on severity
        if max_severity == 'critical' or max_violation_ratio > 3.0:
            action = CorrectionAction.RESTRICT_ALGORITHM
        elif max_severity == 'high' or max_violation_ratio > 2.0:
            action = CorrectionAction.INTRODUCE_HUMAN_OVERSIGHT
        elif max_severity == 'medium':
            action = CorrectionAction.ADJUST_PARAMETERS
        else:
            action = CorrectionAction.ALERT
        
        # Apply parameter adjustment
        new_params = None
        if action == CorrectionAction.ADJUST_PARAMETERS:
            new_params = self._adjust_parameters(E_xt, time_step, X_max)
            self.erh_params = new_params
        
        # Record correction
        correction_record = {
            'time': time_step,
            'action': action,
            'violations_count': len(violations),
            'max_severity': max_severity,
            'new_params': new_params.copy() if new_params else None
        }
        self.correction_history.append(correction_record)
        
        return {
            'applied': True,
            'action': action,
            'new_params': new_params
        }
    
    def _adjust_parameters(
        self,
        E_xt: np.ndarray,
        time_step: int,
        X_max: int
    ) -> ERHParameters:
        """
        Adjust ERH parameters to better fit observed errors.
        
        Parameters
        ----------
        E_xt : np.ndarray
            Error array
        time_step : int
            Current time step
        X_max : int
            Maximum complexity
            
        Returns
        -------
        ERHParameters
            Adjusted parameters
        """
        # Use adaptive parameter adjustment
        new_params = self.erh_params.copy()
        
        # Analyze recent error evolution
        if time_step > 0:
            recent_errors = E_xt[max(0, time_step - 5):time_step + 1, :]
            x_values = np.arange(1, X_max + 1)
            
            # Estimate current exponent
            # Fit |E(x)| = C * x^alpha for recent data
            error_magnitudes = np.abs(recent_errors)
            mean_errors = np.mean(error_magnitudes, axis=0)
            
            # Filter out zeros
            valid_mask = mean_errors > 0
            if np.sum(valid_mask) > 5:
                x_valid = x_values[valid_mask]
                E_valid = mean_errors[valid_mask]
                
                # Log-log regression
                log_x = np.log(x_valid)
                log_E = np.log(E_valid)
                
                coeffs = np.polyfit(log_x, log_E, 1)
                estimated_alpha = coeffs[0]
                estimated_C = np.exp(coeffs[1])
                
                # Adjust parameters toward target
                target_alpha = self.target_exponent
                alpha_diff = estimated_alpha - target_alpha
                
                # Adaptive adjustment: move toward target
                adjustment_rate = 0.1
                new_params.epsilon = max(0.01, min(0.5, 
                    self.erh_params.epsilon - adjustment_rate * alpha_diff))
                
                # Adjust C to better fit
                if estimated_C > 0:
                    new_params.C = 0.9 * self.erh_params.C + 0.1 * estimated_C
        
        return new_params
    
    def adaptive_erh_parameters(
        self,
        E_xt_history: List[np.ndarray],
        target_exponent: float = 0.5
    ) -> ERHParameters:
        """
        Adaptively adjust ERH parameters based on historical error evolution.
        
        Parameters
        ----------
        E_xt_history : List[np.ndarray]
            History of error arrays
        target_exponent : float, default=0.5
            Target exponent for ERH
            
        Returns
        -------
        ERHParameters
            Optimized parameters
        """
        self.target_exponent = target_exponent
        
        if len(E_xt_history) == 0:
            return self.erh_params
        
        # Normalize all errors to 2D arrays (time_steps, X_max)
        normalized_history = []
        for E_xt in E_xt_history:
            E_xt = np.asarray(E_xt)
            if E_xt.ndim == 1:
                # Reshape 1D array to (1, X_max)
                E_xt = E_xt.reshape(1, -1)
            normalized_history.append(E_xt)
        
        # Aggregate all historical errors
        all_errors = np.concatenate(normalized_history, axis=0)
        time_steps_total = all_errors.shape[0]
        X_max = all_errors.shape[1]
        x_values = np.arange(1, X_max + 1)
        
        # Compute mean error magnitude over time
        mean_errors = np.mean(np.abs(all_errors), axis=0)
        
        # Fit power law: |E(x)| = C * x^alpha
        valid_mask = mean_errors > 0
        if np.sum(valid_mask) > 5:
            x_valid = x_values[valid_mask]
            E_valid = mean_errors[valid_mask]
            
            log_x = np.log(x_valid)
            log_E = np.log(E_valid)
            
            coeffs = np.polyfit(log_x, log_E, 1)
            estimated_alpha = coeffs[0]
            estimated_C = np.exp(coeffs[1])
            
            # Set parameters
            new_params = ERHParameters()
            new_params.C = estimated_C
            new_params.epsilon = max(0.01, estimated_alpha - 0.5)
            new_params.baseline_type = self.erh_params.baseline_type
            new_params.baseline_params = self.erh_params.baseline_params.copy()
            
            self.erh_params = new_params
            return new_params
        
        return self.erh_params
    
    def get_monitoring_summary(self) -> Dict:
        """
        Get summary of monitoring activity.
        
        Returns
        -------
        Dict
            Summary statistics
        """
        if len(self.violation_history) == 0:
            return {
                'total_violations': 0,
                'corrections_applied': len(self.correction_history),
                'current_params': {
                    'C': self.erh_params.C,
                    'epsilon': self.erh_params.epsilon
                }
            }
        
        severity_counts = {}
        for violation in self.violation_history:
            severity = violation.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_violations': len(self.violation_history),
            'severity_breakdown': severity_counts,
            'corrections_applied': len(self.correction_history),
            'correction_rate': len(self.correction_history) / len(self.violation_history) if len(self.violation_history) > 0 else 0.0,
            'current_params': {
                'C': self.erh_params.C,
                'epsilon': self.erh_params.epsilon,
                'baseline_type': self.erh_params.baseline_type
            }
        }
    
    def reset(self):
        """Reset monitor state (clear history)."""
        self.violation_history = []
        self.correction_history = []
    
    def enable_monitoring(self):
        """Enable monitoring."""
        self.monitoring_active = True
    
    def disable_monitoring(self):
        """Disable monitoring."""
        self.monitoring_active = False
