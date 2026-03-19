import zipfile
from src.utils.paths import RAW_DIR, EXTRACT_DIR


# extrai um zip de cada vez
def extrai_zip(zip_path):
    ano = zip_path.parent.name
    trimestre = zip_path.stem

    destino = EXTRACT_DIR / ano / trimestre
    destino.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(destino)
    except Exception as e:
        print(f"Erro, ignorando arquvivo: {e}\n")


# extrai todos os zips contidos em raw_dir
def extrair_todos():
    for zip_file in RAW_DIR.rglob("*.zip"):
        extrai_zip(zip_file)
