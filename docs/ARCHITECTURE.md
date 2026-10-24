# 🏗️ OutbreakWatch Architecture & Engineering Design

## 1. Context & Motivation
Under India's **Integrated Disease Surveillance Programme (IDSP)** and the **Integrated Health Information Platform (IHIP)**, early syndromic identification enables containment of outbreaks weeks before laboratory serology confirmation arrives.

Traditional reporting suffers from:
* Reporting latency (5–14 days).
* Over-reliance on confirmed hospital lab tests rather than early community signals.
* Privacy risks when sharing granular health data from small villages/wards.

**OutbreakWatch** solves this via a decentralized, privacy-first syndromic aggregation pipeline.

---

## 2. Ingestion Subsystem

```
[ Primary Health Centers (PHCs) ] ──┐
[ ASHA Worker Community Surveys ] ──┼──> [ Ingestion Gateway ] ──> [ Normalization & Schema Validation ]
[ OTC Pharmacy Antipyretic Sales ] ─┘
```

### Data Feeds
1. **Clinical Screening Feed (PHC / Sub-Centres):** Non-diagnostic syndrome classifications:
   - Acute Respiratory Infection (ARI)
   - Acute Diarrheal Disease (ADD)
   - Fever with Rash
   - High Fever of Unknown Origin (Vector-Borne Suspect)
2. **Pharmacy Indicator Stream:** OTC sales of antipyretics (Paracetamol), anti-emetics, and Oral Rehydration Salts (ORS). Historically, drug sales spike 3–5 days prior to clinical presentations.
3. **Syndromic Tele-triage (IVR / Helpline):** Anonymized voice response transcripts and SMS surveys.

---

## 3. Privacy Preservation Pipeline

Before raw community reports enter the detection engine or dashboard, they pass through a strict **Two-Tier Privacy Layer**:

### Tier 1: $k$-Anonymity Cell Protection
* **Quasi-Identifiers:** Geolocation (Ward/Village), Age Bracket, Date of Onset.
* **Invariant:** For any query returning cell counts $N$, if $N < k$ (where $k=5$), the record count is suppressed (`<5`) or generalized to the parent administrative district to prevent patient identification in small communities.

### Tier 2: $\epsilon$-Differential Privacy via Laplace Mechanism
* To prevent reconstruction and membership inference attacks on the aggregated analytics, noise drawn from a Laplace distribution is added:
  $$\text{Noise} \sim \text{Laplace}\left(0, \frac{1}{\epsilon}\right)$$
* $\epsilon$ can be tuned from $0.2$ (maximum privacy, higher noise) to $1.5$ (analytical balance).

---

## 4. Anomaly Detection & Epidemiological Algorithms

### Algorithm 1: CDC EARS-C2
* Utilizes a 7-day sliding window ending two days prior to the current day ($t-9$ to $t-2$) to calculate baseline mean ($\mu$) and standard deviation ($\sigma$).
* Z-score calculation:
  $$Z(t) = \frac{C(t) - \mu}{\sigma}$$
* **Alert Levels:**
  - $Z < 2.0$: **Normal Baseline**
  - $2.0 \le Z < 3.0$: **Elevated Advisory**
  - $Z \ge 3.0$: **Critical Outbreak Warning**

### Algorithm 2: CUSUM (Cumulative Sum)
* Effective for slow, insidious outbreaks (e.g., waterborne pathogens entering a community over two weeks).
* Accumulates positive deviations:
  $$S_t = \max(0, S_{t-1} + (C(t) - \mu - k\sigma))$$
* When $S_t > h\sigma$, an alert is triggered.

---

## 5. Deployment & Scalability
* **Backend:** Asynchronous FastAPI with high-throughput Pydantic v2 validation.
* **Storage:** Extensible to PostGIS / TimescaleDB for production spatial-temporal time-series storage.
* **Frontend:** Zero-build portable HTML5/ES6 architecture utilizing Leaflet for lightweight mapping and Chart.js for responsive visual analytics.
