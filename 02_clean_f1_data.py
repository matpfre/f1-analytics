import re
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")

CORE_TABLES = [
    "circuits",
    "constructors",
    "drivers",
    "races",
    "results",
    "status",
    "driver_standings",
    "constructor_standings",
    "lap_times",
    "pit_stops",
]


def to_snake_case(column: str) -> str:
    column = re.sub(r"(?<!^)(?=[A-Z])", "_", column)
    return column.lower()


def load_raw_table(name: str) -> pd.DataFrame:
    path = RAW_DIR / f"{name}.csv"
    df = pd.read_csv(path, na_values=["\\N"])
    df.columns = [to_snake_case(c) for c in df.columns]
    return df


def clean_races(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def clean_results(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    numeric_cols = ["position", "points", "laps", "milliseconds", "fastest_lap", "rank"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_lap_times(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["milliseconds"] = pd.to_numeric(df["milliseconds"], errors="coerce")
    df = df.dropna(subset=["milliseconds"])
    return df


CLEANERS = {
    "races": clean_races,
    "results": clean_results,
    "lap_times": clean_lap_times,
}


def clean_table(name: str, df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates()
    cleaner = CLEANERS.get(name)
    if cleaner:
        df = cleaner(df)
    return df


if __name__ == "__main__":
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    for table_name in CORE_TABLES:
        raw_df = load_raw_table(table_name)
        clean_df = clean_table(table_name, raw_df)
        clean_df.to_csv(CLEAN_DIR / f"{table_name}.csv", index=False)
        print(f"{table_name}: {len(raw_df)} -> {len(clean_df)} linhas")
