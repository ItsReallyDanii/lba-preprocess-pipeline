import pandas as pd
import hashlib
from src.preprocess.config import PreprocessConfig

class DataSplitter:
    def __init__(self, config: PreprocessConfig):
        self.config = config

    def _get_split_group(self, family: str, species: str, plant: str) -> str:
        key = f"{family}_{species}_{plant}"
        h = hashlib.md5(f"{key}{self.config.random_seed}".encode()).hexdigest()
        val = int(h, 16) % 100
        if val < 70:
            return "train"
        elif val < 85:
            return "val"
        else:
            return "test"

    def split_data(self, df: pd.DataFrame) -> pd.DataFrame:
        entities = df[["family_id", "species_id", "plant_id"]].drop_duplicates()

        plant_splits = {}
        for _, row in entities.iterrows():
            split = self._get_split_group(row["family_id"], row["species_id"], row["plant_id"])
            plant_splits[row["plant_id"]] = split

        splits = df["plant_id"].map(plant_splits).fillna("train")
        split_manifest = df[["source_id", "plant_id", "session_id", "window_start_ts", "window_end_ts"]].copy()
        split_manifest["split"] = splits

        for a, b in [("train", "val"), ("train", "test"), ("val", "test")]:
            ids_a = set(split_manifest[split_manifest["split"] == a]["session_id"])
            ids_b = set(split_manifest[split_manifest["split"] == b]["session_id"])
            assert ids_a.isdisjoint(ids_b), f"Session Leakage detected between {a} and {b}"

            p_a = set(split_manifest[split_manifest["split"] == a]["plant_id"])
            p_b = set(split_manifest[split_manifest["split"] == b]["plant_id"])
            assert p_a.isdisjoint(p_b), f"Plant Leakage detected between {a} and {b}"

        return split_manifest
