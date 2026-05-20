from __future__ import annotations

import pandas as pd

from etl.transform import transform


def test_transform_core_columns() -> None:
    raw = pd.DataFrame(
        {
            "Timestamp": ["8/7/2020 12:02"],
            "Choose your gender": ["Female"],
            "Age": [18],
            "What is your course?": ["Engineering"],
            "Your current year of Study": ["year 1"],
            "What is your CGPA?": ["3.00 - 3.49"],
            "Marital status": ["No"],
            "Do you have Depression?": ["Yes"],
            "Do you have Anxiety?": ["No"],
            "Do you have Panic attack?": ["Yes"],
            "Did you seek any specialist for a treatment?": ["No"],
        }
    )

    out = transform(raw)
    assert out.shape[0] == 1
    assert out.loc[0, "depression"] == 1
    assert out.loc[0, "anxiety"] == 0
    assert out.loc[0, "year_of_study"] == 1
    assert len(out.loc[0, "record_hash"]) == 64