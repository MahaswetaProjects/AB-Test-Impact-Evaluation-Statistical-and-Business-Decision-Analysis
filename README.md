# A/B-Test-Impact-Evaluation-Statistical-and-Business-Decision-Analysis

**Overview**

This project evaluates the impact of a product change using a controlled A/B experiment.
The goal is to determine whether a new checkout page design leads to a statistically and practically meaningful improvement in conversion rate, and to make a data-driven business decision on whether the change should be shipped.

**Problem Statement**

A redesigned checkout page was tested against the existing version to reduce cart abandonment.
The analysis answers whether the observed improvement is real, reliable, and worth deploying from a business perspective.

**Key Concepts Used**

Experiment design and hypothesis formulation

Sample size calculation using power analysis

A/B and A/A testing

Statistical inference using proportion Z-tests

Confidence intervals and effect size analysis

Practical vs statistical significance

Revenue impact estimation

Decision-making under uncertainty

**Methodology**

Defined control and treatment groups with user-level randomization

Calculated required sample size to ensure sufficient statistical power

Simulated realistic conversion data

Validated experiment setup using an A/A test

Performed hypothesis testing on conversion rates

Computed confidence intervals and lift

Translated statistical results into business impact

Made a final ship or no-ship recommendation

**Key Outcome**

The treatment variant showed a statistically significant and practically meaningful increase in conversion rate.
Based on the estimated revenue uplift and validation checks, the feature is recommended for deployment with monitoring.

**Tools and Libraries**

Python

NumPy

Pandas

Statsmodels

Matplotlib
