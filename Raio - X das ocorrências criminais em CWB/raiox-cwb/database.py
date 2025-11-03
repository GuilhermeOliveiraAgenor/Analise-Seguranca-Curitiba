# database.py
# Funções utilitárias para conectar e operar o SQLite
import sqlite3
from contextlib import closing

DB_PATH = "crimes.db"

def conectar():
    # isolation_level=None permite autocommit com execute()
    return sqlite3.connect(DB_PATH, isolation_level=None)

def criar_tabelas():
    with conectar() as conn, open("models.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

def inserir_crimes_lote(rows):
    """
    Insere múltiplas linhas já normalizadas (lista de tuplas) no banco.
    Espera tuplas na ordem:
    (ano, mes, dia, dia_semana, hora, municipio, bairro, tipo_natureza, natureza, ambiente)
    """
    sql = """
    INSERT INTO crimes
      (ano, mes, dia, dia_semana, hora, municipio, bairro, tipo_natureza, natureza, ambiente)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    with conectar() as conn:
        conn.executemany(sql, rows)

def query_df(sql, params=()):
    """
    Executa uma consulta e retorna lista de dicionários (para JSON fácil).
    """
    with conectar() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]

def query_scalar(sql, params=()):
    with conectar() as conn:
        cur = conn.execute(sql, params)
        r = cur.fetchone()
        return None if r is None else r[0]
