from pathlib import Path

import kaggle

RAW_DIR = Path("data/raw")
DATASET_SLUG = "jtrotman/formula-1-race-data"


def download_dataset(dataset_slug: str, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(dataset_slug, path=str(output_dir), unzip=True)
    csv_files = sorted(output_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {output_dir}")
    return csv_files


if __name__ == "__main__":
    files = download_dataset(DATASET_SLUG, RAW_DIR)
    for f in files:
        print(f.name)
