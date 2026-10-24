"""
Unit tests for CDC EARS-C2 and CUSUM Epidemiological Detection Algorithms
"""

import pytest
from app.engine.detector import AberrationDetector

def test_ears_c2_normal_baseline():
    detector = AberrationDetector()
    # 9 days of stable baseline (e.g., around 10 cases/day)
    stable_counts = [10, 11, 9, 10, 12, 10, 9, 11, 10]
    res = detector.calculate_ears_c2(stable_counts)
    
    assert "z_score" in res
    assert res["z_score"] < 2.0, "Expected normal baseline Z-score < 2.0"

def test_ears_c2_critical_spike():
    detector = AberrationDetector(ears_threshold_critical=3.0)
    # 8 days of baseline around 10, then sudden spike to 50
    spiking_counts = [10, 9, 11, 10, 10, 9, 11, 10, 50]
    res = detector.calculate_ears_c2(spiking_counts)
    
    assert res["z_score"] >= 3.0, f"Expected critical Z-score >= 3.0, got {res['z_score']}"

def test_cusum_gradual_drift():
    detector = AberrationDetector()
    # Gradual incremental drift over 15 days
    drift_counts = [10, 10, 11, 12, 14, 16, 18, 21, 24, 28, 32, 38, 44, 52]
    res = detector.calculate_cusum(drift_counts)
    
    assert "cusum_value" in res
    assert res["is_alarm"] is True, "CUSUM should trigger an alarm for persistent positive drift"

def test_insufficient_data():
    detector = AberrationDetector()
    short_counts = [10, 12, 14]
    res = detector.calculate_ears_c2(short_counts)
    assert res["alert_level"] == "INSUFFICIENT_DATA"
