from pathlib import Path

BASE_DIR = Path.cwd()

RAW_DIR = BASE_DIR / "data" / "raw_data"
EXTRACT_DIR = BASE_DIR / "data" / "extracted"
CADASTRO_DIR = BASE_DIR / "data" / "cadastro"

RAW_DIR.mkdir(parents=True, exist_ok=True)
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
CADASTRO_DIR.mkdir(parents=True, exist_ok=True)
