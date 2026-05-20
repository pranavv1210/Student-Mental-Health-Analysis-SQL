from __future__ import annotations

import pandas as pd

from config.settings import settings

RAW_TO_CANONICAL = {
    "Timestamp": "timestamp",
    "Choose your gender": "gender",
    "Age": "age",
    "What is your course?": "course",
    "Your current year of Study": "year_of_study",
    "What is your CGPA?": "cgpa_range",
    "Marital status": "marital_status",
    "Do you have Depression?": "depression",
    "Do you have Anxiety?": "anxiety",
    "Do you have Panic attack?": "panic_attack",
    "Did you seek any specialist for a treatment?": "sought_treatment",
}


def extract_csv(path: str | None = None) -> pd.DataFrame:
    csv_path = path or settings.csv_path
    return pd.read_csv(csv_path)