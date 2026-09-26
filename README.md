# VITENUS Circular Engine — V0.3

Protótipo de interface de programa para o primeiro serviço da VITENUS: **Diagnóstico e Valorização Circular**.

## O que mudou na V0.3

- interface em pt-BR reorganizada como fluxo de aplicação;
- navegação por etapas do serviço;
- cartões visuais e blocos de explicação;
- entrada de dados guiada por contexto técnico;
- tabelas editáveis para diagnóstico, baseline, oportunidades e plano de ação;
- explicações de "por que este dado existe";
- metodologia incorporada ao próprio programa;
- dicionário de variáveis, fórmulas, escalas, pesos e hipóteses;
- sensibilidade inicial do IPC;
- separação explícita entre fundamentos externos e hipóteses proprietárias VITENUS;
- dashboard executivo e tela de rastreabilidade;
- manutenção dos módulos de cálculo, testes e Supabase da V0.1.
- ordem cronológica explícita: demanda em espera → proposta/qualificação → cadrage → diagnóstico → transformação dos dados → perdas → oportunidades → priorização → plano + ROI → monitoramento.
- nova fase de proposta baseada exclusivamente nos dados limitados disponíveis antes do diagnóstico, com matriz qualitativa de pertinência e limites explícitos.
- persistência inicial de demandas e propostas via `sql/003_workflow.sql`.

## Estrutura do método

`Demandas em espera → Proposta / qualificação → Cadrage → Diagnóstico industrial → Transformação dos dados → Identificação de perdas → Oportunidades circulares → Priorização → Plano + Business Case + Payback + ROI → Implementação → Monitoramento → ROI realizado`

## Importante

A V0.3 continua sendo um protótipo. Pesos, faixas, thresholds, cenários e regras de governança são hipóteses metodológicas internas em validação. A aplicação não representa certificação ISO nem garantia de retorno.

## Deploy

- entrypoint: `app.py`
- dependências: `requirements.txt`
- configuração Streamlit: `.streamlit/config.toml`
- banco: Supabase
- versão metodológica exibida: `VITENUS-METHODOLOGY-0.3`
