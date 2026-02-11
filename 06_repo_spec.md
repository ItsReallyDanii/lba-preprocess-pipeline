---
spec_version: 1.0.5
date: 2026-02-10
owner: Dev Lead
status: ACTIVE
---

# Repository Specification

## Structure (Local-First)
```text
lba-pipeline/
├── README.md
├── pyproject.toml
├── .gitignore
├── configs/
│   ├── preprocess.yaml      # Preprocessing thresholds
│   ├── model.yaml           # DANN Architecture
│   └── train.yaml           # Training loop config
├── data/
│   ├── raw/                 # Immutable inputs
│   ├── processed/           # Canonical Parquet files
│   └── reports/             # JSON logs & Artifacts
├── src/
│   ├── io/                  # Loaders
│   ├── preprocess/          # Clean/Resample/Split
│   │   ├── __init__.py
│   │   ├── config.py        # Typed config loader/validator
│   │   ├── main.py          # CLI entrypoint
│   │   └── ...
│   ├── models/              # DANN, CNN, Baselines
│   ├── align/               # Loss functions (GRL)
│   └── eval/                # Bootstrap, Calibration
├── experiments/
│   ├── 01_data_audit.ipynb
│   ├── 02_baseline_run.ipynb
│   └── 03_lba_run.ipynb
└── tests/
    ├── test_schema.py            # Assert Canonical Schema
    ├── test_split_leakage.py     # Assert ID disjointness
    ├── test_temporal_overlap.py  # Assert Interval Intersection
    └── test_determinism.py       # Assert Seed Fixed
```

## Config Contract (`configs/preprocess.yaml`)
Must include:
* `target_hz: 10`
* `window_seconds: 60`
* `stride_seconds: 10`
* `label_event_gap_seconds: 10`
* `flatline_std_min: 1e-6`
* `drift_slope_max_uv_per_s: 10.0`
* `snr_db_min: 3.0`
* `clip_fraction_max: 0.05`
* `max_rejection_rate_per_source: 0.30`
* `min_samples_per_family: 100`
* `min_samples_per_species: 50`
* `random_seed: 42`

## Artifacts Output (`data/processed/` & `data/reports/`)
* `dataset_clean.parquet` (Tier A)
* `dataset_model_ready.parquet` (Tier B)
* `split_manifest.parquet`
  * Schema: `source_id`, `plant_id`, `session_id`, `window_start_ts`, `window_end_ts`, `split`.
* `rejection_log.parquet`
* `data_quality_report.json`
* `unit_conversion_report.json`
* `config_snapshot.yaml`
* `data_fingerprint.json`

## Test Path Lock
* All tests live under `/tests`.
* Pytest discovery root is `/tests`.
* References to `src/preprocess/tests/` are FORBIDDEN.

---
Footer: Language pass applied: professional-safe | Consistency pass applied: schema/splits/artifacts aligned
