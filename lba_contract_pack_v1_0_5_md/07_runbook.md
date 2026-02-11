---
spec_version: 1.0.5
date: 2026-02-10
owner: Ops Lead
status: ACTIVE
---

# Execution Runbook

## Phase 1: Data Audit (Day 1)
1.  **Ingest:** Place raw CSVs in `data/raw/`.
2.  **Config:** Update `configs/preprocess.yaml` with dataset specifics.
3.  **Run:** `python -m src.preprocess.main --config configs/preprocess.yaml`.
4.  **Verify:** Check `data/reports/data_quality_report.json`.
    * **Decision:** If `rejection_rate_per_source` > 0.30, ABORT.
    * **Check:** Verify `leakage_checks.status` == "PASS".

## Phase 2: Baselines (Day 2)
1.  **Train:** Run Baseline 2 (Fine-Tuned CNN).
2.  **Log:** Record F1 and ECE on Test Set.
3.  **Control:** Run `Shuffled_Label_Probe`. Ensure F1 ~ Random Chance.

## Phase 3: Alignment (Day 3)
1.  **Train:** Run LBA (DANN) model.
2.  **Compare:** Calculate $\Delta$ F1 vs Baseline.
3.  **Bootstrap:** Run `src.eval.bootstrap` to get 95% CI.

## Phase 4: Decision
1.  **Check:** Compare results against `01_decision_gates.md`.
2.  **Report:** Generate `final_verdict.md`.

---
Footer: Language pass applied: professional-safe | Consistency pass applied: schema/splits/artifacts aligned
