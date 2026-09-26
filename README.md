# Vitenus Circular Engine — V0.1

Protótipo de pesquisa aplicada para diagnóstico, valorização circular, priorização, Payback, ROI e acompanhamento de desempenho.

## Interface

A aplicação Streamlit está em **português do Brasil (pt-BR)**. A linguagem técnica interna do motor mantém códigos estáveis como IE, FT, IA, CI, TN, GR, IPC, ROI, Payback, KPI e DCS.

## Estrutura

- `app.py` — ponto de entrada Streamlit e interface pt-BR
- `scoring.py` — motor dos seis índices e IPC
- `economics.py` — Payback e ROI
- `recommendation.py` — regras de governança e recomendação
- `validation.py` — validações de bloqueio/qualidade
- `db.py` — conexão e persistência no Supabase
- `sql/` — scripts SQL versionados
- `tests/` — testes automatizados
- `docs/` — documentação metodológica e implantação
- `.streamlit/config.toml` — configuração da aplicação
- `requirements.txt` — dependências Python

## Deploy no Streamlit Community Cloud

Configure o arquivo principal como:

`app.py`

Mantenha `requirements.txt` na raiz do repositório.

As credenciais Supabase devem ser configuradas como Secrets do Streamlit Cloud ou em `.env` apenas no desenvolvimento local. Nunca publique chaves privadas no GitHub.

## SQL / Supabase

A tradução da interface não altera o banco. Não é necessário executar novamente os scripts SQL apenas para aplicar a tradução.
