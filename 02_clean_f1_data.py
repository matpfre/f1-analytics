import re
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")

CORE_TABLES = [
    "circuits",
    "constructors",
    "drivers",
    "seasons",
    "races",
    "results",
    "constructor_results",
    "status",
    "driver_standings",
    "constructor_standings",
    "qualifying",
    "sprint_results",
    "lap_times",
    "pit_stops",
]

REQUIRED_COLUMNS = {
    "circuits": {"circuit_id", "name"},
    "constructors": {"constructor_id", "name"},
    "drivers": {"driver_id", "forename", "surname"},
    "seasons": {"year", "url"},
    "races": {"race_id", "year", "circuit_id", "date"},
    "results": {"result_id", "race_id", "driver_id", "constructor_id"},
    "constructor_results": {"constructor_results_id", "race_id", "constructor_id"},
    "status": {"status_id", "status"},
    "driver_standings": {"driver_standings_id", "race_id", "driver_id"},
    "constructor_standings": {"constructor_standings_id", "race_id", "constructor_id"},
    "qualifying": {"qualify_id", "race_id", "driver_id", "constructor_id"},
    "sprint_results": {"result_id", "race_id", "driver_id", "constructor_id"},
    "lap_times": {"race_id", "driver_id", "lap", "milliseconds"},
    "pit_stops": {"race_id", "driver_id", "stop", "milliseconds"},
}


def to_snake_case(column: str) -> str:
    column = re.sub(r"(?<!^)(?=[A-Z])", "_", column)
    return column.lower()


def load_raw_table(name: str) -> pd.DataFrame:
    path = RAW_DIR / f"{name}.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo obrigatório não encontrado: {path}")
    df = pd.read_csv(path, na_values=["\\N"])
    df.columns = [to_snake_case(c) for c in df.columns]
    missing_columns = REQUIRED_COLUMNS[name] - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"{path} não contém as colunas obrigatórias: {missing}")
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


def clean_numeric_fields(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_lap_times(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["milliseconds"] = pd.to_numeric(df["milliseconds"], errors="coerce")
    df = df.dropna(subset=["milliseconds"])
    return df


def clean_drivers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["dob"] = pd.to_datetime(df["dob"], errors="coerce")
    return df


CLEANERS = {
    "drivers": clean_drivers,
    "races": clean_races,
    "results": clean_results,
    "constructor_results": lambda df: clean_numeric_fields(df, ["points"]),
    "driver_standings": lambda df: clean_numeric_fields(df, ["points", "position", "wins"]),
    "constructor_standings": lambda df: clean_numeric_fields(df, ["points", "position", "wins"]),
    "qualifying": lambda df: clean_numeric_fields(df, ["number", "position"]),
    "sprint_results": lambda df: clean_numeric_fields(
        df, ["number", "grid", "position", "position_order", "points", "laps", "milliseconds", "fastest_lap", "rank"]
    ),
    "lap_times": clean_lap_times,
    "pit_stops": lambda df: clean_numeric_fields(df, ["stop", "lap", "milliseconds"]),
}


def clean_table(name: str, df: pd.DataFrame) -> pd.DataFrame:
    cleaner = CLEANERS.get(name)
    if cleaner:
        df = cleaner(df)
    return df.drop_duplicates().reset_index(drop=True)


if __name__ == "__main__":
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    for table_name in CORE_TABLES:
        raw_df = load_raw_table(table_name)
        clean_df = clean_table(table_name, raw_df)
        clean_df.to_csv(CLEAN_DIR / f"{table_name}.csv", index=False)
        print(f"{table_name}: {len(raw_df)} -> {len(clean_df)} linhas")
