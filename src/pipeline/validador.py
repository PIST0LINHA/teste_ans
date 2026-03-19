import pandas as pd
import re
from pathlib import Path


def limpar_cnpj(cnpj):
    # roda uma expressao regular pra tirar tudo menos numeros
    return re.sub(r"\D", "", str(cnpj))


def validar_cnpj(cnpj):
    # checa numero verificador e tamanho do cnpj
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


def validar_razao_social(valor):
    # checa se razao social nao eh nula
    return isinstance(valor, str) and valor.strip() != ""


def validar_valor(valor):
    # descarta valores negativos
    try:
        return float(valor) > 0
    except Exception as e:
        print(f"Erro ao validar valor: {valor}, {e}")
        return False


def validar_e_enriquecer(df_consolidado, df_cadastro):
    print("Iniciando validação...")

    # limpa cnpjs
    df_consolidado["cnpj"] = df_consolidado["cnpj"].apply(limpar_cnpj)
    df_cadastro["cnpj"] = df_cadastro["cnpj"].apply(limpar_cnpj)

    # valida os dados
    df_consolidado = df_consolidado[df_consolidado["cnpj"].apply(validar_cnpj)]
    df_consolidado = df_consolidado[
        df_consolidado["valordespesas"].apply(validar_valor)
    ]
    df_consolidado = df_consolidado[
        df_consolidado["razao_social"].apply(validar_razao_social)
    ]

    # Remove duplicatas do cadastro
    df_cadastro = df_cadastro.drop_duplicates(subset="cnpj")

    # inner join no cpf
    df_final = df_consolidado.merge(
        df_cadastro,
        on="cnpj",
        how="inner",
        suffixes=("_dados", "_cadastro"),
    )

    # Logs
    cnpjs_sem_match = set(df_consolidado["cnpj"]) - set(df_cadastro["cnpj"])
    print(f"CNPJs sem match: {len(cnpjs_sem_match)}")
    duplicados = df_cadastro[df_cadastro.duplicated("cnpj", keep=False)]
    print(f"CNPJs duplicados no cadastro: {duplicados.shape[0]}")

    # Renomeia a coluna de razao social (vem do cadastro) e descarta a outra
    df_final = df_final.rename(columns={"razao_social_cadastro": "razao_social"})
    df_final = df_final.drop(columns=["razao_social_dados"], errors="ignore")

    # Renomeia todas as colunas para o padrao do teste
    df_final = df_final.rename(
        columns={
            "cnpj": "CNPJ",
            "razao_social": "RazaoSocial",
            "trimestre": "Trimestre",
            "ano": "Ano",
            "valordespesas": "ValorDespesas",
            "registro_operadora": "RegistroANS",
            "modalidade": "Modalidade",
            "uf": "UF",
        }
    )

    # Seleciona apenas as colunas desejadas, na ordem especificada
    colunas_finais = [
        "CNPJ",
        "RazaoSocial",
        "Trimestre",
        "Ano",
        "ValorDespesas",
        "RegistroANS",
        "Modalidade",
        "UF",
    ]
    df_final = df_final[colunas_finais]

    # Ordena por RazaoSocial e UF (para ficar "agrupado" visualmente)
    df_final = df_final.sort_values(by=["RazaoSocial", "UF"]).reset_index(drop=True)

    return df_final


def agregar_dados(df):
    print("Gerando agregações...")
    agrupado = df.groupby(["RazaoSocial", "UF"])
    resultado = (
        agrupado["ValorDespesas"]
        .agg(total="sum", media="mean", desvio_padrao="std")
        .reset_index()
    )
    return resultado


def executar_validacao(caminho_consolidado, caminho_cadastro, output_dir):
    # Carrega os dados
    df_consolidado = pd.read_csv(caminho_consolidado)
    df_cadastro = pd.read_csv(caminho_cadastro, sep=";", encoding="latin1")

    # Normaliza nomes das colunas para minúsculas (facilita o merge)
    df_consolidado.columns = df_consolidado.columns.str.lower()
    df_cadastro.columns = df_cadastro.columns.str.lower()

    # Processa validação e enriquecimento
    df_validado = validar_e_enriquecer(df_consolidado, df_cadastro)

    # Gera dados agregados
    df_agregado = agregar_dados(df_validado)

    # Garante que o diretório de saída existe
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Salva os arquivos
    df_validado.to_csv(output_dir / "dados_validos.csv", index=False)
    df_agregado.to_csv(output_dir / "dados_agregados.csv", index=False)

    print("\nArquivos gerados com sucesso:")
    print(f"  - Detalhado: {output_dir / 'dados_validos.csv'}")
    print(f"  - Agregado : {output_dir / 'despesas_agregados.csv'}")
    print("Processo finalizado.")
