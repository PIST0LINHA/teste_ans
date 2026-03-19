from src.pipeline import downloader
from src.pipeline import extractor
from src.pipeline import parser
from src.pipeline import validador


def main():
    downloader.baixar_periodos(2025, 2026)
    downloader.baixar_cadastro()

    extractor.extrair_todos()

    parser.procesar_todos()

    # quebra o padrao de coesao sequencial...
    validador.executar_validacao(
        "data/final/consolidado.csv", "data/cadastro/Relatorio_cadop.csv", "data/final"
    )


main()
