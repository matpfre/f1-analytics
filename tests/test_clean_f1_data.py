import importlib.util
from pathlib import Path

import pandas as pd


MODULE_PATH = Path(__file__).parents[1] / "02_clean_f1_data.py"
SPEC = importlib.util.spec_from_file_location("clean_f1_data", MODULE_PATH)
clean_f1_data = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(clean_f1_data)


def test_to_snake_case_converts_camel_case():
    assert clean_f1_data.to_snake_case("fastestLapSpeed") == "fastest_lap_speed"


def test_clean_results_converts_numeric_values():
    raw = pd.DataFrame(
        {
            "position": ["1", "\\N"],
            "points": ["25", "0"],
            "laps": ["58", "0"],
        }
    )

    cleaned = clean_f1_data.clean_results(raw)

    assert cleaned["position"].iloc[0] == 1.0
    assert pd.isna(cleaned["position"].iloc[1])
    assert cleaned["points"].tolist() == [25, 0]


def test_clean_lap_times_removes_rows_without_milliseconds():
    raw = pd.DataFrame(
        {
            "race_id": [1, 1],
            "driver_id": [1, 1],
            "lap": [1, 2],
            "milliseconds": ["102085", "\\N"],
        }
    )

    cleaned = clean_f1_data.clean_lap_times(raw)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["milliseconds"] == 102085


def test_clean_table_removes_duplicates():
    raw = pd.DataFrame({"year": [2024, 2024], "url": ["url", "url"]})

    cleaned = clean_f1_data.clean_table("seasons", raw)

    assert len(cleaned) == 1
