"""
OutbreakWatch Scenario Loader CLI
Allows evaluators and operators to inspect, validate, and inject curated epidemic scenarios.
"""

import argparse
import json
import os
import sys

SCENARIOS = {
    "dengue": {
        "title": "Post-Monsoon Vector-Borne Surge (Dengue Outbreak)",
        "district": "Pune",
        "syndrome": "SYN-VBD",
        "spike_percentage": 320,
        "days": 4,
        "description": "Simulates water stagnation in urban slums following irregular monsoon showers, resulting in sudden high fever spikes and acute Paracetamol OTC depletion."
    },
    "cholera": {
        "title": "Municipal Water Contamination (Acute Diarrheal Outbreak)",
        "district": "Nashik",
        "syndrome": "SYN-ADD",
        "spike_percentage": 420,
        "days": 3,
        "description": "Simulates pipeline breach near industrial drainage, precipitating severe watery diarrhea admissions and an emergency surge in ORS distribution."
    },
    "flu": {
        "title": "Seasonal Pediatric Influenza & Viral Pneumonia Wave",
        "district": "Nagpur",
        "syndrome": "SYN-ARI",
        "spike_percentage": 260,
        "days": 5,
        "description": "Simulates school-term respiratory virus cluster across sub-centre OPDs, elevating cough syrup sales and tele-triage call volumes."
    }
}

def list_scenarios():
    print("=" * 70)
    print("OUTBREAKWATCH CURATED EPIDEMIOLOGICAL SCENARIOS")
    print("=" * 70)
    for key, sc in SCENARIOS.items():
        print(f"\n[*] Preset Key: '{key}'")
        print(f"    Title:       {sc['title']}")
        print(f"    District:    {sc['district']}")
        print(f"    Syndrome:    {sc['syndrome']}")
        print(f"    Magnitude:   +{sc['spike_percentage']}% surge over {sc['days']} days")
        print(f"    Context:     {sc['description']}")
    print("\n" + "=" * 70)

def main():
    parser = argparse.ArgumentParser(description="OutbreakWatch Scenario Evaluation CLI")
    parser.add_argument("--list", action="store_true", help="List all pre-configured epidemic scenarios")
    parser.add_argument("--scenario", choices=["dengue", "cholera", "flu"], help="Preset scenario to inspect")
    
    args = parser.parse_args()

    if args.list or not args.scenario:
        list_scenarios()
        return

    sc = SCENARIOS[args.scenario]
    print(f"\n[+] Loading scenario: {sc['title']}")
    print(f"[+] Target District:  {sc['district']}")
    print(f"[+] Syndrome Code:    {sc['syndrome']}")
    print(f"[+] Aberration Surge: +{sc['spike_percentage']}%")
    print(f"\nReady to execute via OutbreakWatch Dashboard or API (/api/simulate/inject).")

if __name__ == "__main__":
    main()
