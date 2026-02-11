import subprocess
import hashlib
from pathlib import Path
import yaml
import pandas as pd
import numpy as np
import sys

def test_determinism_execution(tmp_path):
    raw_dir = tmp_path / "data/raw"
    processed_dir = tmp_path / "data/processed"
    reports_dir = tmp_path / "data/reports"
    raw_dir.mkdir(parents=True)

    # Generate synthetic window with multiple samples to pass quality gates
    # Window: 10 seconds with 100 samples (10 Hz sampling rate)
    ts_start = pd.Timestamp("2026-01-01 12:00:00", tz="UTC")
    ts_end = ts_start + pd.Timedelta(seconds=10)
    label_start = ts_start + pd.Timedelta(seconds=30)
    label_end = label_start + pd.Timedelta(seconds=5)
    
    # Create 100 samples with small random variation to pass all gates:
    # - variance > 1e-6 (flatline check)
    # - low drift (< 10 µV/s)
    # - good SNR (> 3 dB)
    # - no clipping (values well within -10000 to 10000 range)
    np.random.seed(42)
    num_samples = 100
    base_value = 100.0
    noise = np.random.normal(0, 5.0, num_samples)  # std=5 >> 1e-6
    values = base_value + noise  # Mean ~100, std ~5
    
    # Create time series for each sample
    time_deltas = [pd.Timedelta(seconds=i * 0.1) for i in range(num_samples)]
    timestamps = [ts_start + td for td in time_deltas]
    
    # Build DataFrame with one row per sample
    rows = []
    for i in range(num_samples):
        rows.append({
            "timestamp_utc": timestamps[i],
            "value": values[i],
            "label": 0,
            "family_id": "f",
            "species_id": "s",
            "plant_id": "p",
            "session_id": "sess",
            "hardware_id": "h",
            "source_id": "src",
            "window_start_ts": ts_start,
            "window_end_ts": ts_end,
            "label_event_start_ts": label_start,
            "label_event_end_ts": label_end
        })
    
    df = pd.DataFrame(rows)
    df.to_parquet(raw_dir / "input.parquet")

    config_path = tmp_path / "preprocess.yaml"
    with open(config_path, "w") as f:
        yaml.dump({"random_seed": 42}, f)

    cmd = [
        sys.executable, "-m", "src.preprocess.main",
        "--config", str(config_path),
        "--raw-dir", str(raw_dir),
        "--processed-dir", str(processed_dir),
        "--reports-dir", str(reports_dir)
    ]

    subprocess.check_call(cmd)
    f1 = processed_dir / "dataset_clean.parquet"
    h1 = hashlib.sha256(f1.read_bytes()).hexdigest()

    f1.unlink()
    subprocess.check_call(cmd)
    h2 = hashlib.sha256(f1.read_bytes()).hexdigest()

    assert h1 == h2
