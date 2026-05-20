from __future__ import annotations

import hashlib

import pandas as pd

from etl.extract import RAW_TO_CANONICAL

YES_NO_MAP = {"Yes": 1, "No": 0}


def _normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=RAW_TO_CANONICAL).copy()

    required_cols = set(RAW_TO_CANONICAL.values())
    missing = required_cols.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = df.dropna(subset=["age", "timestamp", "year_of_study"])
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df = df.dropna(subset=["age"])
    df["age"] = df["age"].astype(int)
    df = df[(df["age"] >= 15) & (df["age"] <= 60)]

    for col in ["depression", "anxiety", "panic_attack", "sought_treatment"]:
        df[col] = df[col].map(YES_NO_MAP)
    if df[["depression", "anxiety", "panic_attack", "sought_treatment"]].isna().any().any():
        raise ValueError("Unexpected values in Yes/No columns.")

    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["year_of_study"] = (
        df["year_of_study"].astype(str).str.extract(r"(\d+)")[0].astype(float)
    )
    df = df.dropna(subset=["year_of_study"])
    df["year_of_study"] = df["year_of_study"].astype(int)

    def build_row_hash(row: pd.Series) -> str:
        key = "|".join(
            [
                str(row["timestamp"]),
                _normalize_text(row["gender"]),
                str(row["age"]),
                _normalize_text(row["course"]),
                str(row["year_of_study"]),
                _normalize_text(row["cgpa_range"]),
            ]
        )
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    df["record_hash"] = df.apply(build_row_hash, axis=1)
    return df.reset_index(drop=True)