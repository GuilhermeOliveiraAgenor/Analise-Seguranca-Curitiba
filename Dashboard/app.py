import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, abort

from analise_seguranca_funcoes import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
DB_PATH = 'dados.db'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# =====================================================
# 🔹 Banco de Dados Helpers
# =====================================================
def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db_from_excel(filepath):
    """Lê todas as planilhas do Excel e salva cada uma como tabela no SQLite."""
    xls = pd.ExcelFile(filepath)
    conn = get_conn()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meta_sheets (
                sheet_name TEXT PRIMARY KEY,
                table_name TEXT NOT NULL
            )
        """)
        conn.execute("DELETE FROM meta_sheets")

        for sheet in xls.sheet_names:
            df = xls.parse(sheet)
            table_name = (
                sheet.strip().lower()
                    .replace(" ", "_")
                    .replace("-", "_")
                    .replace("/", "_")
            )
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.execute(
                "INSERT INTO meta_sheets (sheet_name, table_name) VALUES (?, ?)",
                (sheet, table_name)
            )


def get_tables():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT sheet_name, table_name FROM meta_sheets ORDER BY sheet_name")
        rows = cur.fetchall()
    except sqlite3.OperationalError:
        rows = []
    finally:
        conn.close()
    return rows


def load_df(table_name):
    conn = get_conn()
    df = pd.read_sql_query(f'SELECT * FROM \"{table_name}\"', conn)
    conn.close()
    return df


def get_distinct(table_name, column):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            f'SELECT DISTINCT \"{column}\" FROM \"{table_name}\" '
            f'WHERE \"{column}\" IS NOT NULL ORDER BY 1'
        )
        values = [r[0] for r in cur.fetchall() if r[0] not in (None, "", 0)]
    except sqlite3.OperationalError:
        values = []
    finally:
        conn.close()
    return values

import inspect

def sanitize_json(obj):
    """Remove objetos não serializáveis (como funções ou métodos)"""
    if isinstance(obj, (list, tuple)):
        return [sanitize_json(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif callable(obj) or inspect.isfunction(obj) or inspect.ismethod(obj):
        return str(obj)
    else:
        return obj


# =====================================================
# 🔹 Metadados das Funções
# =====================================================
FUNCTIONS_META = {
    "ocorrencias_filtro_crime": {
        "label": "Ocorrências por Crime",
        "func": ocorrencias_filtro_crime,
        "params": ["dataset", "crime"],
    },
    "ranking_bairros_crime": {
        "label": "Ranking de Bairros por Crime",
        "func": ranking_bairros_crime,
        "params": ["dataset", "crime"],
    },
    "crimes_dia_crime_bairro": {
        "label": "Crimes por Dia da Semana (Crime + Bairro)",
        "func": crimes_dia_crime_bairro,
        "params": ["dataset", "crime", "bairro"],
    },
    "periodo_crime_bairro_crime": {
        "label": "Período do Crime (Crime + Bairro)",
        "func": periodo_crime_bairro_crime,
        "params": ["dataset", "crime", "bairro"],
    },
    "crimes_perigosos_semestre": {
        "label": "Crimes Perigosos por Semestre",
        "func": crimes_perigosos_semestre,
        "params": ["dataset", "semestre"],
    },
    "crimes_moradias_semestre": {
        "label": "Crimes em Moradias por Semestre",
        "func": crimes_moradias_semestre,
        "params": ["dataset", "semestre"],
    },
    "crimes_bairro": {
        "label": "Crimes Perigosos por Bairro",
        "func": crimes_bairro,
        "params": ["dataset", "bairro"],
    },
    "crimes_moradias_bairro": {
        "label": "Crimes em Moradias por Bairro",
        "func": crimes_moradias_bairro,
        "params": ["dataset", "bairro"],
    },
    "periodo_moradias_bairro": {
        "label": "Período Crimes em Moradias por Bairro",
        "func": periodo_moradias_bairro,
        "params": ["dataset", "bairro"],
    },
    "dia_moradias_bairro": {
        "label": "Dia da Semana Crimes em Moradias por Bairro",
        "func": dia_moradias_bairro,
        "params": ["dataset", "bairro"],
    },
    "periodo_furtos_roubos_bairro": {
        "label": "Período Furtos/Roubos por Bairro",
        "func": periodo_furtos_roubos_bairro,
        "params": ["dataset", "bairro"],
    },
    "dia_furtos_roubos_bairro": {
        "label": "Dia Furtos/Roubos por Bairro",
        "func": dia_furtos_roubos_bairro,
        "params": ["dataset", "bairro"],
    },
    "periodo_crime_bairro": {
        "label": "Principal Período por Crime (Bairro)",
        "func": periodo_crime_bairro,
        "params": ["dataset", "bairro"],
    },
    "crimes_perigosos_bairro_periodo": {
        "label": "Crimes Perigosos (Bairro + Período)",
        "func": crimes_perigosos_bairro_periodo,
        "params": ["dataset", "bairro", "periodo"],
    },
    "crime_comercial_bairro": {
        "label": "Crimes em Comércio em Horário Comercial (Bairro)",
        "func": crime_comercial_bairro,
        "params": ["dataset", "bairro"],
    },
    "top10_bairros_perigosos": {
        "label": "Top 10 Bairros com Ocorrências Mais Perigosas",
        "func": top10_bairros_perigosos,
        "params": ["dataset"],
    },
    "bairros_por_crime_periodo": {
        "label": "Bairros por Crime e Período",
        "func": bairros_por_crime_periodo,
        "params": ["dataset", "crime", "periodo"],
    },
    "evolucao_crimes_perigosos": {
        "label": "Evolução Mensal de Crimes Perigosos",
        "func": evolucao_crimes_perigosos,
        "params": ["dataset"],
    },
    "ranking_geral_crimes": {
        "label": "Top 10 Crimes Mais Comuns",
        "func": ranking_geral_crimes,
        "params": ["dataset"],
    },
    "crimes_por_ambiente": {
        "label": "Crimes por Tipo de Ambiente",
        "func": crimes_por_ambiente,
        "params": ["dataset"],
    },
}


# =====================================================
# 🔹 Rotas Flask
# =====================================================
@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "Nenhum arquivo enviado", 400

        file = request.files['file']

        if file.filename == '':
            return "Nenhum arquivo selecionado", 400

        if not file.filename.endswith('.xlsx'):
            return "Apenas arquivos .xlsx são permitidos", 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        init_db_from_excel(filepath)
        return redirect(url_for('funcoes'))

    tables = get_tables()
    return render_template('upload.html', tables=tables)


@app.route('/funcoes')
def funcoes():
    tables = get_tables()
    if not tables:
        return redirect(url_for('upload'))
    return render_template('funcoes.html', funcoes=FUNCTIONS_META, tables=tables)


@app.route('/funcoes/<key>', methods=['GET', 'POST'])
def funcao_parametros(key):
    if key not in FUNCTIONS_META:
        abort(404)

    tables = get_tables()
    if not tables:
        return redirect(url_for('upload'))

    meta = FUNCTIONS_META[key]
    default_table = tables[0][1]

    # =========================
    # GET → mostra formulário
    # =========================
    if request.method == 'GET':
        crimes = get_distinct(default_table, 'Natureza')
        bairros = get_distinct(default_table, 'Bairro')
        return render_template(
            'grafico.html',
            stage='form',
            func_key=key,
            meta=meta,
            tables=tables,
            crimes=crimes,
            bairros=bairros,
            result=None
        )

    # =========================
    # POST → processa filtros
    # =========================
    if 'dataset' in meta['params']:
        table_name = request.form.get('dataset') or default_table
    else:
        table_name = default_table

    df = load_df(table_name)

    params = {}
    if 'crime' in meta['params']:
        params['crime'] = request.form.get('crime')
    if 'bairro' in meta['params']:
        params['bairro'] = request.form.get('bairro')
    if 'semestre' in meta['params']:
        semestre = request.form.get('semestre') or "1"
        params['semestre'] = int(semestre)
    if 'periodo' in meta['params']:
        params['periodo'] = request.form.get('periodo')

    func = meta['func']
    result = func(df, **{k: v for k, v in params.items() if v})

    # =====================================================
    # 🔹 Ranking de Bairros por Crime → múltiplos gráficos
    #     Esperoa DataFrame com colunas: Bairro, Crimes, Bloco
    # =====================================================
    if key == "ranking_bairros_crime" and isinstance(result, pd.DataFrame) and "Bloco" in result.columns:
        blocos = []
        result = result.copy()

        result["Bairro"] = result["Bairro"].astype(str).replace(["None", "nan", "0", ""], pd.NA)
        result["Crimes"] = pd.to_numeric(result["Crimes"], errors="coerce").fillna(0)
        result = result.dropna(subset=["Bairro"])
        result = result[result["Crimes"] > 0]

        for bloco_id, bloco_df in result.groupby("Bloco"):
            labels = bloco_df["Bairro"].tolist()    # ✅ note os ()
            values = bloco_df["Crimes"].astype(float).tolist() # ✅ note os ()
            blocos.append({
                "labels": labels,
                "data": values,  # <-- CORRIGIDO (era "values")
                "titulo": f"Bloco {int(bloco_id)}"
            })

        result_table = result[["Bairro", "Crimes", "Bloco"]].to_html(
            classes="table table-sm table-striped",
            index=False
        )

        return render_template(
            "grafico.html",
            stage="chart_multi",
            meta=meta,
            blocos=blocos,
            result_table=result_table
        )


    # =====================================================
    # 🔹 Caso normal: um gráfico
    # =====================================================
    if isinstance(result, pd.DataFrame):
        labels = result.iloc[:, 0].astype(str).tolist()

        numeric_cols = result.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            values = result[numeric_cols[0]].astype(float).tolist()
        else:
            try:
                values = pd.to_numeric(
                    result.iloc[:, -1],
                    errors='coerce'
                ).fillna(0).tolist()
            except Exception:
                values = [0] * len(result)

        result_table = result.to_html(
            classes='table table-sm table-striped',
            index=False
        )
    else:
        labels, values, result_table = [], [], None

    return render_template(
        'grafico.html',
        stage='chart',
        func_key=key,
        meta=meta,
        tables=tables,
        params=params,
        labels=labels,
        values=values,
        table_name=table_name,
        result_table=result_table
    )


if __name__ == '__main__':
    app.run(debug=True)