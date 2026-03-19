from src.pipeline import downloader
from src.pipeline import extractor
from src.pipeline import parser


def main():
    print("DOWNLOADER\n")
    downloader.baixar_periodos(2025, 2026)
    downloader.baixar_cadastro()

    print("EXTRACTOR\n")
    extractor.extrair_todos()

    print("PARSER\n")
    parser.procesar_todos()


main()
