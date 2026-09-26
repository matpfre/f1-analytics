import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

CLEAN_DIR = Path("data/clean")

LOAD_ORDER = [
    "circuits",
    "constructors",
    "drivers",
    "status",
    "races",
    "results",
    "driver_standings",
    "constructor_standings",
    "lap_times",
    "pit_stops",
]


def get_engine():
    connection_string = os.environ["AZURE_SQL_CONNECTION_STRING"]
    return create_engine(connection_string, fast_executemany=True)


def load_table(engine, name: str) -> int:
    df = pd.read_csv(CLEAN_DIR / f"{name}.csv")
    df.to_sql(name, engine, if_exists="replace", index=False, chunksize=1000)
    return len(df)


if __name__ == "__main__":
    engine = get_engine()
    for table_name in LOAD_ORDER:
        row_count = load_table(engine, table_name)
        print(f"{table_name}: {row_count} linhas carregadas")
