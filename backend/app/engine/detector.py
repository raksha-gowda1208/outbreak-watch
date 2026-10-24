"""
OutbreakWatch Detection Engine
Implements CDC EARS (Early Aberration Reporting System) and CUSUM algorithms for syndromic surveillance.
"""

import math
from typing import List, Dict, Any, Optional

class AberrationDetector:
    def __init__(self, ears_threshold_elevated: float = 2.0, ears_threshold_critical: float = 3.0):
        """
        :param ears_threshold_elevated: Z-score cutoff for Yellow alert (default 2.0 sigma)
        :param ears_threshold_critical: Z-score cutoff for Red alert (default 3.0 sigma)
        """
        self.elevated_threshold = ears_threshold_elevated
        self.critical_threshold = ears_threshold_critical

    @staticmethod
    def calculate_ears_c2(counts: List[int]) -> Dict[str, Any]:
        """
        Calculates CDC EARS-C2 aberration index.
        Requires at least 9 historical days:
        - Baseline window: 7 days with 2-day buffer (t-9 to t-2)
        - Current count: t
        """
        if len(counts) < 9:
            return {
                "z_score": 0.0,
                "baseline_mean": 0.0,
                "baseline_std": 0.0,
                "alert_level": "INSUFFICIENT_DATA"
            }

        current_count = counts[-1]
        # Baseline is 7 days prior to t-2 (i.e. counts[-9:-2])
        baseline_window = counts[-9:-2]
        
        mean_base = sum(baseline_window) / len(baseline_window)
        variance = sum((x - mean_base) ** 2 for x in baseline_window) / max(1, len(baseline_window) - 1)
        std_base = math.sqrt(variance)
        
        # Floor standard deviation to prevent hyper-sensitivity at near-zero counts
        effective_std = max(1.0, std_base)
        z_score = (current_count - mean_base) / effective_std
        
        return {
            "z_score": round(z_score, 2),
            "baseline_mean": round(mean_base, 2),
            "baseline_std": round(effective_std, 2),
            "current_count": current_count
        }

    @staticmethod
    def calculate_cusum(counts: List[int], k: float = 0.5, h: float = 4.0) -> Dict[str, Any]:
        """
        Calculates tabular Cumulative Sum (CUSUM) for detecting insidious gradual shifts.
        k: slack value (allowable shift, usually 0.5 sigma)
        h: decision interval threshold (usually 4 to 5 sigma)
        """
        if len(counts) < 10:
            return {"cusum_value": 0.0, "is_alarm": False}
            
        baseline = counts[:-1]
        mean = sum(baseline) / len(baseline)
        std = math.sqrt(sum((x - mean) ** 2 for x in baseline) / max(1, len(baseline) - 1))
        effective_std = max(1.0, std)
        
        s = 0.0
        for x in counts[-7:]: # evaluate over last 7 days
            norm_x = (x - mean) / effective_std
            s = max(0.0, s + norm_x - k)
            
        return {
            "cusum_value": round(s, 2),
            "threshold": h,
            "is_alarm": s >= h
        }

    def evaluate_time_series(self, historical_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes a chronological list of daily records for a specific district & syndrome.
        Returns anomaly diagnosis, alert level, and actionable recommendation.
        """
        if not historical_records:
            return {"status": "NO_RECORDS"}

        # Extract daily counts
        phc_counts = [r["phc_consultations"] for r in historical_records]
        otc_counts = [r["pharmacy_otc_sales"] for r in historical_records]
        
        ears_res = self.calculate_ears_c2(phc_counts)
        otc_ears = self.calculate_ears_c2(otc_counts)
        cusum_res = self.calculate_cusum(phc_counts)
        
        z = ears_res.get("z_score", 0.0)
        otc_z = otc_ears.get("z_score", 0.0)
        
        # Determine alert classification
        if z >= self.critical_threshold or (z >= 2.2 and otc_z >= 2.5):
            alert_level = "CRITICAL"
            color = "#EF4444" # Red
            recommendation = (
                "IMMEDIATE ACTION REQUIRED: Dispatch Rapid Response Team (RRT) for spot epidemiological survey. "
                "Enforce clinical water/food sample testing and notify District Surveillance Officer (DSO)."
            )
        elif z >= self.elevated_threshold or cusum_res["is_alarm"] or otc_z >= 2.5:
            alert_level = "ELEVATED"
            color = "#F59E0B" # Amber
            recommendation = (
                "ADVISORY: Early syndromic or OTC surge detected. Initiate active case finding via ASHA workers "
                "and cross-check laboratory logbooks for preliminary culture requests."
            )
        else:
            alert_level = "NORMAL"
            color = "#10B981" # Green
            recommendation = "ROUTINE MONITORING: Syndromic distribution within expected baseline variance."

        latest_record = historical_records[-1]
        
        return {
            "district_id": latest_record["district_id"],
            "district_name": latest_record["district_name"],
            "syndrome_id": latest_record["syndrome_id"],
            "syndrome_name": latest_record["syndrome_name"],
            "date": latest_record["date"],
            "alert_level": alert_level,
            "color_code": color,
            "ears_c2": ears_res,
            "otc_signal": {
                "current_otc_units": latest_record["pharmacy_otc_sales"],
                "otc_z_score": otc_z,
                "lead_indicator_detected": otc_z >= 2.5
            },
            "cusum": cusum_res,
            "recommendation": recommendation
        }
