import os
import argparse
import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

CLEAN_DIR = Path("data/clean")

LOAD_ORDER = [
    "circuits",
    "constructors",
    "drivers",
    "seasons",
    "status",
    "races",
    "results",
    "constructor_results",
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

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)


def get_engine():
    connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING")
    if not connection_string:
        raise RuntimeError("AZURE_SQL_CONNECTION_STRING não foi configurada")
    return create_engine(connection_string, fast_executemany=True)


def read_clean_table(name: str) -> pd.DataFrame:
    path = CLEAN_DIR / f"{name}.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo tratado não encontrado: {path}")
    df = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS[name] - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"{path} não contém as colunas obrigatórias: {missing}")
    if df.columns.duplicated().any():
        raise ValueError(f"{path} contém nomes de colunas duplicados")
    return df


def load_tables(engine, replace: bool) -> dict[str, int]:
    tables = {name: read_clean_table(name) for name in LOAD_ORDER}
    if_exists = "replace" if replace else "fail"
    row_counts = {}
    with engine.begin() as connection:
        for name, df in tables.items():
            df.to_sql(name, connection, if_exists=if_exists, index=False, chunksize=1000)
            row_counts[name] = len(df)
    return row_counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Carrega as tabelas tratadas no Azure SQL")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="substitui tabelas existentes; sem esta opção, a carga falha se elas já existirem",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    engine = get_engine()
    for table_name, row_count in load_tables(engine, replace=args.replace).items():
        LOGGER.info("%s: %s linhas carregadas", table_name, row_count)
