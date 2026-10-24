"""
OutbreakWatch Privacy & Anonymization Engine
Implements k-Anonymity cell suppression and epsilon-Differential Privacy via the Laplace Mechanism.
"""

import math
import random
from typing import List, Dict, Any, Tuple

class PrivacyEngine:
    def __init__(self, k_threshold: int = 5, default_epsilon: float = 1.0):
        """
        :param k_threshold: Minimum cell count required to display raw number without suppression.
        :param default_epsilon: Differential privacy parameter (lower = higher noise / greater privacy).
        """
        self.k_threshold = k_threshold
        self.epsilon = default_epsilon

    def apply_k_anonymity(self, count: int) -> Tuple[Any, bool]:
        """
        Suppresses granular counts below threshold k to protect against linkage attacks.
        Returns: (sanitized_count, is_suppressed)
        """
        if count < self.k_threshold and count > 0:
            return f"<{self.k_threshold}", True
        return count, False

    def sample_laplace_noise(self, sensitivity: float = 1.0, epsilon: float = None) -> float:
        """
        Samples noise from the zero-mean Laplace distribution Lap(0, scale)
        where scale = sensitivity / epsilon.
        """
        eps = epsilon if epsilon is not None else self.epsilon
        scale = sensitivity / max(0.01, eps)
        
        # Standard inverse transform sampling for Laplace distribution
        u = random.uniform(-0.5, 0.5)
        sign = 1.0 if u >= 0 else -1.0
        noise = -scale * sign * math.log(1.0 - 2.0 * abs(u))
        return noise

    def apply_differential_privacy(self, raw_count: int, epsilon: float = None) -> int:
        """
        Applies Laplace noise to an aggregate counting query.
        Clamps at 0 since negative counts are physically impossible in epidemiology.
        """
        noise = self.sample_laplace_noise(sensitivity=1.0, epsilon=epsilon)
        perturbed_count = int(round(raw_count + noise))
        return max(0, perturbed_count)

    def sanitize_phc_records(self, phc_list: List[Dict[str, Any]], enable_dp: bool = True) -> List[Dict[str, Any]]:
        """
        Applies k-anonymity suppression and optional differential privacy to granular PHC observations.
        """
        sanitized = []
        for item in phc_list:
            raw_val = item.get("raw_cases", 0)
            
            # 1. Apply k-anonymity
            k_val, suppressed = self.apply_k_anonymity(raw_val)
            
            # 2. Apply DP if enabled and not suppressed
            if enable_dp and not suppressed:
                final_val = self.apply_differential_privacy(raw_val)
            else:
                final_val = k_val
                
            sanitized.append({
                "phc_id": item.get("phc_id"),
                "phc_name": item.get("phc_name"),
                "lat": item.get("lat"),
                "lon": item.get("lon"),
                "display_cases": final_val,
                "is_k_suppressed": suppressed
            })
        return sanitized

    def get_privacy_metrics(self) -> Dict[str, Any]:
        """Returns the current privacy configuration and formal mathematical guarantees."""
        return {
            "k_anonymity_threshold": self.k_threshold,
            "epsilon_budget": self.epsilon,
            "mechanism": "Laplace Mechanism (Pure Epsilon-DP)",
            "theoretical_guarantee": f"e^{self.epsilon:.2f} <= {math.exp(self.epsilon):.2f} bounded likelihood ratio",
            "quasi_identifiers_removed": [
                "Citizen Full Name",
                "Aadhaar Number / ABHA ID",
                "Exact Street Address / House Number",
                "Phone Number / Contact Info",
                "Biometric / Genomic Indicators"
            ]
        }
