---
spec_version: 1.0.5
date: 2026-02-10
owner: Data Engineer
status: ACTIVE
---

# Data Contract & Schema

## 1. Canonical Schema (`processed/`)
All processed Parquet files must adhere to this schema:
* `timestamp_utc` (datetime64[ns]): UTC timestamp of sample.
* `value_uv` (float32): Standardized signal amplitude in microvolts.
* `value_norm` (float32, optional): Normalized amplitude for modeling. **See Normalization Boundary below.**
* `label` (int8): 0=Control, 1=Stressed.
* `family_id` (string): Botanical family (e.g., "Fabaceae").
* `species_id` (string): Genus/Species (e.g., "Glycine_max").
* `plant_id` (string): Unique biological entity ID.
* `session_id` (string): Unique recording session ID.
* `hardware_id` (string): Electrode/Device type (e.g., "Needle_AgCl").
* `source_id` (string): Provenance dataset identifier.
* `window_start_ts` (datetime64[ns]): Start of the analysis window.
* `window_end_ts` (datetime64[ns]): End of the analysis window.
* `label_event_start_ts` (datetime64[ns]): Start of the stress intervention.
* `label_event_end_ts` (datetime64[ns]): End of the stress intervention.

## 1A. Schema Tiers (Normative)
To prevent ambiguity between preprocessing and model-ready artifacts, define two schema tiers:

### Tier A: `dataset_clean.parquet` (Preprocess Canonical)
Required columns:
* `timestamp_utc`, `value_uv`, `label`, `family_id`, `species_id`, `plant_id`, `session_id`, `hardware_id`, `source_id`, `window_start_ts`, `window_end_ts`, `label_event_start_ts`, `label_event_end_ts`
* `value_norm` is **optional** and **SHOULD be absent** by default.

### Tier B: `dataset_model_ready.parquet` (Model-Ready Canonical)
Required columns:
* All Tier A columns plus `value_norm`.
* `value_norm` is **REQUIRED**.

**Normalization Boundary:** `value_norm` MUST be fit on Train split statistics only, after split assignment, then applied to Val/Test.

**Note:** `tests/test_schema.py` must validate against Tier A for preprocessing outputs and Tier B for model-ready outputs.

## 2. Signal Quality Definitions
* **Unit Standardization (Mandatory):**
    * If source unit is mV, convert via `value_uv = value_mV * 1000`.
    * If source unit is V, convert via `value_uv = value_V * 1_000_000`.
    * Persist per-source conversion metadata in provenance (`source_unit`, `conversion_applied`, `scale_factor`).
* **Drift:** Defined in uV/s. Reject if linear slope > `drift_slope_max_uv_per_s`.
* **Flatline:** Reject if standard deviation < `flatline_std_min`.
* **SNR (Signal-to-Noise Ratio):**
    * $SNR_{dB} = 10 \log_{10}(\frac{P_{signal}}{P_{noise}})$
    * Reject if $SNR_{dB} < snr\_db\_min$.
* **Clip Fraction:** Reject if > `clip_fraction_max` of points are at sensor saturation limits.

## 3. Leakage Guard (CRITICAL)
* **Hierarchy Lock:** `family_id` -> `species_id` -> `plant_id` -> `session_id`.
* **Constraint:** Disjointness is required pairwise across all split pairs:
    * `plant_id`: train $\cap$ val = $\emptyset$, train $\cap$ test = $\emptyset$, val $\cap$ test = $\emptyset$
    * `session_id`: train $\cap$ val = $\emptyset$, train $\cap$ test = $\emptyset$, val $\cap$ test = $\emptyset$
* **Temporal Isolation:**
    * **Logic:** Build `feature_interval_expanded = [window_start_ts - label_event_gap_seconds, window_end_ts + label_event_gap_seconds]`.
    * **REQUIRED FAIL CHECKS:** Feature-vs-LabelEvent non-overlap across split pairs (train/val, train/test, val/test).
    * **DIAGNOSTIC ONLY:** Feature-vs-Feature overlap may be logged in `overlap_pairs` but MUST NOT be a fail condition by itself.

## 4. Artifact Outputs
The preprocessing pipeline must generate:
1.  `dataset_clean.parquet` (Tier A).
2.  `dataset_model_ready.parquet` (Tier B).
3.  `split_manifest.parquet`: Window-granular split assignment.
    * Columns: `source_id`, `plant_id`, `session_id`, `window_start_ts`, `window_end_ts`, `split`.
4.  `rejection_log.parquet`: Metadata of all rejected windows.
5.  `unit_conversion_report.json`: Per-source unit mapping and scale factors.
6.  `data_quality_report.json`:
    * `report_schema_version`: "1.0.0"
    * `leakage_checks`:
        * `status`: "PASS" | "FAIL"
        * `offending_ids`: List[String]
        * `overlap_pairs`: List[{left_id, right_id, left_split, right_split, overlap_seconds, overlap_type}]

---
Footer: Language pass applied: professional-safe | Consistency pass applied: schema/splits/artifacts aligned
