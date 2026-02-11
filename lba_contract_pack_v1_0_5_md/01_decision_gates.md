---
spec_version: 1.0.5
date: 2026-02-10
owner: Phase 1 Lead
status: ACTIVE
---

# Decision Gates & Success Metrics

## Gate 0: Data Integrity (The "Kill Switch")
* **Trigger:** Post-preprocessing (`preprocess.py`).
* **Metric:** `rejection_rate_per_source` < 30%.
* **Metric:** `leakage_checks.status` == "PASS" with pairwise disjointness across (train,val), (train,test), (val,test) for `plant_id` and `session_id`, and zero forbidden temporal overlap.
* **Fail Condition:** >30% data loss due to noise, or any detectable label leakage (`leakage_checks.offending_ids` is not empty).
* **Action:** Stop. Do not train. Archive project.

## Gate 1: Sanity Check (Imbalance-Aware)
* **Trigger:** First zero-shot validation run.
* **Definition:** `Majority_Class_Baseline_F1`: Macro-F1 from always predicting majority class in test split.
* **Definition:** `random_f1_mean` = mean(F1_seed_i for i in 0..99) from stratified random predictions.
* **Definition:** `random_f1_p95` = quantile(F1_seed_i, 0.95, method="linear").
* **Metric:** `ZeroShot_MacroF1` >= `max(Majority_Class_Baseline_F1, random_f1_mean) + 0.02`.
* **Metric:** `ZeroShot_MacroF1` >= `random_f1_p95 + 0.01`.
* **Metric:** `ECE_PostCalib` < 0.05 (Validation Set).
* **Fail Condition:** Model fails to beat trivial baselines by required margin or exhibits high calibration error.
* **Action:** Debug architecture; if persistent, kill.

## Gate 2: The Technical Win (The "Delta")
* **Trigger:** Comparison vs. Baseline (Fine-Tuned Transfer).
* **Metric:** `Relative_Lift_F1` >= 10%.
* **Metric:** `Lift_LowerBound_CI` > 0 (95% Bootstrap CI).
* **Fail Condition:** Lift is statistically insignificant (CI crosses zero).
* **Action:** Pivot to "Negative Result" report; do not claim novelty.

## Gate 3: Impact (The "Stretch")
* **Trigger:** Final Evaluation.
* **Metric:** `Relative_Lift_F1` >= 15%.
* **Metric:** `Worst_Case_Robustness` (performance drop under noise) < 20%.
* **Action:** Proceed to publication/Phase 2.

---
Footer: Language pass applied: professional-safe | Consistency pass applied: schema/splits/artifacts aligned
