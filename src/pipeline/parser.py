import pandas as pd

from src.utils.paths import CADASTRO_DIR, EXTRACT_DIR, BASE_DIR


def ler_arquivo(file_path):
    try:
        if file_path.suffix in [".csv", ".txt"]:
            return pd.read_csv(file_path, sep=";", encoding="latin1", low_memory=False)

        elif file_path.suffix == [".xlsx", ".xls"]:
            return pd.read_excel(file_path)

        else:
            return None

    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}\n")
        return None


def checa_despesas(texto):
    # checa pra ver se o texto eh uma string
    if not isinstance(texto, str):
        return None

    texto = texto.lower()

    # força bruta mas funciona
    return (
        "despesas" in texto
        and "eventos" in texto
        and "sinistro" in texto
        and "sinistros" in texto
    )


# func auxiliar para mudar o separador de numeros reais
def to_float(col):
    return (
        col.astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".")
        .pipe(pd.to_numeric, errors="coerce")
    )


def processar_arquivo(file_path):
    # df de dataframe
    df = ler_arquivo(file_path)
    if df is None:
        return None

    # normaliza colunas com as infos disponiveis nos csvs extraidos
    df.columns = [c.lower().strip() for c in df.columns]

    colunas_necessarias = ["reg_ans", "descricao", "vl_saldo_inicial", "vl_saldo_final"]

    if not all(col in df.columns for col in colunas_necessarias):
        print(f"Arquivo ignorado: {file_path}\n")
        return None

    # checa descricao pra ver se cita sinistros e/ou eventos
    df_filtrado = df[df["descricao"].apply(checa_despesas)].copy()

    if df_filtrado is None:
        print(f"Arquivo ignorado: {file_path}\n")
        return None

    # calcula diferenca entre valor final e inicial
    df_filtrado["ValorDespesas"] = to_float(df_filtrado["vl_saldo_final"]) - to_float(
        df_filtrado["vl_saldo_inicial"]
    )

    for parte in file_path.parts:
        if "T" in parte:
            df_filtrado["Trimestre"] = parte[0]
            df_filtrado["Ano"] = parte[2:]
            break

    return df_filtrado[["reg_ans", "Trimestre", "Ano", "ValorDespesas"]]


# carrega o cadastro de empresas ativas da ans
def carregar_cadastro():
    # carrega e normaliza csv do cadastro
    df = pd.read_csv(
        CADASTRO_DIR / "Relatorio_cadop.csv",
        sep=";",
        encoding="latin1",
        low_memory=False,
    )
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

    colunas_necessarias = ["registro_operadora", "cnpj", "razao_social"]
    if not all(col in df.columns for col in colunas_necessarias):
        raise ValueError(f"Colunas esperadas não encontradas: {df.columns.tolist()}")

    df["registro_operadora"] = df["registro_operadora"].astype(str).str.strip()
    df["cnpj"] = df["cnpj"].astype(str).str.strip()
    df["razao_social"] = df["razao_social"].astype(str).str.strip()
    df = df.drop_duplicates(subset="registro_operadora")

    return df


# junta as duas tabelas csv em uma so
def enriquecer_dados(df_dados, cadastro):
    df_dados["reg_ans"] = df_dados["reg_ans"].astype(str).str.strip()
    df_final = df_dados.merge(
        cadastro, left_on="reg_ans", right_on="registro_operadora", how="inner"
    )

    df_final = df_final[["cnpj", "razao_social", "Trimestre", "Ano", "ValorDespesas"]]

    return df_final


def procesar_todos():
    resultados = []

    for file_path in EXTRACT_DIR.rglob("*"):
        print(f"Acessando pasta: {file_path}\n")
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() in [".csv", ".txt", ".xlsx", ".xls"]:
            print(f"Processando arquivo: {file_path}\n")

            df = processar_arquivo(file_path)

            if df is not None:
                resultados.append(df)

    if not resultados:
        print("Nenhum arquivo valido\n")
        return None

    df_final = pd.concat(resultados, ignore_index=True)

    cadastro = carregar_cadastro()
    df_final = enriquecer_dados(df_final, cadastro)

    df_final = df_final[["cnpj", "razao_social", "Trimestre", "Ano", "ValorDespesas"]]
    df_final = pd.DataFrame(df_final)

    df_final.to_csv(f"{BASE_DIR}/{'data'}/{'final'}/consolidado.csv", index=False)
    return df_final
