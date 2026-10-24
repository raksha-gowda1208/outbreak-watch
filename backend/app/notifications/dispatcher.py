"""
OutbreakWatch Rapid Response & Alert Dispatch Engine
Generates and dispatches multi-channel advisories (SMS/WhatsApp/Email) to District Surveillance Officers.
"""

from datetime import datetime
from typing import Dict, Any, List

class AlertDispatcher:
    def __init__(self):
        self.dispatch_history: List[Dict[str, Any]] = []

    def generate_dispatch_payload(self, anomaly_report: Dict[str, Any], recipient_role: str = "District Surveillance Officer") -> Dict[str, Any]:
        """
        Creates an actionable triage payload containing epidemiological metrics
        and clinical rapid response protocols.
        """
        district = anomaly_report.get("district_name", "Unknown District")
        syndrome = anomaly_report.get("syndrome_name", "Syndromic Aberration")
        alert_level = anomaly_report.get("alert_level", "NORMAL")
        z_score = anomaly_report.get("ears_c2", {}).get("z_score", 0.0)
        
        # Clinical response protocol mapping based on syndrome
        protocols = {
            "Acute Diarrheal Disease": [
                "1. Immediate testing of municipal and borewell water chlorine residual (OT test).",
                "2. Pre-position ORS and IV fluids at rural primary health centers.",
                "3. Deploy ASHA workers for door-to-door ORS packet distribution in affected wards.",
                "4. Collect stool specimens for hanging drop and culture examination."
            ],
            "Vector-Borne / High Fever": [
                "1. Mobilize vector control teams for focal indoor space spraying and source reduction.",
                "2. Stock platelet transfusion packs and NS1/IgM rapid diagnostic kits at Civil Hospital.",
                "3. Issue community advisory on dry-day observance and preventing freshwater stagnation."
            ],
            "Acute Respiratory Infection": [
                "1. Activate respiratory triage desk at outpatient departments (OPD).",
                "2. Enforce droplet precautions and surgical mask distribution.",
                "3. Review pulse oximeter and oxygen concentrator inventory at taluk hospitals."
            ],
            "Fever with Rash": [
                "1. Check regional measles/rubella vaccination coverage in child cohorts under 5.",
                "2. Administer Vitamin A therapeutic doses to symptomatic pediatric cases.",
                "3. Institute contact tracing within 72 hours of rash onset."
            ]
        }

        matched_protocol = []
        for key, steps in protocols.items():
            if key.lower() in syndrome.lower():
                matched_protocol = steps
                break
        if not matched_protocol:
            matched_protocol = ["1. Initiate localized epidemiological contact tracing.", "2. Review laboratory requisition logs."]

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        dispatch_id = f"DISPATCH-MoHFW-{int(datetime.now().timestamp())}"

        sms_summary = f"[MoHFW-IDSP ALERT] {alert_level} Aberration in {district} ({syndrome}, Z={z_score}). RRT mobilization recommended. Ref: {dispatch_id}"

        dispatch_record = {
            "dispatch_id": dispatch_id,
            "timestamp": timestamp,
            "recipient_role": recipient_role,
            "district_name": district,
            "syndrome_name": syndrome,
            "alert_level": alert_level,
            "z_score": z_score,
            "sms_text": sms_summary,
            "action_protocol": matched_protocol,
            "channels": ["SMS Gateway (NIC-Push)", "State Health WhatsApp Bot", "DSO Email Digest"],
            "status": "DISPATCHED"
        }

        self.dispatch_history.insert(0, dispatch_record)
        return dispatch_record

    def get_history(self) -> List[Dict[str, Any]]:
        return self.dispatch_history

# Global singleton
dispatcher = AlertDispatcher()
