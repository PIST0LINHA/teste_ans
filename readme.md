# PIPELINE DE DADOS - ANS

Este projeto visa implementar um pipeline de dados completo utilizando dados públicos da ANS (Agência Nacional de Saúde Suplementar).

O objetivo é coletar, processar, validar e consolidar informações financeiras de operadoras de planos de saúde.

***

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

***

# Decisões Técnicas

O projeto expos diversas tomadas de decisões técnicas durante seu desenvolvimento, sendo elas:

- Processar os arquivos baixados de forma incremental ou de uma vez na memória
Dado o baixo volume de arquivos, foi decidido processar todos em memória, onde menos de 1GB de RAM foi utilizado para o processo e geração de dados finais

- Validação de dados
Dados como CNPJs e Razões sociais poderiam vir inválidos, seja por estarem incompletos ou vazios, o que necessitou tanto de limpeza quanto normalização.
Após normalização e limpeza, dados inválidos foram ignorados.
No arquivo `consolidado.csv` cadastros presentes nos registros contábeis mas não presentes no cadastro ANS, e vice-versa, foram descartados.
 
***

# Executando o projeto

1. Instale as dependências
- Em um terminal, execute o comando `pip install -r requirements.txt`

2. Execute o pipeline
- `python main.py`

## Observação

Em alguns ambientes, é necessário que o comando seja modificado para `python3 main.py`. 
Caso não queira executar o script `setup.sh`, execute os seguintes comandos:
- `python -m venv venv`
- `source venv/bin/activate`
- `pip install --upgrade pip`
- `pip install -r requirements.txt`

Vale ressaltar que o ambiente criado é um ambiente virtual e não deve afetar o ambiente global já configurado, caso exista.


