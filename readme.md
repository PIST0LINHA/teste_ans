# PIPELINE DE DADOS - ANS

Este projeto visa implementar um pipeline de dados completo utilizando dados públicos da ANS (Agência Nacional de Saúde Suplementar).

O objetivo é coletar, processar, validar e consolidar informações financeiras de operadoras de planos de saúde.

---

# Etapas do Projeto

O pipeline é dividido em quatro etapas principais:

## 1. Download dos dados

- Baixa arquivos de demonstração contábeis por ano e trimestre
- Baixa o cadastro de operadoras ativas
- Armazena os arquivos na pasta `raw_data`

## 2. Extração de Arquivos

- Extrai arquivos `.zip`
- Organiza os arquivos na pasta `extracted`

## 3. Processamento

- Lê arquivos `.csv, .txt, .xlsx e .xls`
- Filtra dados relacionados somente à eventos e sinistros
- Calcula o valor das despesas
- Gera um arquivo com os dados consolidados na pasta `final`

## 4. Validação e Enriquecimento de dados

- Valida CNPJ, Valores Positivos e Razões Sociais não vazias
- Cruza dados com o cadastro ANS
- Normaliza dados e remove inconsistências
- Gera:
  - `dados_agregados.csv`
  - `dados_validos.csv`
   
