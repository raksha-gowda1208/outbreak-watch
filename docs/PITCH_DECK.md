# 📊 OutbreakWatch Pitch Deck & Presentation Guide
**Innovators Conclave 2026 | Challenge Code: IC26-03-05 | MoHFW Track**

---

## Slide 1: Title & Overview
* **Header:** OutbreakWatch
* **Subtitle:** Privacy-Preserving Community Symptom Trend Intelligence & Outbreak Aberration Detector
* **Target:** Ministry of Health & Family Welfare (MoHFW) | Integrated Disease Surveillance Programme (IDSP)
* **Pillars:** Multi-Source Triangulation • CDC EARS-C2 Math • $\epsilon$-Differential Privacy

---

## Slide 2: Ground Reality & Core Problem
* **The 5-14 Day Blind Spot:** Current disease surveillance relies on confirmatory laboratory serology. By the time tests return positive, hospitals are already overwhelmed.
* **Ignored Community Early Signals:** ASHA worker screening surveys and localized OTC pharmacy antipyretic surges are not integrated into central monitoring.
* **The Privacy Barrier:** Granular reporting from rural sub-centres risks re-identifying patients in small communities.

---

## Slide 3: The OutbreakWatch Solution
* **Comprehensive Ingestion:** Aggregates primary care consults, OTC pharmacy medication sales (Paracetamol, ORS), and tele-triage logs.
* **Epidemiological Anomaly Math:** Replaces arbitrary thresholds with CDC EARS-C2 and CUSUM algorithms.
* **Zero-Trust Privacy:** Strict $k$-anonymity ($k \ge 5$) cell suppression and Laplace Differential Privacy ($\epsilon$-DP).
* **Decisive Triage Action:** Auto-generates actionable Rapid Response Team (RRT) advisories for District Surveillance Officers.

---

## Slide 4: System Architecture
* **Ingestion Gateway:** Normalizes multi-stream inputs into standardized feature vectors.
* **Privacy Layer:** Strips all PII and injects mathematically calibrated Laplace noise.
* **Aberration Core:** 7-day rolling baseline calculation with $Z$-score anomaly flags ($Z \ge 3.0\sigma$).
* **Surveillance Frontend:** Interactive Leaflet GIS Heatmap with time-series trajectory tracking.

---

## Slide 5: The Anomaly Detection Engine (CDC EARS-C2)
* **Formula:**
  $$C_2(t) = \frac{Y(t) - \bar{Y}_{C2}}{S_{C2}}$$
  Where baseline window spans $t-9$ to $t-2$ (7 days with 2-day buffer) to prevent ongoing outbreaks from corrupting the baseline.
* **Lead Indicator Detection:** Identifies pharmacy OTC sales surges peaking 3 to 5 days ahead of clinical hospital presentations.

---

## Slide 6: Mathematical Privacy Safeguards
* **$k$-Anonymity ($k \ge 5$):** Any sub-centre reporting $< 5$ cases is masked to protect small communities against linkage attacks.
* **Laplace Differential Privacy ($\epsilon$-DP):**
  $$M(D) = f(D) + \text{Laplace}\left(0, \frac{\Delta f}{\epsilon}\right)$$
  Mathematically guarantees that the presence or absence of any single citizen cannot be reconstructed from public dashboard queries.

---

## Slide 7: Live Demonstration (The Chaos Outbreak Injector)
* **Baseline Inspection:** Routine monitoring across Maharashtra pilot districts.
* **Live Anomaly Injection:** Select District: Pune, Syndrome: Acute Diarrheal Disease, Magnitude: +300% surge.
* **Instant Reaction:** Map triggers pulsing red radar node, EARS-C2 flags $Z = 3.42$, and automated CMO advisory dispatches in real-time.

---

## Slide 8: ABDM / FHIR Interoperability & Scalability
* **National Standards:** Outputs HL7-FHIR `Observation` bundles compatible with Ayushman Bharat Digital Mission (ABDM).
* **GIS Interoperability:** Generates standardized GeoJSON for state disaster management GIS portals.
* **Production Ready:** Fully containerized with Docker, automated GitHub Actions CI pipeline, and modular FastAPI architecture.

---

## Slide 9: Competitive Moat & Summary
* **Comparison Matrix:**
  * Conventional Hackathon Projects: Static CSV tables, arbitrary `count > 50` thresholds, zero privacy guarantees.
  * OutbreakWatch: Multi-stream triangulation, CDC-validated anomaly algorithms, mathematical differential privacy, and live chaos outbreak injector.
