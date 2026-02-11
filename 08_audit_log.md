---
spec_version: 1.0.5
date: 2026-02-10
owner: Auditor
status: TEMPLATE
---

# Audit Log

| Date | Gate | Metric | Value | Threshold | Result (Pass/Fail) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| YYYY-MM-DD | Gate 0 (Data) | Rejection Rate | --% | < 30% | -- | -- |
| YYYY-MM-DD | Gate 0 (Data) | Leakage Checks | -- | PASS | -- | Verified by `test_split_leakage.py` |
| YYYY-MM-DD | Gate 1 (Sanity) | Zero-Shot F1 | -- | > Formula | -- | vs Max(Majority, Random) |
| YYYY-MM-DD | Gate 2 (Win) | Relative Lift | --% | > 10% | -- | CI: [LB, UB] |
| YYYY-MM-DD | Gate 3 (Impact) | Robustness | --% | < 20% drop | -- | -- |

## Final Recommendation
[ ] Strategic Discard
[ ] Technical Win

---
Footer: Language pass applied: professional-safe | Consistency pass applied: schema/splits/artifacts aligned
