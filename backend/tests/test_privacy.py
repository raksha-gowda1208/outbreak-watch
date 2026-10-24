"""
Unit tests for k-Anonymity and Laplace Differential Privacy Engine
"""

import pytest
from app.privacy.engine import PrivacyEngine

def test_k_anonymity_suppression():
    engine = PrivacyEngine(k_threshold=5)
    
    # Values below k should be suppressed
    val, is_suppressed = engine.apply_k_anonymity(3)
    assert is_suppressed is True
    assert val == "<5"
    
    # Values at or above k should pass unchanged
    val_ok, is_suppressed_ok = engine.apply_k_anonymity(7)
    assert is_suppressed_ok is False
    assert val_ok == 7

def test_differential_privacy_non_negative():
    engine = PrivacyEngine(default_epsilon=1.0)
    for _ in range(50):
        perturbed = engine.apply_differential_privacy(raw_count=0)
        assert perturbed >= 0, "Perturbed count must never be negative in epidemiological surveillance"

def test_phc_records_sanitization():
    engine = PrivacyEngine(k_threshold=5, default_epsilon=1.0)
    sample_phcs = [
        {"phc_id": "PHC-1", "phc_name": "Rural Post A", "lat": 18.5, "lon": 73.8, "raw_cases": 2},
        {"phc_id": "PHC-2", "phc_name": "Urban Post B", "lat": 18.6, "lon": 73.9, "raw_cases": 25}
    ]
    
    sanitized = engine.sanitize_phc_records(sample_phcs, enable_dp=True)
    assert len(sanitized) == 2
    assert sanitized[0]["is_k_suppressed"] is True
    assert sanitized[0]["display_cases"] == "<5"
    assert sanitized[1]["is_k_suppressed"] is False
