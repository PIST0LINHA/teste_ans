## -- cria tabela de operadoras

CREATE TABLE IF NOT EXISTS operadoras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    registro_ans VARCHAR(20) UNIQUE NOT NULL,
    cnpj VARCHAR(14) NOT NULL,
    razao_social VARCHAR(255) NOT NULL,
    nome_fantasia VARCHAR(255),
    modalidade VARCHAR(100),
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf CHAR(2),
    cep VARCHAR(8),
    ddd VARCHAR(2),
    telefone VARCHAR(20),
    fax VARCHAR(20),
    email VARCHAR(255),
    representante VARCHAR(255),
    cargo_representante VARCHAR(100),
    regiao_comercializacao VARCHAR(100),
    data_registro_ans DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

## -- cria tabela de despesas
CREATE TABLE IF NOT EXISTS despesas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,  -- BIGINT para muitos registros
    cnpj VARCHAR(14) NOT NULL,
    razao_social VARCHAR(255) NOT NULL,
    trimestre TINYINT NOT NULL,   -- 1 a 4 cabe em TINYINT
    ano SMALLINT NOT NULL,
    valor_despesas DECIMAL(15,2) NOT NULL,
    registro_ans VARCHAR(20),
    modalidade VARCHAR(100),
    uf CHAR(2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

## -- Índices para performance
CREATE INDEX idx_despesas_cnpj ON despesas(cnpj);
CREATE INDEX idx_despesas_trimestre_ano ON despesas(trimestre, ano);
CREATE INDEX idx_despesas_uf ON despesas(uf);
CREATE INDEX idx_despesas_registro_ans ON despesas(registro_ans);
CREATE INDEX idx_despesas_valor ON despesas(valor_despesas);

# -- dados agregados
CREATE TABLE IF NOT EXISTS despesas_agregadas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    razao_social VARCHAR(255) NOT NULL,
    uf CHAR(2) NOT NULL,
    total_despesas DECIMAL(15,2) NOT NULL,
    media_despesas DECIMAL(15,2) NOT NULL,
    desvio_padrao_despesas DECIMAL(15,2),
    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_razao_uf (razao_social, uf)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_agregadas_razao_uf ON despesas_agregadas(razao_social, uf);

## Quais as 5 operadoras com maior crescimento percentual de despesas entre o primeiro e o último trimestre analisado?

WITH
-- Identificar primeiro e último trimestre
primeiro_ultimo AS (
    SELECT 
        MIN(CONCAT(ano, LPAD(trimestre, 2, '0'))) AS primeiro,
        MAX(CONCAT(ano, LPAD(trimestre, 2, '0'))) AS ultimo
    FROM despesas
),
-- Despesas totais por operadora e trimestre
despesas_por_operadora AS (
    SELECT 
        cnpj,
        razao_social,
        ano,
        trimestre,
        CONCAT(ano, LPAD(trimestre, 2, '0')) AS periodo,
        SUM(valor_despesas) AS total_despesas
    FROM despesas
    GROUP BY cnpj, razao_social, ano, trimestre
),
-- Filtrar apenas primeiro e último período
primeiro_periodo AS (
    SELECT d.cnpj, d.razao_social, d.total_despesas
    FROM despesas_por_operadora d
    CROSS JOIN primeiro_ultimo pu
    WHERE d.periodo = pu.primeiro
),
ultimo_periodo AS (
    SELECT d.cnpj, d.razao_social, d.total_despesas
    FROM despesas_por_operadora d
    CROSS JOIN primeiro_ultimo pu
    WHERE d.periodo = pu.ultimo
),
-- Juntar e calcular crescimento
crescimento AS (
    SELECT 
        p.cnpj,
        p.razao_social,
        p.total_despesas AS despesa_primeiro,
        u.total_despesas AS despesa_ultimo,
        CASE 
            WHEN p.total_despesas > 0 THEN 
                (u.total_despesas - p.total_despesas) / p.total_despesas * 100
            ELSE NULL
        END AS crescimento_percentual
    FROM primeiro_periodo p
    INNER JOIN ultimo_periodo u ON p.cnpj = u.cnpj
)
SELECT 
    cnpj,
    razao_social,
    despesa_primeiro,
    despesa_ultimo,
    crescimento_percentual
FROM crescimento
WHERE crescimento_percentual IS NOT NULL
ORDER BY crescimento_percentual DESC
LIMIT 5;

## Qual a distribuição de despesas por UF? Liste os 5 estados com maiores despesas totais. 

SELECT 
    uf,
    SUM(valor_despesas) AS total_despesas
FROM despesas
WHERE uf IS NOT NULL AND uf != ''
GROUP BY uf
ORDER BY total_despesas DESC
LIMIT 5;
