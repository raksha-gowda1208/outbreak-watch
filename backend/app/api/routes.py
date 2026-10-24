"""
REST API Routes for OutbreakWatch
"""

import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.models.schemas import OutbreakInjectionRequest, PrivacyConfigRequest
from app.privacy.engine import PrivacyEngine
from app.engine.detector import AberrationDetector

router = APIRouter()

# Global state initialized from seed data
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "../../../data-pipeline/seed_data.json")

# Initialize engines
privacy_engine = PrivacyEngine(k_threshold=5, default_epsilon=1.0)
detector_engine = AberrationDetector(ears_threshold_elevated=2.0, ears_threshold_critical=3.0)

def load_data():
    if os.path.exists(DATA_FILE_PATH):
        with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    # Fallback to importing generator if seed_data.json isn't present
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-pipeline")))
    import generator
    return generator.generate_synthetic_dataset(days_back=30, inject_active_outbreak=True)

DATA_STORE = load_data()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "OutbreakWatch Surveillance Engine",
        "timestamp": datetime.now().isoformat(),
        "total_records": len(DATA_STORE["records"])
    }

@router.get("/districts")
def get_districts():
    return DATA_STORE["districts"]

@router.get("/syndromes")
def get_syndromes():
    return DATA_STORE["syndromes"]

@router.get("/trends")
def get_trends(
    district_name: Optional[str] = Query("Pune", description="District to query"),
    syndrome_id: Optional[str] = Query("SYN-ADD", description="Syndrome ID"),
    apply_dp: bool = Query(True, description="Whether to apply Differential Privacy noise")
):
    """
    Returns the time-series trajectory of a specific syndrome in a district,
    including baseline comparisons, OTC signals, and privacy-preserved counts.
    """
    matching_records = [
        r for r in DATA_STORE["records"]
        if r["district_name"].lower() == district_name.lower() and r["syndrome_id"] == syndrome_id
    ]
    
    if not matching_records:
        raise HTTPException(status_code=404, detail="No records matching criteria found")
        
    # Sort chronologically
    matching_records = sorted(matching_records, key=lambda x: x["date"])
    
    # Run aberration evaluation
    analysis = detector_engine.evaluate_time_series(matching_records)
    
    # Process records for display with privacy protections
    trend_series = []
    for r in matching_records:
        raw_phc = r["phc_consultations"]
        dp_phc = privacy_engine.apply_differential_privacy(raw_phc) if apply_dp else raw_phc
        
        # Sanitize granular PHC allocations
        sanitized_phcs = privacy_engine.sanitize_phc_records(r.get("phc_breakdown", []), enable_dp=apply_dp)
        
        trend_series.append({
            "date": r["date"],
            "raw_phc_consultations": raw_phc,
            "display_phc_consultations": dp_phc,
            "pharmacy_otc_sales": r["pharmacy_otc_sales"],
            "tele_triage_calls": r["tele_triage_calls"],
            "phc_breakdown": sanitized_phcs,
            "is_outbreak_period": r.get("is_simulated_outbreak", False)
        })
        
    return {
        "district_name": district_name,
        "syndrome_id": syndrome_id,
        "syndrome_name": next((s["name"] for s in DATA_STORE["syndromes"] if s["id"] == syndrome_id), syndrome_id),
        "analysis": analysis,
        "series": trend_series
    }

@router.get("/anomalies")
def get_active_anomalies():
    """
    Evaluates every district and syndrome across the latest window
    and flags all ELEVATED and CRITICAL anomalies.
    """
    anomalies = []
    for district in DATA_STORE["districts"]:
        d_name = district["name"]
        for syn in DATA_STORE["syndromes"]:
            s_id = syn["id"]
            records = [
                r for r in DATA_STORE["records"]
                if r["district_name"] == d_name and r["syndrome_id"] == s_id
            ]
            if len(records) >= 9:
                records = sorted(records, key=lambda x: x["date"])
                eval_res = detector_engine.evaluate_time_series(records)
                if eval_res["alert_level"] in ("ELEVATED", "CRITICAL"):
                    anomalies.append(eval_res)
                    
    # Sort with CRITICAL on top
    anomalies.sort(key=lambda x: 0 if x["alert_level"] == "CRITICAL" else 1)
    return {
        "total_active_anomalies": len(anomalies),
        "critical_count": sum(1 for a in anomalies if a["alert_level"] == "CRITICAL"),
        "elevated_count": sum(1 for a in anomalies if a["alert_level"] == "ELEVATED"),
        "anomalies": anomalies
    }

@router.get("/map/hotspots")
def get_map_hotspots(syndrome_id: Optional[str] = Query(None)):
    """
    Returns geographical coordinates, severity flags, and cluster intensities
    for interactive map rendering.
    """
    hotspots = []
    
    for district in DATA_STORE["districts"]:
        d_name = district["name"]
        
        # Determine highest severity for this district
        highest_alert = "NORMAL"
        highest_z = 0.0
        active_syndromes = []
        
        syndromes_to_check = [s for s in DATA_STORE["syndromes"] if syndrome_id is None or s["id"] == syndrome_id]
        
        for syn in syndromes_to_check:
            records = [
                r for r in DATA_STORE["records"]
                if r["district_name"] == d_name and r["syndrome_id"] == syn["id"]
            ]
            if len(records) >= 9:
                records = sorted(records, key=lambda x: x["date"])
                eval_res = detector_engine.evaluate_time_series(records)
                z = eval_res["ears_c2"].get("z_score", 0.0)
                if z > highest_z:
                    highest_z = z
                    
                if eval_res["alert_level"] == "CRITICAL":
                    highest_alert = "CRITICAL"
                    active_syndromes.append(f"{syn['name']} (Z={z})")
                elif eval_res["alert_level"] == "ELEVATED" and highest_alert != "CRITICAL":
                    highest_alert = "ELEVATED"
                    active_syndromes.append(f"{syn['name']} (Z={z})")
                    
        color = "#10B981" # Green
        radius = 16
        if highest_alert == "CRITICAL":
            color = "#EF4444" # Red
            radius = 32
        elif highest_alert == "ELEVATED":
            color = "#F59E0B" # Amber
            radius = 24
            
        hotspots.append({
            "district_id": district["id"],
            "district_name": district["name"],
            "lat": district["lat"],
            "lon": district["lon"],
            "population": district["population"],
            "alert_level": highest_alert,
            "color": color,
            "radius": radius,
            "max_z_score": highest_z,
            "flagged_syndromes": active_syndromes,
            "phcs_count": len(district["phcs"])
        })
        
    return hotspots

@router.post("/simulate/inject")
def inject_outbreak_simulation(payload: OutbreakInjectionRequest):
    """
    Live Chaos Outbreak Injector:
    Alters recent syndromic counts in memory to simulate a sudden localized outbreak.
    Evaluators can execute this to witness real-time alerting.
    """
    target_district = payload.district_name.strip()
    target_syndrome = payload.syndrome_id.strip()
    multiplier = 1.0 + (payload.spike_percentage / 100.0)
    
    modified_count = 0
    records = DATA_STORE["records"]
    
    # Sort all dates to find the latest N days
    all_dates = sorted(list(set(r["date"] for r in records)))
    target_dates = all_dates[-payload.days_duration:]
    
    for r in records:
        if r["district_name"].lower() == target_district.lower() and r["syndrome_id"] == target_syndrome:
            if r["date"] in target_dates:
                r["phc_consultations"] = int(round(r["phc_consultations"] * multiplier))
                r["pharmacy_otc_sales"] = int(round(r["pharmacy_otc_sales"] * (multiplier + 0.3)))
                r["tele_triage_calls"] = int(round(r["tele_triage_calls"] * (multiplier + 0.5)))
                r["is_simulated_outbreak"] = True
                
                for phc in r.get("phc_breakdown", []):
                    phc["raw_cases"] = int(round(phc["raw_cases"] * multiplier))
                    
                modified_count += 1
                
    if modified_count == 0:
        raise HTTPException(status_code=404, detail="Matching district or syndrome not found for injection")
        
    return {
        "status": "OUTBREAK_INJECTED",
        "district": target_district,
        "syndrome_id": target_syndrome,
        "spike_applied": f"+{payload.spike_percentage}%",
        "records_modified": modified_count,
        "affected_dates": target_dates,
        "message": "Outbreak anomaly successfully induced. Dashboard maps and anomaly feeds updated in real-time."
    }

@router.get("/privacy/metrics")
def get_privacy_metrics():
    """Returns mathematical privacy parameters and compliance guarantees."""
    return privacy_engine.get_privacy_metrics()

@router.post("/privacy/config")
def update_privacy_config(payload: PrivacyConfigRequest):
    """Dynamically adjusts the privacy budget (epsilon) and k-anonymity threshold."""
    privacy_engine.epsilon = payload.epsilon
    privacy_engine.k_threshold = payload.k_threshold
    return {
        "status": "UPDATED",
        "new_epsilon": privacy_engine.epsilon,
        "new_k_threshold": privacy_engine.k_threshold
    }
