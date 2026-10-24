"""
ABDM (Ayushman Bharat Digital Mission) & HL7-FHIR Interoperability Module
Generates standardized FHIR R4 Observation bundles for syndromic surveillance.
"""

from datetime import datetime
from typing import Dict, Any, List

# Standard SNOMED-CT & LOINC concept codes for syndromic surveillance
SYNDROME_ONTOLOGY = {
    "SYN-ADD": {
        "code": "62315008",
        "system": "http://snomed.info/sct",
        "display": "Acute Diarrheal Syndrome",
        "loinc": "75325-1"
    },
    "SYN-VBD": {
        "code": "38362002",
        "system": "http://snomed.info/sct",
        "display": "Dengue/Vector-Borne Febrile Syndrome",
        "loinc": "6452-4"
    },
    "SYN-ARI": {
        "code": "195708003",
        "system": "http://snomed.info/sct",
        "display": "Acute Respiratory Infection Syndrome",
        "loinc": "43408-4"
    },
    "SYN-FWR": {
        "code": "271807003",
        "system": "http://snomed.info/sct",
        "display": "Febrile Rash Syndrome",
        "loinc": "32288-3"
    }
}

class FHIRExporter:
    @staticmethod
    def generate_fhir_bundle(records: List[Dict[str, Any]], district_name: str) -> Dict[str, Any]:
        """
        Converts internal syndromic surveillance records into an ABDM-compliant
        HL7-FHIR R4 Bundle containing Observation resources.
        """
        entries = []
        for r in records[-10:]: # Export latest 10 reporting windows
            syn_id = r.get("syndrome_id")
            ontology = SYNDROME_ONTOLOGY.get(syn_id, {
                "code": "418799008",
                "system": "http://snomed.info/sct",
                "display": "Symptom Cluster",
                "loinc": "75325-1"
            })

            obs_id = f"obs-{r.get('district_id', 'dist')}-{syn_id}-{r.get('date')}"
            
            entry = {
                "fullUrl": f"urn:uuid:{obs_id}",
                "resource": {
                    "resourceType": "Observation",
                    "id": obs_id,
                    "meta": {
                        "profile": [
                            "https://nrces.in/ndhm/fhir/r4/StructureDefinition/Observation"
                        ]
                    },
                    "status": "final",
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                    "code": "survey",
                                    "display": "Survey"
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": ontology["system"],
                                "code": ontology["code"],
                                "display": ontology["display"]
                            }
                        ],
                        "text": r.get("syndrome_name", "Syndromic Cluster")
                    },
                    "effectiveDateTime": f"{r.get('date')}T12:00:00+05:30",
                    "valueQuantity": {
                        "value": r.get("display_phc_consultations", r.get("phc_consultations", 0)),
                        "unit": "consultations",
                        "system": "http://unitsofmeasure.org",
                        "code": "{count}"
                    },
                    "component": [
                        {
                            "code": {
                                "text": "Associated OTC Pharmacy Surges"
                            },
                            "valueQuantity": {
                                "value": r.get("pharmacy_otc_sales", 0),
                                "unit": "units"
                            }
                        }
                    ],
                    "note": [
                        {
                            "text": f"Anonymized aggregate syndromic observation for {district_name}. Governed by k-anonymity (k>=5) and epsilon-DP."
                        }
                    ]
                }
            }
            entries.append(entry)

        return {
            "resourceType": "Bundle",
            "id": f"bundle-syndromic-{district_name.lower().replace(' ', '-')}",
            "meta": {
                "lastUpdated": datetime.now().isoformat()
            },
            "type": "collection",
            "total": len(entries),
            "entry": entries
        }
