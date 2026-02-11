---
spec_version: 1.0.5
date: 2026-02-10
owner: Experiment Lead
status: ACTIVE
---

# Experiment Protocol

## 1. Split Strategy: "Double-Blind Holdout"
* **Hierarchy:** `family_id` -> `species_id` -> `plant_id` -> `session_id`.
* **Train:** Families {A, B} + Hardware {1}.
* **Validation:** Family {A} (Held-out Species) + Hardware {1} (Calibrate here).
* **Test (Zero-Shot):** Family {C} + Hardware {2} (Explicit Hardware Holdout).

## 2. Model Architecture (DANN)
* **Feature Extractor:** 3-layer 1D-CNN ($k=3, \text{stride}=1$).
* **Label Classifier:** 2-layer MLP (ReLU, Dropout 0.5).
* **Domain Discriminator:** 3-layer MLP + Gradient Reversal Layer (GRL).
* **Loss Function:** $L = L_{class} - \lambda L_{domain}$.

## 3. Negative Controls (Mandatory)
* **Control A (Shuffled Labels):** Randomize labels in training. Test set F1 must track random chance.
* **Control B (Domain Only):** Freeze Encoder, train Classifier to predict `species_id` or `hardware_id`. Accuracy should be minimized in the aligned space.

## 4. Calibration
* **Method:** Temperature Scaling on Validation Set only.
* **Report:** ECE (Expected Calibration Error) pre- and post-scaling.

## 5. Uncertainty
* **Method:** Paired Bootstrap Resampling ($N=1000$ iterations).
* **Output:** Mean $\Delta$ F1 + 95% Confidence Interval (e.g., "+12% [8%, 16%]").

---
Footer: Language pass applied: professional-safe | Consistency pass applied: schema/splits/artifacts aligned
