---
spec_version: 1.0.5
date: 2026-02-10
owner: Phase 1 Lead
status: ACTIVE
---

# Project Charter: Latent Bio-Signal Alignment (LBA)

## 1. Mission
To develop a software-only, cross-domain alignment pipeline that maps disparate plant bio-electrical time-series into a shared latent embedding space, enabling zero-shot stress inference across botanical families and hardware types.

## 2. Problem Statement: The Domain Shift Gap
Current plant electrophysiology models suffer from significant brittleness due to domain shift. A model trained on *Solanum tuberosum* (Potato) using needle electrodes typically fails to generalize to *Glycine max* (Soybean) using surface electrodes. The lack of a "universal translation layer" prevents the utilization of heterogeneous public datasets for robust stress prediction.

## 3. The Technical Win
A **Domain-Adversarial Neural Network (DANN)** or **Contrastive (CLOCS)** pipeline that:
1.  Ingests raw time-series from multiple species and hardware sources.
2.  Aligns them in a shared latent space by minimizing domain-specific feature variance.
3.  Achieves statistically significant relative F1 lift in zero-shot classification (Held-out Family) compared to standard fine-tuning.

## 4. Scope (Phase 1)
* **In-Scope:** Public datasets (Zenodo/Kaggle), Python/PyTorch implementation, DANN architecture, Cross-Family validation.
* **Out-of-Scope:** New wet-lab experiments, custom hardware, unproven "Foundation Model" claims, commercial deployment.

## 5. Success Definition
* **Strategic Discard:** If data quality (drift/artifacts) prevents stable alignment or requires excessive rejection (>30%).
* **Technical Win:** If Gate 2 (Relative Lift) is passed with calibrated uncertainty.

---
Footer: Language pass applied: professional-safe | Consistency pass applied: schema/splits/artifacts aligned
