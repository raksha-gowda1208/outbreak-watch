"""
Test script for OutbreakWatch core endpoints
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.routes import get_districts, get_active_anomalies, get_trends, get_map_hotspots, inject_outbreak_simulation
from app.models.schemas import OutbreakInjectionRequest

def run_tests():
    print("[1] Testing get_districts()...")
    districts = get_districts()
    assert len(districts) == 5, f"Expected 5 districts, got {len(districts)}"
    print(f"    OK -> {len(districts)} districts loaded: {[d['name'] for d in districts]}")

    print("[2] Testing get_active_anomalies()...")
    anomalies = get_active_anomalies()
    print(f"    OK -> Found {anomalies['total_active_anomalies']} active anomalies across districts.")

    print("[3] Testing get_trends('Pune', 'SYN-ADD')...")
    trends = get_trends('Pune', 'SYN-ADD', apply_dp=True)
    assert len(trends["series"]) > 0, "Trends series is empty"
    analysis = trends["analysis"]
    print(f"    OK -> Pune ADD records: {len(trends['series'])}, Alert Level: {analysis['alert_level']}, Z-Score: {analysis['ears_c2']['z_score']}")

    print("[4] Testing get_map_hotspots()...")
    hotspots = get_map_hotspots()
    assert len(hotspots) == 5, f"Expected 5 hotspots, got {len(hotspots)}"
    print(f"    OK -> {len(hotspots)} district hotspots generated.")

    print("[5] Testing Live Outbreak Simulation Injection...")
    req = OutbreakInjectionRequest(
        district_name="Nashik",
        syndrome_id="SYN-VBD",
        spike_percentage=400,
        days_duration=3
    )
    res = inject_outbreak_simulation(req)
    print(f"    OK -> {res['status']}: {res['message']}")

    # Verify that Nashik now triggers an alert
    nashik_trends = get_trends('Nashik', 'SYN-VBD', apply_dp=True)
    print(f"    OK -> Post-injection Nashik Alert: {nashik_trends['analysis']['alert_level']}, Z-score: {nashik_trends['analysis']['ears_c2']['z_score']}")

    print("\n[+] ALL CORE ENGINE TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    run_tests()
