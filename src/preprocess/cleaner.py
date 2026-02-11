import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any
from src.preprocess.config import PreprocessConfig

class DataCleaner:
    def __init__(self, config: PreprocessConfig):
        self.config = config
        self.stats = {
            "total_windows": 0,
            "rejected_windows": 0,
            "reasons": {},
            "by_source": {}
        }

    def _check_clip_fraction(self, signal: np.ndarray) -> bool:
        if len(signal) == 0:
            return False
        min_rail = self.config.sensor_min_val
        max_rail = self.config.sensor_max_val
        clipped_count = np.sum((signal <= min_rail) | (signal >= max_rail))
        fraction = clipped_count / len(signal)
        return fraction > self.config.clip_fraction_max

    def _check_drift(self, signal: np.ndarray, duration_s: float) -> bool:
        if duration_s <= 0:
            return False
        x = np.arange(len(signal))
        slope = np.polyfit(x, signal, 1)[0]
        fs = self.config.target_hz
        slope_uv_s = slope * fs
        return abs(slope_uv_s) > self.config.drift_slope_max_uv_per_s

    def _check_flatline(self, signal: np.ndarray) -> bool:
        return np.std(signal) < self.config.flatline_std_min

    def _check_snr(self, signal: np.ndarray) -> bool:
        p_signal = np.var(signal)
        p_noise = np.var(np.diff(signal)) + 1e-9
        if p_noise == 0:
            return False
        snr = 10 * np.log10(p_signal / p_noise)
        return snr < self.config.snr_db_min

    def run(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        self.stats["total_windows"] = len(df)
        conversion_meta = {}

        if "source_id" in df.columns and self.config.source_scaling:
            df["scale_factor"] = df["source_id"].map(self.config.source_scaling).fillna(1.0)
            df["value_uv"] = df["value"] * df["scale_factor"]
            for src, factor in self.config.source_scaling.items():
                conversion_meta[src] = {"scale_factor": factor}
        else:
            df["value_uv"] = df["value"]
            conversion_meta["default"] = {"scale_factor": 1.0}

        clean_rows = []
        rejected_rows = []

        grouped = df.groupby(["source_id", "plant_id", "session_id", "window_start_ts"])

        for _, group in grouped:
            signal = group["value_uv"].values
            duration = (group["window_end_ts"].iloc[0] - group["window_start_ts"].iloc[0]).total_seconds()

            rejection_reason = None
            if self._check_flatline(signal):
                rejection_reason = "flatline"
            elif self._check_drift(signal, duration):
                rejection_reason = "drift"
            elif self._check_snr(signal):
                rejection_reason = "snr"
            elif self._check_clip_fraction(signal):
                rejection_reason = "clip"

            if rejection_reason:
                self.stats["rejected_windows"] += 1
                self.stats["reasons"][rejection_reason] = self.stats["reasons"].get(rejection_reason, 0) + 1
                src = group["source_id"].iloc[0]
                self.stats["by_source"][src] = self.stats["by_source"].get(src, 0) + 1
                meta = group.iloc[0].to_dict()
                meta["rejection_reason"] = rejection_reason
                rejected_rows.append(meta)
            else:
                clean_rows.append(group)

        if clean_rows:
            df_clean = pd.concat(clean_rows).reset_index(drop=True)
        else:
            df_clean = pd.DataFrame(columns=df.columns)

        if rejected_rows:
            rejection_log = pd.DataFrame(rejected_rows)
        else:
            rejection_log = pd.DataFrame(columns=["session_id", "window_start_ts", "rejection_reason"])

        return df_clean, rejection_log, conversion_meta
