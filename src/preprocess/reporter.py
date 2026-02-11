import pandas as pd
import hashlib
from typing import Dict, Any
from src.preprocess.config import PreprocessConfig

class DataReporter:
    def __init__(self, config: PreprocessConfig):
        self.config = config
        self.dropped_null_rows = 0

    def set_extra_stats(self, dropped_null_rows: int):
        self.dropped_null_rows = dropped_null_rows

    def compute_leakage_checks(self, df: pd.DataFrame, manifest: pd.DataFrame) -> Dict[str, Any]:
        merge_keys = ["source_id", "plant_id", "session_id", "window_start_ts", "window_end_ts"]

        merged = pd.merge(
            df,
            manifest[merge_keys + ["split"]],
            on=merge_keys,
            how="inner"
        )

        leakage_status = "PASS"
        offending_ids = set()
        overlap_pairs = []

        gap = pd.Timedelta(seconds=self.config.label_event_gap_seconds)
        pairs = [("train", "val"), ("train", "test"), ("val", "test")]

        for split_a, split_b in pairs:
            df_a = merged[merged["split"] == split_a]
            df_b = merged[merged["split"] == split_b]
            if df_a.empty or df_b.empty:
                continue

            m_check = pd.merge(df_a, df_b, on=["source_id", "plant_id"], suffixes=("_a", "_b"))
            if not m_check.empty:
                feat_start_a = m_check["window_start_ts_a"] - gap
                feat_end_a = m_check["window_end_ts_a"] + gap
                lbl_start_b = m_check["label_event_start_ts_b"]
                lbl_end_b = m_check["label_event_end_ts_b"]

                overlap_mask = (feat_start_a < lbl_end_b) & (feat_end_a > lbl_start_b)

                if overlap_mask.any():
                    leakage_status = "FAIL"
                    bad_rows = m_check[overlap_mask]
                    offending_ids.update(bad_rows["plant_id"].astype(str).unique().tolist())

                    for _, row in bad_rows.iterrows():
                        overlap_pairs.append({
                            "left_id": str(row["window_start_ts_a"]),
                            "right_id": str(row["label_event_start_ts_b"]),
                            "left_split": split_a,
                            "right_split": split_b,
                            "overlap_seconds": 0.0,
                            "overlap_type": "feature_vs_label_event"
                        })

                feat_start_b = m_check["window_start_ts_b"]
                feat_end_b = m_check["window_end_ts_b"]
                overlap_mask_ff = (feat_start_a < feat_end_b) & (feat_end_a > feat_start_b)
                if overlap_mask_ff.any():
                    bad_rows_ff = m_check[overlap_mask_ff]
                    for _, row in bad_rows_ff.iterrows():
                        overlap_pairs.append({
                            "left_id": str(row["window_start_ts_a"]),
                            "right_id": str(row["window_start_ts_b"]),
                            "left_split": split_a,
                            "right_split": split_b,
                            "overlap_seconds": 0.0,
                            "overlap_type": "feature_vs_feature_diagnostic"
                        })

        return {
            "status": leakage_status,
            "offending_ids": list(offending_ids),
            "overlap_pairs": overlap_pairs
        }

    def generate_report(self, df_raw, df_clean, rejection_log, split_manifest, cleaner_stats, conversion_meta):
        canonical_cols = {
            "timestamp_utc", "value_uv", "label", "family_id", "species_id",
            "plant_id", "session_id", "hardware_id", "source_id",
            "window_start_ts", "window_end_ts", "label_event_start_ts", "label_event_end_ts"
        }
        missing_cols = canonical_cols - set(df_clean.columns)
        schema_errors = len(missing_cols)

        leakage = self.compute_leakage_checks(df_clean, split_manifest)

        return {
            "report_schema_version": "1.0.0",
            "schema_version": "1.0.6",
            "total_windows_processed": int(cleaner_stats.get("total_windows", 0)),
            "rejected_windows_count": int(cleaner_stats.get("rejected_windows", 0)),
            "rejection_reason_dist": cleaner_stats.get("reasons", {}),
            "rejection_rate_per_source": {
                k: v / len(df_raw[df_raw["source_id"] == k]) if len(df_raw[df_raw["source_id"] == k]) > 0 else 0
                for k, v in cleaner_stats.get("by_source", {}).items()
            },
            "class_balance_by_family_species": {
                str(k): int(v) for k, v in df_clean.groupby(["family_id", "species_id", "label"]).size().to_dict().items()
            },
            "harmonization_stats_by_source": {
                src: {"count": int(count)} for src, count in df_clean["source_id"].value_counts().items()
            },
            "schema_validation_errors_count": schema_errors,
            "dropped_null_rows": self.dropped_null_rows,
            "unit_conversion_summary": conversion_meta,
            "leakage_checks": leakage,
            "config_hash": hashlib.md5(str(self.config.model_dump()).encode()).hexdigest(),
            "seed": self.config.random_seed
        }
