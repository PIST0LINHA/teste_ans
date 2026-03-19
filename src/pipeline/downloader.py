import requests
from src.utils.paths import RAW_DIR, CADASTRO_DIR

# configuracoes
api_url = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis"
cadastro_url = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
headers = {"User-Agent": "Mozilla/5.0"}


# baixa apenas um arquivo de cada vez
def download_unico(url, destino):
    # faz um get request para a url fornecida usando headers preconfigurados
    try:
        with requests.get(url, headers=headers, stream=True, timeout=10) as resposta:
            resposta.raise_for_status()

            # checa se o arquivo tiver algo
            total_bytes = 0

            # faz o download dos arquivos
            with open(destino, "wb") as f:
                # tecnicamente mais eficiente, mas 8kb tambem esta ok
                for chunk in resposta.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        total_bytes += len(chunk)

            # ignora arquivos vazios
            if total_bytes == 0:
                print(f"Arquivo vazio, removendo {url}")
                destino.unlink(missing=True)
                return

            print(f"Download concluido: {destino}\n")

    # mostra a url e o erro recebido caso nao consiga baixar um arquivo
    except Exception as e:
        print(f"Falha ao baixar {url}: {e}\n")


# baixa periodos inteiros
def baixar_periodos(ano_inicio, ano_fim):
    for ano in range(ano_inicio, ano_fim + 1):
        # separa por ano
        pasta_ano = RAW_DIR / str(ano)
        pasta_ano.mkdir(exist_ok=True)

        for trimestre in range(1, 5):
            # define caminhos para os downloads
            nome_arquivo = f"{trimestre}T{ano}.zip"
            url = f"{api_url}/{ano}/{nome_arquivo}"
            destino = pasta_ano / nome_arquivo

            # pula arquivo caso ja exista
            if destino.exists():
                print(f"Arquivo já existe: {destino}\n")
                continue

            print(f"Baixando {url}")
            download_unico(url, destino)


# para baixar o cadastro de empresas ativas
def baixar_cadastro():
    destino = CADASTRO_DIR / "Relatorio_cadop.csv"

    # evita baixar de novo
    if destino.exists() and destino.stat().st_size > 0:
        print(f"Cadastro já existe: {destino}")
        return destino

    print("Baixando cadastro ANS...")
    download_unico(cadastro_url, destino)

    return destino
