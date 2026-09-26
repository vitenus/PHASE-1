# VITENUS Circular Engine — V0.4

V0.4 reconstrói o protótipo como uma plataforma operacional de **Diagnóstico e Valorização Circular**.

## O que mudou
- Workspace único por projeto, com fluxo cronológico da demanda ao monitoramento.
- Escopo hierárquico e flexível: planta → setor → linha/unidade → processo → etapa.
- Coleta de campo orientada a observações, entrevistas, medições, fontes e qualidade.
- Transformação de observações em dados estruturados.
- Registro de perdas e oportunidades circulares sem obrigar o usuário a trabalhar em tabelas.
- Simulador econômico preliminar na proposta com Payback e ROI.
- Business Case e curva de retorno.
- Priorização com os seis índices e IPC.
- Dashboard com gráficos Plotly.
- Parecer executivo e exportação do workspace.
- Rastreabilidade de dados e versão metodológica.
- Identidade visual VITENUS renovada: superfícies arredondadas, fluxo, cards, métricas e hierarquia visual.
- Correção do erro `min_height` → `height` no `st.text_area`.

## Supabase
Execute também `sql/004_workspace.sql` depois das migrações anteriores. A aplicação continua funcionando localmente mesmo sem Supabase; o botão de persistência informa o erro de conexão sem interromper o workspace.

## Execução
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Testes
```bash
pytest -q
python -m py_compile app.py db.py economics.py scoring.py validation.py recommendation.py
```

## Nota metodológica
Os pesos, escalas e faixas proprietárias do VITENUS continuam sendo hipóteses de protótipo e devem ser testados e calibrados com projetos-piloto. Payback/ROI projetados não são garantias.
