# 🔬 Epidemiological Modeling & Mathematical Privacy Safeguards

## 1. Algorithmic Overview: CDC EARS Suite

The **Early Aberration Reporting System (EARS)**, developed by the U.S. Centers for Disease Control and Prevention (CDC) and widely adapted by the WHO, is specifically designed for syndromic surveillance where long historical baselines may not be available or seasonal patterns shift rapidly.

### EARS C1, C2, and C3 Comparison
| Method | Baseline Window | Lag Period | Primary Strengths |
| :--- | :--- | :--- | :--- |
| **C1** | Past 7 days ($t-7$ to $t-1$) | 0 days | Responsive to immediate day-over-day surges. |
| **C2** | Past 7 days ($t-9$ to $t-2$) | 2 days | **OutbreakWatch Default.** Resilient to ongoing multi-day outbreaks contaminating the baseline. |
| **C3** | Sum of past 3 days of C2 scores | 2 days | Detects sustained multi-day gradual increases. |

### Mathematical Formula for EARS-C2
Given observed syndromic counts $Y_1, Y_2, \dots, Y_t$:

$$\bar{Y}_{C2} = \frac{1}{7} \sum_{i=2}^{8} Y_{t-i}$$

$$S_{C2} = \sqrt{\frac{1}{6} \sum_{i=2}^{8} (Y_{t-i} - \bar{Y}_{C2})^2}$$

$$C_2(t) = \frac{Y_t - \bar{Y}_{C2}}{S_{C2}}$$

---

## 2. Mathematical Privacy: $\epsilon$-Differential Privacy

In public health epidemiology, releasing aggregate statistics can inadvertently expose individuals to **membership inference attacks** if combined with auxiliary datasets (e.g., voter registration lists, insurance claims).

### Definition
A randomized algorithm $\mathcal{M}$ satisfies $\epsilon$-differential privacy if for any two neighboring datasets $D_1, D_2$ differing on at most one individual record, and for any set of outputs $S \subseteq \text{Range}(\mathcal{M})$:

$$\Pr[\mathcal{M}(D_1) \in S] \le e^{\epsilon} \cdot \Pr[\mathcal{M}(D_2) \in S]$$

### The Laplace Mechanism
For counting queries $f(D)$ with $L_1$ sensitivity $\Delta f = 1$:

$$\mathcal{M}(D) = f(D) + \text{Lap}\left(0, \frac{1}{\epsilon}\right)$$

Where the probability density function of the Laplace distribution is:

$$p(x) = \frac{1}{2b} \exp\left(-\frac{|x|}{b}\right), \quad b = \frac{1}{\epsilon}$$

### Practical Implementation in OutbreakWatch
1. When generating daily syndrome counts per sub-district, if the count is $< k$ ($k=5$), the count is suppressed.
2. For all public-facing queries, calibrated Laplace noise is injected, ensuring that whether any single citizen visited a clinic today cannot be discerned from the dashboard.
