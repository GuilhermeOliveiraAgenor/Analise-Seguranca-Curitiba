# analytics.py
# Normalização de CSV (colunas com/sem acento) + listas úteis de classificação

import pandas as pd
import unicodedata

# Mapeia nomes possíveis -> canônicos (sem acento/espacos e em minúsculas)
COLMAP = {
    "id": "id",
    "ano": "ano",
    "mês": "mes", "mes": "mes",
    "dia": "dia",
    "dia da semana": "dia_semana",
    "hora": "hora",
    "município": "municipio", "municipio": "municipio",
    "bairro": "bairro",
    "tipo natureza": "tipo_natureza", "tipo_natureza": "tipo_natureza",
    "natureza": "natureza",
    "ambiente": "ambiente",
}

def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Normaliza cabeçalhos
    new_cols = []
    for c in df.columns:
        base = strip_accents(c).strip().lower()  # remove acento, trim, lower
        new_cols.append(COLMAP.get(base, base))
    df.columns = new_cols
    return df

def carregar_csv_para_linhas(file_storage) -> list[tuple]:
    """
    Lê CSV carregado via Flask, normaliza colunas, filtra Curitiba e devolve linhas para inserir no DB.
    Retorna lista de tuplas (ano, mes, dia, dia_semana, hora, municipio, bairro, tipo_natureza, natureza, ambiente)
    """
    # Tentamos com separador vírgula (se vier de fonte padrão); ajuste se necessário
    df = pd.read_csv(file_storage, sep=",", encoding="latin-1")
    df = normalize_columns(df)

    # Checagem mínima de colunas
    required = {"ano","mes","dia","dia_semana","hora","municipio","bairro","natureza","ambiente"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes no CSV: {missing}")

    # Filtra apenas Curitiba (case-insensitive)
    df = df[df["municipio"].astype(str).str.upper() == "CURITIBA"].copy()

    # Coerção de tipos
    df["hora"] = pd.to_numeric(df["hora"], errors="coerce").fillna(-1).astype(int)
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    df["mes"] = pd.to_numeric(df["mes"], errors="coerce").astype("Int64")
    df["dia"] = pd.to_numeric(df["dia"], errors="coerce").astype("Int64")

    # Preenche tipo_natureza se não existir
    if "tipo_natureza" not in df.columns:
        df["tipo_natureza"] = None

    # Seleção e ordem canônica
    df = df[["ano","mes","dia","dia_semana","hora","municipio","bairro","tipo_natureza","natureza","ambiente"]]

    # Transforma em lista de tuplas
    rows = list(map(tuple, df.to_records(index=False)))
    return rows

# Listas coerentes com seus dados reais (conforme análise anterior)
FURTOS = {
    "FURTO SIMPLES",
    "FURTO QUALIFICADO",
    "FURTO DE COISA COMUM",
}

ROUBOS = {
    "ROUBO",
    "ROUBO AGRAVADO",
    "ROUBO COM RESULTADO DE LESAO CORPORAL GRAVE",
}

CRIMES_VIOLENTOS = {
    "ROUBO",
    "ROUBO AGRAVADO",
    "EXTORSAO MEDIANTE SEQUESTRO",
    "ROUBO COM RESULTADO DE LESAO CORPORAL GRAVE",
}

CRIMES_COMERCIO_BASE = {
    # você usou isto para comércio nas análises
    "FURTO SIMPLES",
    "FURTO QUALIFICADO",
    "ROUBO",
    "DANO",
    "ROUBO AGRAVADO",
    "VIOLACAO DE DOMICILIO",
    "FURTO DE COISA COMUM",
    "ROUBO COM RESULTADO DE LESAO CORPORAL GRAVE",
}

# Constrói cláusulas SQL IN ('A','B','C')
def sql_in(list_or_set):
    # Monta clausula SQL IN com escape de apóstrofo
    safe_values = []
    for x in list_or_set:
        safe_values.append("'" + str(x).replace("'", "''") + "'")
    return "(" + ", ".join(safe_values) + ")"


def periodo_case_sql(col="hora"):
    # Manhã 6..11, Tarde 12..17, Noite demais
    return f"""
    CASE
      WHEN {col} BETWEEN 6 AND 11 THEN 'Manhã'
      WHEN {col} BETWEEN 12 AND 17 THEN 'Tarde'
      ELSE 'Noite'
    END
    """
