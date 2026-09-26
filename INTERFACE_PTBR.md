# VITENUS Circular Engine V0.2 — Interface

A interface foi reorganizada como um programa guiado, e não como uma página única de métricas.

## Fluxo visual

1. Visão geral
2. Cadrage
3. Diagnóstico
4. Dados & baseline
5. Perdas & oportunidades
6. Priorização
7. Business Case
8. Plano de ação
9. Monitoramento
10. Metodologia
11. Dashboard
12. Supabase

## Princípios de UX

- Cada tela responde **o que fazer agora?**
- Cada entrada explica **por que é necessária?**
- Cada resultado explica **como foi calculado?**
- Cada hipótese informa **se é normativa, referencial ou proprietária**.
- Campos são organizados pela sequência lógica do serviço.
- Tabelas são editáveis para simular coleta real.
- Gráficos mostram os resultados sem substituir o texto técnico.
- A metodologia fica dentro do produto, em vez de ficar escondida em um PDF externo.

## Próxima evolução

A V0.2 ainda usa dados locais de sessão para várias telas. A próxima etapa deve persistir cada entidade no Supabase:

`empresa → planta → processo → fluxo → observação → fonte → perda → oportunidade → solução → score → business case → plano → medição`.

Também deve substituir os valores demo por registros reais vindos do banco.
