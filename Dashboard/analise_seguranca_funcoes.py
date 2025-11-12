# analise_seguranca_funcoes.py
# Funções de análise para trabalhar com um DataFrame (base única)

import pandas as pd

# Listas de filtros
crimes_perigosos = [
    'FURTO SIMPLES',
    'FURTO QUALIFICADO',
    'ROUBO',
    'DROGAS PARA O CONSUMO PESSOAL',
    'DANO',
    'ROUBO AGRAVADO',
    'VIOLACAO DE DOMICILIO',
    'FURTO DE COISA COMUM',
    'PORTE ILEGAL DE ARMA DE FOGO, ACESSORIO OU MUNICAO - USO PERMITIDO',
    'EXTORSAO MEDIANTE SEQUESTRO',
    'ROUBO COM RESULTADO DE LESAO CORPORAL GRAVE',
    'COMERCIO ILEGAL DE ARMA DE FOGO'
]

furtos = [
    'FURTO SIMPLES', 'FURTO QUALIFICADO', 'FURTO DE COISA COMUM',
]

roubos = [
    'ROUBO', 'ROUBO AGRAVADO', 'ROUBO COM RESULTADO DE LESAO CORPORAL GRAVE'
]

furtos_roubos = [
    'FURTO SIMPLES', 'FURTO QUALIFICADO', 'FURTO DE COISA COMUM',
    'ROUBO', 'ROUBO AGRAVADO', 'ROUBO COM RESULTADO DE LESAO CORPORAL GRAVE'
]

crimes_comercio = [
    'FURTO SIMPLES',
    'FURTO QUALIFICADO',
    'ROUBO',
    'DANO',
    'ROUBO AGRAVADO',
    'VIOLACAO DE DOMICILIO',
    'FURTO DE COISA COMUM',
    'ROUBO COM RESULTADO DE LESAO CORPORAL GRAVE',
]

mes_map = {
    'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4,
    'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8,
    'set': 9, 'out': 10, 'nov': 11, 'dez': 12
}

def _add_mes_num(df):
    if 'Mês' in df.columns and 'Mês_num' not in df.columns:
        df = df.copy()
        df['Mês_num'] = df['Mês'].map(mes_map)
    return df

def _periodo(hora):
    try:
        h = int(hora)
    except (ValueError, TypeError):
        return 'Indefinido'
    if 6 <= h <= 11:
        return 'Manhã'
    elif 12 <= h <= 17:
        return 'Tarde'
    else:
        return 'Noite'

# 1) Ocorrências por crime específico
def ocorrencias_filtro_crime(df, crime):
    f = df[df['Natureza'] == crime]
    r = f['Natureza'].value_counts().reset_index()
    r.columns = ['Natureza', 'Quantidade']
    return r


# 2) Ranking bairros por crime
def ranking_bairros_crime(df, crime):
    # Garante cópia independente
    f = df.copy()

    # Normaliza nomes das colunas
    colunas = {c.strip().lower(): c for c in df.columns}
    if 'natureza' in colunas:
        natureza_col = colunas['natureza']
    else:
        raise KeyError("Coluna 'Natureza' não encontrada no dataset.")

    if 'bairro' in colunas:
        bairro_col = colunas['bairro']
    else:
        raise KeyError("Coluna 'Bairro' não encontrada no dataset.")

    # Filtro seguro
    f = f[f[natureza_col] == crime]

    # Remove nulos e valores inválidos
    f = f[f[bairro_col].notna()]
    f[bairro_col] = f[bairro_col].astype(str).str.strip()
    f = f[~f[bairro_col].isin(["", "0", "NULL", "None"])]

    # Gera ranking
    q = f[bairro_col].value_counts().reset_index(name='Crimes')
    q.columns = ['Bairro', 'Crimes']

    if q.empty:
        return pd.DataFrame(columns=['Bairro', 'Crimes', 'Bloco'])

    # Ordena e limita até 80 bairros
    q = q.sort_values(by='Crimes', ascending=False).head(80).reset_index(drop=True)

    # Cria coluna de blocos (4 blocos de 20 bairros)
    q["Bloco"] = (q.index // 20) + 1

    return q



# 3) Crimes por dia da semana (crime + bairro)
def crimes_dia_crime_bairro(df, crime, bairro):
    f = df[(df['Natureza'] == crime) & (df['Bairro'] == bairro)]
    q = f['Dia da Semana'].value_counts().reset_index()
    q.columns = ['Dia da Semana', 'Quantidade']
    return q

# 4) Período do crime (crime + bairro)
def periodo_crime_bairro_crime(df, crime, bairro):
    f = df[(df['Natureza'] == crime) & (df['Bairro'] == bairro)].copy()
    f['Periodo'] = f['Hora'].apply(_periodo)
    q = f['Periodo'].value_counts().reset_index()
    q.columns = ['Periodo', 'Quantidade']
    return q

# 5) Crimes perigosos por semestre
def crimes_perigosos_semestre(df, semestre):
    df = df[df['Natureza'].isin(crimes_perigosos)].copy()
    df = _add_mes_num(df)
    if semestre == 1:
        f = df[(df['Mês_num'] >= 1) & (df['Mês_num'] <= 6)]
    else:
        f = df[(df['Mês_num'] >= 7) & (df['Mês_num'] <= 12)]
    r = f.groupby('Mês').size().reset_index(name='Crimes')
    r = r.sort_values(by='Crimes', ascending=False)
    return r

# 6) Crimes contra moradias por semestre
def crimes_moradias_semestre(df, semestre):
    df = df.copy()
    violacao = df[(df['Natureza'] == 'VIOLACAO DE DOMICILIO') & (df['Ambiente'].str.upper() == 'RESIDENCIA')]
    dano = df[(df['Natureza'] == 'DANO') & (df['Ambiente'].str.upper() == 'RESIDENCIA')]
    furt_rob = df[(df['Natureza'].isin(['FURTO', 'ROUBO'])) & (df['Ambiente'].str.upper() == 'RESIDENCIA')]
    base = pd.concat([violacao, dano, furt_rob], ignore_index=True)
    base = _add_mes_num(base)
    if semestre == 1:
        f = base[(base['Mês_num'] >= 1) & (base['Mês_num'] <= 6)]
    else:
        f = base[(base['Mês_num'] >= 7) & (base['Mês_num'] <= 12)]
    r = f.groupby('Mês').size().reset_index(name='Crimes')
    return r.sort_values(by='Crimes', ascending=False)

# 7) Crimes perigosos por bairro
def crimes_bairro(df, bairro):
    f = df[df['Natureza'].isin(crimes_perigosos)]
    f = f[f['Bairro'] == bairro]
    r = f['Natureza'].value_counts().reset_index(name='Crimes')
    r.columns = ['Natureza', 'Crimes']
    return r

# 8) Crimes em moradias por bairro
def crimes_moradias_bairro(df, bairro):
    df = df[['Bairro', 'Natureza', 'Ambiente']].copy()
    violacao = df[(df['Natureza'] == 'VIOLACAO DE DOMICILIO') & (df['Ambiente'] == 'RESIDENCIA')]
    violacao['Crime'] = 'VIOLACAO DE DOMICILIO'
    dano = df[(df['Natureza'] == 'DANO') & (df['Ambiente'] == 'RESIDENCIA')]
    dano['Crime'] = 'DANO'
    fr = df[(df['Natureza'].isin(furtos_roubos)) & (df['Ambiente'] == 'RESIDENCIA')]
    fr['Crime'] = 'FURTO/ROUBO'
    base = pd.concat([violacao, dano, fr])
    base = base[base['Bairro'] == bairro]
    r = base.groupby('Natureza').size().reset_index(name='Crimes')
    return r.sort_values(by='Crimes', ascending=False)

# 9) Período moradias por bairro
def periodo_moradias_bairro(df, bairro):
    df = df[['Bairro', 'Natureza', 'Hora', 'Ambiente']].copy()
    violacao = df[(df['Natureza'] == 'VIOLACAO DE DOMICILIO') &
                  (df['Ambiente'] == 'RESIDENCIA') &
                  (df['Bairro'] == bairro)]
    dano = df[(df['Natureza'] == 'DANO') &
              (df['Ambiente'] == 'RESIDENCIA') &
              (df['Bairro'] == bairro)]
    fr = df[(df['Natureza'].isin(furtos_roubos)) &
            (df['Ambiente'] == 'RESIDENCIA') &
            (df['Bairro'] == bairro)]
    base = pd.concat([violacao, dano, fr])
    base['Periodo'] = base['Hora'].apply(_periodo)
    r = base.groupby('Periodo').size().reset_index(name='Crimes')
    return r.sort_values(by='Crimes', ascending=False)

# 10) Dia da semana moradias por bairro
def dia_moradias_bairro(df, bairro):
    df = df[['Bairro', 'Natureza', 'Hora', 'Ambiente', 'Dia da Semana']].copy()
    violacao = df[(df['Natureza'] == 'VIOLACAO DE DOMICILIO') &
                  (df['Ambiente'] == 'RESIDENCIA') &
                  (df['Bairro'] == bairro)]
    dano = df[(df['Natureza'] == 'DANO') &
              (df['Ambiente'] == 'RESIDENCIA') &
              (df['Bairro'] == bairro)]
    fr = df[(df['Natureza'].isin(furtos_roubos)) &
            (df['Ambiente'] == 'RESIDENCIA') &
            (df['Bairro'] == bairro)]
    base = pd.concat([violacao, dano, fr])
    r = base.groupby('Dia da Semana').size().reset_index(name='Crimes')
    return r.sort_values(by='Crimes', ascending=False)


# 11) Período furtos/roubos por bairro
def periodo_furtos_roubos_bairro(df, bairro):
    try:
        # Filtra apenas furtos e roubos do bairro
        f = df[(df['Bairro'] == bairro) & (df['Natureza'].isin(furtos_roubos))].copy()

        # Garante que a coluna 'Hora' seja numérica (ignora strings como 'Noite', 'Dia')
        f['Hora'] = pd.to_numeric(f['Hora'], errors='coerce')

        # Remove linhas com hora nula (casos de erro de conversão)
        f = f.dropna(subset=['Hora'])

        # Converte hora para inteiro
        f['Hora'] = f['Hora'].astype(int)

        # Mapeia período
        f['Periodo'] = f['Hora'].apply(_periodo)

        # Conta ocorrências por tipo e período
        c = f.groupby(['Natureza', 'Periodo']).size().reset_index(name='Ocorrencias')

        # Seleciona o período com mais ocorrências para cada tipo de crime
        idx = c.groupby('Natureza')['Ocorrencias'].idxmax()
        r = c.loc[idx].reset_index(drop=True)

        # Ordena
        return r.sort_values(by='Ocorrencias', ascending=False)

    except Exception as e:
        print(f"[ERRO] Falha na função periodo_furtos_roubos_bairro: {e}")
        return pd.DataFrame(columns=['Natureza', 'Periodo', 'Ocorrencias'])


# 12) Dia furtos/roubos por bairro
def dia_furtos_roubos_bairro(df, bairro):
    f = df[(df['Bairro'] == bairro) & (df['Natureza'].isin(furtos_roubos))]
    c = f.groupby(['Natureza', 'Dia da Semana']).size().reset_index(name='Ocorrencias')
    idx = c.groupby('Natureza')['Ocorrencias'].idxmax()
    r = c.loc[idx].reset_index(drop=True)
    return r.sort_values(by='Ocorrencias', ascending=False)

# 13) Principal período por crime (geral por bairro)
def periodo_crime_bairro(df, bairro):
    f = df[df['Bairro'] == bairro][['Hora', 'Natureza']].copy()
    f['Periodo'] = f['Hora'].apply(_periodo)
    c = f.value_counts(subset=['Natureza', 'Periodo']).reset_index(name='Contagem')
    idx = c.groupby('Natureza')['Contagem'].idxmax()
    r = c.loc[idx].reset_index(drop=True)
    return r.sort_values(by='Contagem', ascending=False)

# 14) Crimes perigosos por bairro e período
def crimes_perigosos_bairro_periodo(df, bairro, periodo):
    f = df[df['Natureza'].isin(crimes_perigosos)].copy()
    f['Periodo'] = f['Hora'].apply(_periodo)
    f = f[(f['Periodo'] == periodo) & (f['Bairro'] == bairro)]
    r = f['Natureza'].value_counts().reset_index(name='Crimes')
    r.columns = ['Natureza', 'Crimes']
    return r.sort_values(by='Crimes', ascending=False)

# 15) Crimes em comércio (horário comercial) por bairro
def crime_comercial_bairro(df, bairro):
    f = df[df['Natureza'].isin(crimes_comercio)].copy()
    f = f[(f['Hora'].between(8, 18)) & (f['Ambiente'] == 'COMERCIO') & (f['Bairro'] == bairro)]
    r = f['Natureza'].value_counts().reset_index()
    r.columns = ['Natureza', 'Crimes']
    return r.sort_values(by='Crimes', ascending=False)

import pandas as pd

# =====================================================
# 🔹 1) Top 10 bairros mais perigosos (total de crimes)
# =====================================================
def top10_bairros_perigosos(df):
    """Lista os 10 bairros com maior número de ocorrências."""
    ranking = df['Bairro'].value_counts().reset_index()
    ranking.columns = ['Bairro', 'Crimes']
    return ranking.head(10)

# =====================================================
# 🔹 2) Bairros com determinado crime e período do dia
# =====================================================
def bairros_por_crime_periodo(df, crime, periodo):
    """Filtra bairros onde ocorreram crimes específicos no período escolhido."""
    def map_periodo(h):
        if 6 <= h <= 11:
            return 'Manhã'
        elif 12 <= h <= 17:
            return 'Tarde'
        else:
            return 'Noite'

    df['Periodo'] = df['Hora'].apply(map_periodo)
    filtrado = df[(df['Natureza'] == crime) & (df['Periodo'] == periodo)]
    resultado = filtrado['Bairro'].value_counts().reset_index()
    resultado.columns = ['Bairro', 'Ocorrências']
    return resultado.head(20)

# =====================================================
# 🔹 3) Evolução mensal de crimes perigosos (gráfico linha)
# =====================================================
def evolucao_crimes_perigosos(df):
    """Mostra evolução mensal dos crimes perigosos (linha temporal)."""
    crimes_perigosos = [
        'FURTO SIMPLES', 'FURTO QUALIFICADO', 'ROUBO', 'DANO',
        'ROUBO AGRAVADO', 'VIOLACAO DE DOMICILIO',
        'ROUBO COM RESULTADO DE LESAO CORPORAL GRAVE'
    ]

    mes_map = {
        'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4,
        'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8,
        'set': 9, 'out': 10, 'nov': 11, 'dez': 12
    }

    df['Mês_num'] = df['Mês'].map(mes_map)
    filtrado = df[df['Natureza'].isin(crimes_perigosos)]
    serie = filtrado.groupby('Mês_num').size().reset_index(name='Crimes')
    serie = serie.sort_values('Mês_num')
    return serie

# =====================================================
# 🔹 4) Ranking geral de crimes (top 10 naturezas)
# =====================================================
def ranking_geral_crimes(df):
    """Lista os 10 crimes mais comuns (todas naturezas)."""
    ranking = df['Natureza'].value_counts().reset_index()
    ranking.columns = ['Crime', 'Ocorrências']
    return ranking.head(10)

# =====================================================
# 🔹 5) Crimes por tipo de ambiente (pizza)
# =====================================================
def crimes_por_ambiente(df):
    """Conta quantos crimes ocorreram em cada tipo de ambiente."""
    ambiente = df['Ambiente'].value_counts().reset_index()
    ambiente.columns = ['Ambiente', 'Ocorrências']
    return ambiente
