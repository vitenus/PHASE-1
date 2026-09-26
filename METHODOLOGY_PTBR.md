# VITENUS Circular Engine — Metodologia V0.3

## 1. Objetivo

O primeiro serviço da VITENUS parte de um problema industrial: identificar onde a empresa perde matéria, quanto essa perda representa, por que ela ocorre e quais oportunidades circulares podem transformar parte dessa perda em valor econômico e ambiental.

O software não deve começar pelo score. A sequência cronológica de execução é:

**Demanda em espera → proposta/qualificação → cadrage → diagnóstico industrial → transformação dos dados → identificação de perdas → oportunidades circulares → priorização → plano + Business Case + Payback/ROI → implementação → monitoramento → ROI realizado.**

A **proposta/qualificação** é uma etapa anterior ao diagnóstico. Ela usa apenas os dados limitados disponíveis no momento da contratação para verificar aderência, justificar o escopo, registrar lacunas e explicitar limitações. Ela não prova causas, economias, ROI ou Payback.

## 2. Fundamentos externos

- **ISO 14051:2011 — MFCA:** rastrear e quantificar fluxos/estoques de materiais em unidades físicas e avaliar os custos associados.
- **ISO 14053:2021:** implementação faseada de MFCA.
- **ISO 59004:2024:** vocabulário, princípios e orientação para economia circular.
- **ISO 59010:2024:** transição de modelos de criação de valor e redes de valor lineares para circulares.
- **ISO 59020:2024:** medição e avaliação de circularidade em um sistema definido, com fronteiras, indicadores e processamento reproduzível.
- **Medição e verificação:** baseline, período de desempenho, variáveis relevantes, medição e documentação das mudanças devem ser mantidos separados de estimativas.

Esses referenciais dão disciplina ao método. Eles não definem os pesos proprietários da VITENUS.

## 3. Arquitetura cronológica do primeiro serviço

### 3.0 Demanda em espera
Registra a solicitação, dor declarada, origem, escopo percebido e dados iniciais. A demanda permanece em fila até ser analisada.

### 3.1 Proposta / qualificação preliminar
Avalia a pertinência da oferta com dados limitados. A matriz é qualitativa: aderência ao serviço, relação com circularidade, dados mínimos, executabilidade preliminar e possibilidade futura de medição. Não utiliza o IPC e não deve produzir promessa financeira.

### 3.2 Cadrage
Define empresa, produto, processos, perímetro, período, objetivo e fontes disponíveis.

### 3.2 Cadrage
Define empresa, produto, processos, perímetro, período, objetivo e fontes disponíveis.

### 3.3 Diagnóstico industrial
Registra pontos de geração, quantidades, tipos de resíduos, destinos, perdas, restos, subprodutos, emissões/fluidos e comportamento da matéria em cada processo.

### 3.4 Transformação em dados
Cada observação deve possuir, sempre que possível: variável, valor, unidade, período, fonte, método de coleta, qualidade e verificação.

### 3.5 Identificação de perdas
Quatro lentes do serviço:

1. perda de matéria-prima;
2. perda econômica;
3. perda de potencial;
4. perda estratégica.

### 3.6 Oportunidades circulares
Três famílias principais:

- redução — otimização de processo;
- reutilização — reintegração interna;
- valorização — reciclagem/valorização externa.

Exemplos adicionais: remanufatura, simbiose industrial, substituição de matéria-prima, novos produtos e novos modelos.

### 3.7 Priorização
As soluções são avaliadas em seis dimensões: IE, FT, IA, CI, TN e GR.

## 4. Seis índices

### IE — Impacto Econômico

Primeiro calcula-se o retorno econômico anual simples:

`REA = BEN / Investimento × 100`

onde `BEN = BEA − OPEX adicional`.

A V0.2 converte o REA em uma escala 1–10 e depois em 0–100. As bandas são hipóteses de governança V0.1/V0.2, não limites financeiros universais.

### FT — Viabilidade Técnica

Seis dimensões:

- compatibilidade do processo: 25%;
- maturidade tecnológica: 20%;
- disponibilidade de equipamentos: 15%;
- complexidade das modificações: 15%;
- dependência de terceiros: 10%;
- necessidade de piloto/validação: 15%.

A escala de entrada é 1–10. Quanto maior a nota, maior a viabilidade/favorabilidade técnica na dimensão avaliada.

### IA — Impacto Ambiental

Dimensões iniciais:

- material virgem evitado: 30%;
- resíduos evitados/recuperados: 25%;
- energia evitada: 15%;
- água evitada: 10%;
- emissões evitadas: 20%.

Na versão de produção, os percentuais devem ser derivados de quantidades físicas e fatores documentados e versionados. O software não deve inventar fator de emissão ou benefício ambiental.

### CI — Complexidade de Implementação

Dimensões: departamentos, mudanças de processo, fornecedores, parceiros, complexidade de CAPEX, parada de produção e mudança organizacional.

Entrada: 1–10, onde 1 é baixa complexidade e 10 alta complexidade. O resultado é invertido para que maior complexidade produza menor índice:

`CI = 10 × (11 − média ponderada)`

### TN — Tempo Necessário

O tempo de implementação é convertido em índice decrescente. Na V0.1:

| Prazo | TN |
|---:|---:|
| ≤ 1 mês | 100 |
| >1–2 | 90 |
| >2–3 | 80 |
| >3–4 | 70 |
| >4–6 | 60 |
| >6–9 | 50 |
| >9–12 | 40 |
| >12–18 | 30 |
| >18–24 | 20 |
| >24 | 10 |

São faixas de governança, não limites científicos.

### GR — Grau de Risco

Dimensões: técnico, financeiro, operacional, regulatório, mercado, fornecedor e qualidade.

Entrada: 1–10, onde 1 é risco mínimo e 10 risco muito alto. O resultado é invertido:

`GR = 10 × (11 − média ponderada)`

## 5. IPC

`IPC = 0,30 IE + 0,20 FT + 0,20 IA + 0,10 CI + 0,10 TN + 0,10 GR`

Os pesos somam 100% e cada componente está em 0–100, portanto IPC também está em 0–100.

### Racional do desenho

- economia: 30%;
- viabilidade técnica: 20%;
- impacto ambiental: 20%;
- complexidade: 10%;
- tempo: 10%;
- risco: 10%.

A intenção é equilibrar valor econômico, possibilidade de execução e efeito ambiental sem apagar custo de implementação, tempo ou risco.

**Importante:** esses pesos são hipóteses proprietárias. A VITENUS deve testá-los por análise de sensibilidade, concordância entre avaliadores e calibração com projetos reais antes de tratá-los como modelo maduro.

## 6. Business Case

`BEA = economias de materiais + resíduos + energia + água + receita adicional + outros benefícios`

`BEN = BEA − OPEX adicional`

`ROI projetado = (benefícios − OPEX − investimento) / investimento × 100`

O ROI do projeto não deve ser confundido com o ROI da contratação do serviço VITENUS.

## 7. Payback

A aproximação simples é:

`Payback (meses) = Investimento / (BEN anual / 12)`

Para implantação real, o motor deve evoluir para fluxo de caixa mensal com ramp-up, CAPEX parcelado e benefícios por período.

Os cenários conservador/central/otimista são mecanismos de exploração de premissas, não probabilidades.

## 8. Qualidade dos dados — DCS

Escala de evidência:

5. medição instrumentada / ERP / documento financeiro verificável;
4. documento oficial ou registro interno verificável;
3. declaração operacional ou registro não validado independentemente;
2. estimativa técnica;
1. hipótese de mercado / premissa exploratória.

O DCS é uma métrica de governança da evidência; não é intervalo estatístico de confiança.

## 9. Governança

O IPC nunca deve ser o único mecanismo de decisão. O sistema verifica, no mínimo:

- restrição regulatória;
- segurança;
- incompatibilidade técnica;
- risco crítico;
- disponibilidade de mercado;
- disponibilidade de fornecedor;
- qualidade insuficiente dos dados.

## 10. Sensibilidade e validação futura

Após uma amostra real de projetos, a VITENUS deve testar:

- sensibilidade do IPC aos pesos;
- concordância entre avaliadores das notas 1–10;
- relação entre ROI/Payback projetados e realizados;
- viés de seleção e dados ausentes;
- incerteza das medições físicas;
- estabilidade das faixas por setor.

## 11. Limites explícitos

O protótipo não deve declarar:

- certificação ISO;
- garantia de economia;
- garantia de ROI;
- causalidade ambiental sem evidência;
- precisão estatística que não foi calculada.

O valor do sistema está na rastreabilidade e na capacidade de tornar as hipóteses explícitas, testáveis e reproduzíveis.
