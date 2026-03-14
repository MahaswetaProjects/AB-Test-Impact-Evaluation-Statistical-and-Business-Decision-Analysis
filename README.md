# 🧪 A/B Test Impact Evaluation — Checkout Redesign

> **Statistical & Business Decision Analysis** | Python · Statsmodels · Streamlit

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📋 Executive Summary

| Metric | Value |
|---|---|
| **Experiment** | Checkout Page Redesign (UX simplification) |
| **Sample Size** | 3,835 users per group (7,670 total) |
| **Control Conversion** | 9.15% |
| **Treatment Conversion** | 12.07% |
| **Relative Lift** | **+31.9%** |
| **p-value** | **< 0.0001** |
| **Estimated Monthly Uplift** | **₹2.33 Crore** |
| **Recommendation** | ✅ **Ship** |

---

## 🎯 Problem Statement

An e-commerce platform's checkout page had a ~90% cart abandonment rate. The product team redesigned the checkout UX to reduce friction. This project evaluates whether the redesign produces a statistically significant and practically meaningful improvement before committing to a full rollout.

**Key Question:**
> *Does the new checkout design improve conversion rate enough to justify deployment?*

---

## 🔬 Methodology

### 1. Experiment Design
- **Randomisation unit**: User-level (prevents contamination)
- **Groups**: Control (A) = existing page, Treatment (B) = redesigned page
- **Primary metric**: Conversion rate (checkout completion)
- **Significance level**: α = 0.05 | **Power**: 80%

### 2. Statistical Pipeline

```
Power Analysis → Sample Size Calculation
       ↓
Data Collection & Quality Checks
       ↓
A/A Test Validation (infrastructure check)
       ↓
Hypothesis Testing (Two-tailed Z-test for proportions)
       ↓
Confidence Intervals (Wilson method)
       ↓
Effect Size (Cohen's h)
       ↓
Segment Analysis (device × user type)
       ↓
Business Impact & Sensitivity Analysis
       ↓
Ship / No-Ship Decision
```

### 3. Key Statistical Concepts Applied

| Concept | Why It Matters |
|---|---|
| **Power Analysis** | Prevents underpowered tests / resource waste |
| **A/A Test** | Validates randomisation infrastructure |
| **Z-test for proportions** | Correct test for binary conversion metric |
| **Wilson CI** | More accurate than normal approximation for proportions |
| **Cohen's h** | Quantifies effect size independent of sample size |
| **Lift CI** | Shows uncertainty range of the business impact |
| **Segment Analysis** | Detects heterogeneous treatment effects |
| **Sensitivity Analysis** | Stress-tests revenue projections |

---

## 📊 Key Results

### Statistical Significance
- **Z-statistic**: −4.15
- **p-value**: 3.3 × 10⁻⁵ (far below α = 0.05)
- **Lift 95% CI**: [1.67%, 4.17%] — entirely above zero

### Practical Significance
- **Absolute lift**: +2.92 percentage points
- **Relative lift**: +31.9%
- **Cohen's h**: 0.098 (small–medium effect)

### Business Impact
| Scenario | Monthly Uplift | Annual Uplift |
|---|---|---|
| Conservative (CI lower) | ₹1.33 Cr | ₹15.96 Cr |
| **Point estimate** | **₹2.33 Cr** | **₹27.96 Cr** |
| Optimistic (CI upper) | ₹3.33 Cr | ₹39.96 Cr |

### Decision Checklist
- ✅ Statistical significance: p < 0.05
- ✅ Practical significance: lift ≥ 1%
- ✅ A/A test passed: no false positive detected
- ✅ Lift CI entirely above zero
- ✅ Effect consistent across device segments

---

## 🗂️ Repository Structure

```
📦 ab-test-checkout-redesign/
├── 📓 AB_Test_Impact_Evaluation.ipynb   ← Full analysis notebook
├── 🖥️  app.py                            ← Interactive Streamlit dashboard
├── 📄 README.md                          ← This file
└── 📋 requirements.txt                  ← Dependencies
```

---

## 🚀 Quick Start

### Run the Notebook
```bash
pip install -r requirements.txt
jupyter notebook AB_Test_Impact_Evaluation.ipynb
```

### Launch the Dashboard
```bash
pip install -r requirements.txt
streamlit run app.py
```
The dashboard opens at `http://localhost:8501`

---

## 🖥️ Interactive Dashboard Features

The Streamlit dashboard (`app.py`) lets you:

| Feature | Description |
|---|---|
| **Live parameter tuning** | Adjust α, power, MDE, sample size, AOV |
| **Statistical results** | Z-test, p-value, CIs, effect size |
| **Segment explorer** | Lift breakdown by device and user type |
| **Revenue calculator** | 3-scenario business impact with heatmap |
| **Decision checklist** | Automated ship/no-ship recommendation |

---

## 📈 Charts Generated

| Chart | File |
|---|---|
| EDA overview (conversion rates, device, user type) | `eda_overview.png` |
| Confidence intervals + bootstrap distribution | `confidence_intervals.png` |
| Segment lift (device × user type) | `segment_analysis.png` |
| Revenue scenarios + heatmap | `business_impact.png` |

---

## 🔮 Future Work

1. **Bayesian A/B Testing** — Posterior probability of treatment being best; natural early stopping
2. **Sequential Testing (SPRT)** — Peek at results without inflating Type I error
3. **Multi-armed Bandit** — Dynamically shift traffic to maximise revenue during experiment
4. **Uplift Modelling (CATE)** — Identify which user segments benefit most from the treatment
5. **Long-term retention analysis** — Does conversion lift translate to higher 30/60/90-day LTV?

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **Python** | Core analysis |
| **NumPy / Pandas** | Data manipulation |
| **Statsmodels** | Statistical tests, power analysis |
| **Scipy** | Bootstrap sampling |
| **Matplotlib / Seaborn** | Visualisations |
| **Streamlit** | Interactive dashboard |

---

## 📬 Author

**Mahasweta Talik**
- 📧 mahasweta005talik@gmail.com
- 💼 [LinkedIn](https://linkedin.com/in/your-profile)
- 🐙 [GitHub](https://github.com/your-username)

---

*This project demonstrates end-to-end A/B test design, statistical validation, and business impact quantification — core skills for data analyst and data scientist roles.*
