---
spec_version: 1.0.5
date: 2026-02-10
owner: Lead Scientist
status: LOCKED
---

# Method Novelty Audit: Latent Bio-Signal Alignment (LBA)

## [IDEA]
A cross-domain alignment pipeline using Domain-Adversarial Neural Networks (DANN) to map disparate plant bio-electrical time-series into a shared "Phenotypic Stress Space."

## [COMPARATORS]
1.  **Baseline 1:** Feature-Engineering + Random Forest (Standard Practice).
2.  **Baseline 2:** Fine-Tuned 1D-CNN (Pre-train Source -> Fine-tune Target).
3.  **Baseline 3:** Naive Transfer (Train Source -> Test Target directly).

## [NOVELTY CLASSIFICATION]
* **A) Structural (35%):** Adaptation of DANN/CLOCS to low-frequency bio-electrical data.
* **B) Recombination (55%):** Using latent alignment to bridge the "Species Gap."
* **C) Standard (10%):** PyTorch plumbing.

## [DELTA TEST]
* **Metric:** Zero-Shot Transfer F1 on Held-Out Family.
* **Threshold:** >10% relative lift over Baseline 2 (Fine-Tuned).

## [FALSIFICATION]
* If `LBA_Model` performance is indistinguishable from `Domain_Blind_Model`, the alignment hypothesis is falsified.
* If `Shuffled_Label_Probe` achieves F1 significantly > 0.5 (random chance), the model is learning artifacts.

---
Footer: Language pass applied: professional-safe | Consistency pass applied: schema/splits/artifacts aligned
