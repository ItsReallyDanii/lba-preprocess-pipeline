import subprocess
import hashlib
from pathlib import Path
import yaml
import pandas as pd
import sys

def test_determinism_execution(tmp_path):
    raw_dir = tmp_path / "data/raw"
    processed_dir = tmp_path / "data/processed"
    reports_dir = tmp_path / "data/reports"
    raw_dir.mkdir(parents=True)

    ts = pd.Timestamp("2026-01-01 12:00:00", tz="UTC")
    df = pd.DataFrame([{
        "timestamp_utc": ts, "value": 1.0, "label": 0,
        "family_id": "f", "species_id": "s", "plant_id": "p", "session_id": "sess",
        "hardware_id": "h", "source_id": "src",
        "window_start_ts": ts, "window_end_ts": ts,
        "label_event_start_ts": ts, "label_event_end_ts": ts
    }])
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
