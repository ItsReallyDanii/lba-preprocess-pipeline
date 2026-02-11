import argparse
import logging
import sys
import yaml
import pandas as pd
import numpy as np
from pathlib import Path

from src.preprocess.config import PreprocessConfig, load_config
from src.preprocess.cleaner import DataCleaner
from src.preprocess.splitter import DataSplitter
from src.preprocess.reporter import DataReporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    ts_cols = [
        "timestamp_utc", "window_start_ts", "window_end_ts",
        "label_event_start_ts", "label_event_end_ts"
    ]
    for col in ts_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors="raise", utc=True)
            except Exception as e:
                logger.error(f"Failed to parse timestamp column {col}: {e}")
                sys.exit(1)
    return df

def main():
    parser = argparse.ArgumentParser(description="LBA Preprocessing Pipeline")
    parser.add_argument("--config", type=str, required=True, help="Path to preprocess.yaml")
    parser.add_argument("--raw-dir", type=str, default="data/raw", help="Input directory")
    parser.add_argument("--processed-dir", type=str, default="data/processed", help="Output directory")
    parser.add_argument("--reports-dir", type=str, default="data/reports", help="Reports directory")
    args = parser.parse_args()

    try:
        config_path = Path(args.config)
        config: PreprocessConfig = load_config(config_path)
    except Exception as e:
        logger.error(f"Config load failed: {e}")
        sys.exit(1)

    raw_dir = Path(args.raw_dir)
    processed_dir = Path(args.processed_dir)
    reports_dir = Path(args.reports_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    all_dfs = []
    input_files = sorted(list(raw_dir.glob("*.parquet")) + list(raw_dir.glob("*.csv")))
    if not input_files:
        logger.error(f"No input files found in {raw_dir}")
        sys.exit(1)

    initial_null_count = 0
    for f in input_files:
        try:
            df = pd.read_parquet(f) if f.suffix == ".parquet" else pd.read_csv(f)
            len_before = len(df)
            df = df.dropna(how="any")
            initial_null_count += (len_before - len(df))
            all_dfs.append(df)
        except Exception as e:
            logger.error(f"Failed to load {f}: {e}")
            sys.exit(1)

    df_raw = pd.concat(all_dfs, ignore_index=True)
    df_raw = parse_timestamps(df_raw)

    cleaner = DataCleaner(config)
    df_clean, rejection_log, conversion_meta = cleaner.run(df_raw)

    splitter = DataSplitter(config)
    split_manifest = splitter.split_data(df_clean)

    reporter = DataReporter(config)
    reporter.set_extra_stats(dropped_null_rows=initial_null_count)
    quality_report = reporter.generate_report(
        df_raw, df_clean, rejection_log, split_manifest, cleaner.stats, conversion_meta
    )

    df_clean.to_parquet(processed_dir / "dataset_clean.parquet", index=False)

    merge_keys = ["source_id", "plant_id", "session_id", "window_start_ts", "window_end_ts"]
    df_merged = pd.merge(
        df_clean,
        split_manifest[merge_keys + ["split"]],
        on=merge_keys,
        how="left"
    )

    train_vals = df_merged[df_merged["split"] == "train"]["value_uv"].values
    if len(train_vals) > 0:
        mean = np.mean(train_vals)
        std = np.std(train_vals)
        if std == 0:
            std = 1.0
    else:
        mean, std = 0.0, 1.0

    df_merged["value_norm"] = (df_merged["value_uv"] - mean) / std
    cols_tier_b = list(df_clean.columns) + ["value_norm"]
    df_merged[cols_tier_b].to_parquet(processed_dir / "dataset_model_ready.parquet", index=False)

    split_manifest.to_parquet(processed_dir / "split_manifest.parquet", index=False)
    rejection_log.to_parquet(processed_dir / "rejection_log.parquet", index=False)

    import json
    with open(reports_dir / "data_quality_report.json", "w") as f:
        json.dump(quality_report, f, indent=2, default=str)
    with open(reports_dir / "unit_conversion_report.json", "w") as f:
        json.dump(conversion_meta, f, indent=2)
    with open(processed_dir / "config_snapshot.yaml", "w") as f:
        yaml.dump(config.model_dump(), f)

    if quality_report["leakage_checks"]["status"] == "FAIL":
        logger.error("GATE 0 FAILURE: Leakage detected.")
        sys.exit(1)

    for src, rate in quality_report.get("rejection_rate_per_source", {}).items():
        if rate > config.max_rejection_rate_per_source:
            logger.error(f"GATE 0 FAILURE: Rejection rate {src}={rate:.2f} > limit")
            sys.exit(1)

    logger.info("Preprocessing completed successfully.")

if __name__ == "__main__":
    main()
