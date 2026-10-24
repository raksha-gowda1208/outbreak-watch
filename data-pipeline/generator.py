"""
OutbreakWatch Synthetic Syndromic Data Generator
Generates realistic multi-stream epidemiological baseline data and configurable outbreak scenarios.
"""

import json
import random
import math
from datetime import datetime, timedelta

DISTRICTS = [
    {
        "id": "DIST-01",
        "name": "Pune",
        "state": "Maharashtra",
        "lat": 18.5204,
        "lon": 73.8567,
        "population": 9429408,
        "phcs": [
            {"id": "PHC-PUN-01", "name": "Haveli PHC", "lat": 18.5089, "lon": 73.8742},
            {"id": "PHC-PUN-02", "name": "Khadakwasla Subcentre", "lat": 18.4410, "lon": 73.7629},
            {"id": "PHC-PUN-03", "name": "Shirur Community Clinic", "lat": 18.8267, "lon": 74.3789},
            {"id": "PHC-PUN-04", "name": "Baramati Rural Hospital", "lat": 18.1517, "lon": 74.5774}
        ]
    },
    {
        "id": "DIST-02",
        "name": "Mumbai Suburban",
        "state": "Maharashtra",
        "lat": 19.0760,
        "lon": 72.8777,
        "population": 9356962,
        "phcs": [
            {"id": "PHC-MUM-01", "name": "Kurla Health Post", "lat": 19.0657, "lon": 72.8794},
            {"id": "PHC-MUM-02", "name": "Andheri East Dispensary", "lat": 19.1136, "lon": 72.8697},
            {"id": "PHC-MUM-03", "name": "Borivali Urban PHC", "lat": 19.2288, "lon": 72.8541}
        ]
    },
    {
        "id": "DIST-03",
        "name": "Nashik",
        "state": "Maharashtra",
        "lat": 19.9975,
        "lon": 73.7898,
        "population": 6107187,
        "phcs": [
            {"id": "PHC-NSK-01", "name": "Panchavati Urban Centre", "lat": 20.0110, "lon": 73.8012},
            {"id": "PHC-NSK-02", "name": "Sinnar Rural Hospital", "lat": 19.8458, "lon": 74.0028},
            {"id": "PHC-NSK-03", "name": "Trimbak PHC", "lat": 19.9324, "lon": 73.5306}
        ]
    },
    {
        "id": "DIST-04",
        "name": "Thane",
        "state": "Maharashtra",
        "lat": 19.2183,
        "lon": 72.9781,
        "population": 8070032,
        "phcs": [
            {"id": "PHC-THN-01", "name": "Kalyan Health Centre", "lat": 19.2437, "lon": 73.1355},
            {"id": "PHC-THN-02", "name": "Bhiwandi Subcentre", "lat": 19.2967, "lon": 73.0631}
        ]
    },
    {
        "id": "DIST-05",
        "name": "Nagpur",
        "state": "Maharashtra",
        "lat": 21.1458,
        "lon": 79.0882,
        "population": 4653570,
        "phcs": [
            {"id": "PHC-NGP-01", "name": "Sitabuldi Urban Health Centre", "lat": 21.1472, "lon": 79.0819},
            {"id": "PHC-NGP-02", "name": "Kamptee Rural Clinic", "lat": 21.2230, "lon": 79.1970}
        ]
    }
]

SYNDROMES = [
    {
        "id": "SYN-ARI",
        "name": "Acute Respiratory Infection",
        "baseline_rate_per_10k": 12.0,
        "otc_counterpart": "Cough Syrup & Antihistamines",
        "description": "Fever, cough, sore throat, shortness of breath"
    },
    {
        "id": "SYN-ADD",
        "name": "Acute Diarrheal Disease",
        "baseline_rate_per_10k": 8.5,
        "otc_counterpart": "ORS & Anti-diarrheal Packets",
        "description": "Loose watery stools >= 3 times/day, dehydration"
    },
    {
        "id": "SYN-VBD",
        "name": "Vector-Borne / High Fever",
        "baseline_rate_per_10k": 5.0,
        "otc_counterpart": "Paracetamol 650mg & Analgesics",
        "description": "Sudden high fever, retro-orbital pain, severe arthralgia"
    },
    {
        "id": "SYN-FWR",
        "name": "Fever with Rash",
        "baseline_rate_per_10k": 2.1,
        "otc_counterpart": "Topical Calamine & Paracetamol",
        "description": "Maculopapular rash accompanied by febrile illness"
    }
]

def generate_synthetic_dataset(days_back=30, inject_active_outbreak=True):
    """
    Generates a 30-day multi-stream synthetic dataset with realistic
    baseline variations, day-of-week seasonality, and an optional subtle outbreak.
    """
    random.seed(42)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    daily_records = []
    
    current_date = start_date
    day_index = 0
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        is_weekend = current_date.weekday() in (5, 6)
        weekend_factor = 0.75 if is_weekend else 1.0  # PHC visits drop on weekends
        
        for district in DISTRICTS:
            pop_factor = district["population"] / 1_000_000
            
            for syn in SYNDROMES:
                base_count = (syn["baseline_rate_per_10k"] * pop_factor) * weekend_factor
                # Add natural Poisson-like variation
                noise = random.gauss(0, math.sqrt(max(1, base_count)))
                case_count = max(0, int(round(base_count + noise)))
                
                # Associated OTC Pharmacy sales surge (usually higher volume than PHC visits)
                otc_multiplier = random.uniform(2.8, 3.5)
                otc_units_sold = int(round(case_count * otc_multiplier + random.randint(10, 40)))
                
                # Community tele-triage IVR reports (subset of self-reporting citizens)
                tele_reports = int(round(case_count * random.uniform(0.15, 0.35)))
                
                # Active outbreak injection (e.g. Pune has an emerging Acute Diarrheal surge in last 4 days)
                is_anomaly_injected = False
                if inject_active_outbreak and district["name"] == "Pune" and syn["id"] == "SYN-ADD":
                    days_from_end = (end_date - current_date).days
                    if days_from_end <= 4:
                        # Gradual exponential spike: Day -4: +80%, Day -3: +160%, Day -2: +240%, Today: +380%
                        surge_multiplier = 1.0 + (5 - days_from_end) * 0.75
                        case_count = int(round(case_count * surge_multiplier))
                        otc_units_sold = int(round(otc_units_sold * (surge_multiplier + 0.4)))
                        tele_reports = int(round(tele_reports * (surge_multiplier + 0.6)))
                        is_anomaly_injected = True
                
                # Generate granular PHC sub-allocations
                phc_allocations = []
                remaining_cases = case_count
                for idx, phc in enumerate(district["phcs"]):
                    if idx == len(district["phcs"]) - 1:
                        allocated = remaining_cases
                    else:
                        share = random.uniform(0.2, 0.4)
                        allocated = min(remaining_cases, int(round(case_count * share)))
                        remaining_cases -= allocated
                    
                    phc_allocations.append({
                        "phc_id": phc["id"],
                        "phc_name": phc["name"],
                        "lat": phc["lat"],
                        "lon": phc["lon"],
                        "raw_cases": max(0, allocated)
                    })
                
                record = {
                    "date": date_str,
                    "district_id": district["id"],
                    "district_name": district["name"],
                    "lat": district["lat"],
                    "lon": district["lon"],
                    "syndrome_id": syn["id"],
                    "syndrome_name": syn["name"],
                    "phc_consultations": case_count,
                    "pharmacy_otc_sales": otc_units_sold,
                    "tele_triage_calls": tele_reports,
                    "phc_breakdown": phc_allocations,
                    "is_simulated_outbreak": is_anomaly_injected
                }
                daily_records.append(record)
                
        current_date += timedelta(days=1)
        day_index += 1
        
    return {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "districts_count": len(DISTRICTS),
            "syndromes_count": len(SYNDROMES),
            "total_records": len(daily_records),
            "days_covered": days_back + 1
        },
        "districts": DISTRICTS,
        "syndromes": SYNDROMES,
        "records": daily_records
    }

if __name__ == "__main__":
    print("[*] Generating synthetic multi-stream syndromic dataset...")
    data = generate_synthetic_dataset(days_back=30, inject_active_outbreak=True)
    with open("seed_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Successfully generated {data['metadata']['total_records']} records across {data['metadata']['districts_count']} districts.")
