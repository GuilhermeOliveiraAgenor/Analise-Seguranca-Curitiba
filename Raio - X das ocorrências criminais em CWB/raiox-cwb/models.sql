-- Tabela canônica com nomes normalizados (sem acentos)
CREATE TABLE IF NOT EXISTS crimes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ano INTEGER,
  mes INTEGER,
  dia INTEGER,
  dia_semana TEXT,
  hora INTEGER,
  municipio TEXT,
  bairro TEXT,
  tipo_natureza TEXT,
  natureza TEXT,
  ambiente TEXT
);

-- Índices para acelerar as consultas mais comuns
CREATE INDEX IF NOT EXISTS idx_crimes_bairro ON crimes (bairro);
CREATE INDEX IF NOT EXISTS idx_crimes_hora ON crimes (hora);
CREATE INDEX IF NOT EXISTS idx_crimes_natureza ON crimes (natureza);
CREATE INDEX IF NOT EXISTS idx_crimes_dia_semana ON crimes (dia_semana);
CREATE INDEX IF NOT EXISTS idx_crimes_ambiente ON crimes (ambiente);
