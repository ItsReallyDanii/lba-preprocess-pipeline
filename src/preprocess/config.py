from pydantic import BaseModel, Field
from typing import Dict
from pathlib import Path
import yaml

class PreprocessConfig(BaseModel):
    class Config:
        extra = "forbid"

    target_hz: int = 10
    window_seconds: int = 60
    stride_seconds: int = 10
    label_event_gap_seconds: int = 10

    flatline_std_min: float = 1e-6
    drift_slope_max_uv_per_s: float = 10.0
    snr_db_min: float = 3.0

    sensor_min_val: float = -10000.0
    sensor_max_val: float = 10000.0
    clip_fraction_max: float = 0.05

    max_rejection_rate_per_source: float = 0.30
    min_samples_per_family: int = 100
    min_samples_per_species: int = 50
    random_seed: int = 42

    source_scaling: Dict[str, float] = Field(default_factory=dict)

def load_config(path: Path) -> PreprocessConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return PreprocessConfig(**data)
