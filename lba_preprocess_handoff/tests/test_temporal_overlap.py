import pandas as pd
from src.preprocess.config import PreprocessConfig
from src.preprocess.reporter import DataReporter

def test_temporal_overlap_fail_check():
    config = PreprocessConfig(label_event_gap_seconds=5, random_seed=42)
    ts_base = pd.Timestamp("2026-01-01 12:00:00", tz="UTC")

    df = pd.DataFrame([
        {
            "session_id": "s1", "plant_id": "p1", "source_id": "src",
            "window_start_ts": ts_base,
            "window_end_ts": ts_base + pd.Timedelta(seconds=60),
            "label_event_start_ts": ts_base + pd.Timedelta(seconds=60),
            "label_event_end_ts": ts_base + pd.Timedelta(seconds=120)
        },
        {
            "session_id": "s1", "plant_id": "p1", "source_id": "src",
            "window_start_ts": ts_base + pd.Timedelta(seconds=1000),
            "window_end_ts": ts_base + pd.Timedelta(seconds=1060),
            "label_event_start_ts": ts_base + pd.Timedelta(seconds=60),
            "label_event_end_ts": ts_base + pd.Timedelta(seconds=120)
        }
    ])

    manifest = pd.DataFrame([
        {
            "source_id": "src", "plant_id": "p1", "session_id": "s1",
            "window_start_ts": ts_base, "window_end_ts": ts_base + pd.Timedelta(seconds=60),
            "split": "train"
        },
        {
            "source_id": "src", "plant_id": "p1", "session_id": "s1",
            "window_start_ts": ts_base + pd.Timedelta(seconds=1000),
            "window_end_ts": ts_base + pd.Timedelta(seconds=1060),
            "split": "test"
        }
    ])

    reporter = DataReporter(config)
    checks = reporter.compute_leakage_checks(df, manifest)
    assert checks["status"] == "FAIL"
    assert "p1" in checks["offending_ids"]

def test_temporal_overlap_pass_check():
    config = PreprocessConfig(label_event_gap_seconds=5, random_seed=42)
    ts_base = pd.Timestamp("2026-01-01 12:00:00", tz="UTC")

    df = pd.DataFrame([
        {
            "session_id": "s1", "plant_id": "p1", "source_id": "src",
            "window_start_ts": "2026-01-01T12:00:00Z",
            "window_end_ts": "2026-01-01T12:01:00Z",
            "label_event_start_ts": "2026-01-01T12:20:00Z",
            "label_event_end_ts": "2026-01-01T12:21:00Z"
        },
        {
            "session_id": "s1", "plant_id": "p1", "source_id": "src",
            "window_start_ts": "2026-01-01T12:40:00Z",
            "window_end_ts": "2026-01-01T12:41:00Z",
            "label_event_start_ts": "2026-01-01T12:20:00Z",
            "label_event_end_ts": "2026-01-01T12:21:00Z"
        }
    ])
    for c in ["window_start_ts","window_end_ts","label_event_start_ts","label_event_end_ts"]:
        df[c] = pd.to_datetime(df[c], utc=True)

    manifest = pd.DataFrame([
        {"source_id":"src","plant_id":"p1","session_id":"s1","window_start_ts":pd.to_datetime("2026-01-01T12:00:00Z"),"window_end_ts":pd.to_datetime("2026-01-01T12:01:00Z"),"split":"train"},
        {"source_id":"src","plant_id":"p1","session_id":"s1","window_start_ts":pd.to_datetime("2026-01-01T12:40:00Z"),"window_end_ts":pd.to_datetime("2026-01-01T12:41:00Z"),"split":"test"},
    ])

    reporter = DataReporter(config)
    checks = reporter.compute_leakage_checks(df, manifest)
    assert checks["status"] == "PASS"
    assert len(checks["offending_ids"]) == 0
