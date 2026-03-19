import pandas as pd
import re
from pathlib import Path


# procura substring q nao eh numero e substitui por nada
def limpar_cnpj(cnpj):
    return re.sub(r"\D", "", str(cnpj))


# checa se cnpj tem 14 numeros e digito validador bate
def validar_cnpj(cnpj):
    cnpj = limpar_cnpj(cnpj)

    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def calcular_digito(cnpj, pesos):
        soma = sum(int(dig) * peso for dig, peso in zip(cnpj, pesos))
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1

    dig1 = calcular_digito(cnpj[:12], pesos1)
    dig2 = calcular_digito(cnpj[:13], pesos2)

    return cnpj[-2:] == dig1 + dig2


#  da strip em valor e se retornar vazio eh porque nao tem razao social
def validar_razao_social(valor):
    return isinstance(valor, str) and valor.strip() != ""


# checa se valor maior que zero
def validar_valor(valor):
    try:
        return float(valor) > 0

    except Exception as e:
        print(f"Erro ao validar valor: {valor}, {e}")
        return False


def validar_e_enriquecer(df_consolidado, df_cadastro):
    print("Iniciando validação...")

    # limpar cnoj
    df_consolidado["cnpj"] = df_consolidado["cnpj"].apply(limpar_cnpj)
    df_cadastro["cnpj"] = df_cadastro["cnpj"].apply(limpar_cnpj)

    # validacoes
    df_consolidado = df_consolidado[df_consolidado["cnpj"].apply(validar_cnpj)]

    df_consolidado = df_consolidado[
        df_consolidado["valordespesas"].apply(validar_valor)
    ]

    df_consolidado = df_consolidado[
        df_consolidado["razao_social"].apply(validar_razao_social)
    ]

    # remove duplicados
    df_cadastro = df_cadastro.drop_duplicates(subset="cnpj")

    # merge usando sufixos depois de quebrar um milhao de vezes
    df_final = df_consolidado.merge(
        df_cadastro,
        on="cnpj",
        how="inner",
        suffixes=("_dados", "_cadastro"),
    )

    # logs
    cnpjs_sem_match = set(df_consolidado["cnpj"]) - set(df_cadastro["cnpj"])
    print(f"CNPJs sem match: {len(cnpjs_sem_match)}")

    duplicados = df_cadastro[df_cadastro.duplicated("cnpj", keep=False)]
    print(f"CNPJs duplicados no cadastro: {duplicados.shape[0]}")

    # renomeia razao social e exclui a outra depois do merge
    df_final = df_final.rename(columns={"razao_social_cadastro": "razao_social"})
    df_final = df_final.drop(columns=["razao_social_dados"], errors="ignore")

    # cria dataframe final
    df_final = df_final[
        [
            "cnpj",
            "razao_social",
            "registro_operadora",
            "modalidade",
            "uf",
            "trimestre",
            "ano",
            "valordespesas",
        ]
    ]

    return df_final


def agregar_dados(df):
    print("Gerando agregações...")

    agrupado = df.groupby(["razao_social", "uf"])

    resultado = (
        agrupado["valordespesas"]
        .agg(total="sum", media="mean", desvio_padrao="std")
        .reset_index()
    )

    return resultado


def executar_validacao(caminho_consolidado, caminho_cadastro, output_dir):
    df_consolidado = pd.read_csv(caminho_consolidado)
    df_cadastro = pd.read_csv(caminho_cadastro, sep=";", encoding="latin1")

    # normalizar colunas
    df_consolidado.columns = df_consolidado.columns.str.lower()
    df_cadastro.columns = df_cadastro.columns.str.lower()

    df_validado = validar_e_enriquecer(df_consolidado, df_cadastro)

    df_agregado = agregar_dados(df_validado)

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    df_validado.to_csv(output_dir / "dados_validos.csv", index=False)
    df_agregado.to_csv(output_dir / "dados_agregados.csv", index=False)

    print("Processo finalizado com sucesso.")
