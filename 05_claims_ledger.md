---
spec_version: 1.0.5
date: 2026-02-10
owner: Review Lead
status: DRAFT
---

# Claims Ledger

## Safe Claims (Defensible)
1.  "Latent alignment reduces performance degradation under cross-species shift compared to naive transfer baselines."
2.  "The pipeline improves calibration (ECE) on held-out families relative to unaligned models."
3.  "Bio-electrical signals exhibit shared stress-response morphologies across tested families when mapped to a shared latent space."

## Risky Claims (Forbidden without Gate 3)
1.  "Universal Plant Interface." (Too broad).
2.  "Generalizes to all plant species." (Inductive fallacy).
3.  "Replaces wet-lab calibration." (Overclaim).

## Reviewer Defense
* **Objection:** "Is the model learning electrode noise?"
    * **Defense:** "Negative Control B (Domain Probe) confirms latent space is invariant to `hardware_id`."
* **Objection:** "Are the labels leaky?"
    * **Defense:** "Temporal decoupling enforced in `preprocess.py`; feature windows are strictly disjoint from label event windows."

---
Footer: Language pass applied: professional-safe | Consistency pass applied: schema/splits/artifacts aligned
