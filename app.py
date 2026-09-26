import streamlit as st
from datetime import date
import math
import pandas as pd
import plotly.express as px

from scoring import (
    economic_index,
    technical_feasibility_index,
    environmental_index,
    implementation_complexity_index,
    time_index,
    risk_index,
    ipc,
    ipc_band,
)
from economics import (
    annual_gross_benefit,
    net_annual_benefit,
    simple_payback_months,
    project_roi_percent,
    vitenus_service_roi_percent,
)
from recommendation import recommend
from db import get_client, save_assessment

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Vitenus Circular Engine", page_icon="♻️", layout="wide")

# -----------------------------
# Identidade visual / textos
# -----------------------------
st.markdown(
    """
    <style>
    .vitenus-subtitle {font-size: 1.05rem; opacity: .78; margin-bottom: 1rem;}
    .method-card {padding: 1rem; border: 1px solid rgba(128,128,128,.25); border-radius: 12px; margin-bottom: .75rem;}
    .small-note {font-size: .85rem; opacity: .75;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("VITENUS Circular Engine — V0.1")
st.markdown(
    '<div class="vitenus-subtitle">Protótipo de pesquisa aplicada — resultados a validar com dados-piloto.</div>',
    unsafe_allow_html=True,
)

# -----------------------------
# Seleção de empresa / projeto
# -----------------------------
st.sidebar.header("Contexto do projeto")
empresas_demo = ["Caso fictício 01", "Caso fictício 02", "Empresa piloto"]
empresa = st.sidebar.selectbox("Empresa", empresas_demo + ["+ Nova empresa"])
if empresa == "+ Nova empresa":
    empresa = st.sidebar.text_input("Nome da nova empresa", "") or "Nova empresa"

projeto = st.sidebar.text_input("Projeto", "Diagnóstico de circularidade V0.1")
opportunity_name = st.sidebar.text_input("Oportunidade", "Oportunidade piloto")

# -----------------------------
# Dados econômicos
# -----------------------------
st.sidebar.header("Parâmetros econômicos")
investment = st.sidebar.number_input("Investimento total (R$)", min_value=0.0, value=100000.0, step=5000.0)
opex = st.sidebar.number_input("OPEX adicional anual (R$)", min_value=0.0, value=5000.0, step=500.0)
hurdle = st.sidebar.number_input("Taxa mínima de retorno — hurdle rate (%)", min_value=-100.0, value=15.0, step=1.0)
months = st.sidebar.number_input("Tempo de implementação (meses)", min_value=0.0, value=6.0, step=1.0)
dcs = st.sidebar.slider("Índice de Confiança dos Dados — DCS", 0, 100, 80)

# -----------------------------
# Abas principais
# -----------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. Dados e Business Case",
    "2. Metodologia",
    "3. Seis Índices",
    "4. Payback e ROI",
    "5. Recomendação",
    "6. Dashboard",
    "7. Supabase e rastreabilidade",
])

# -----------------------------
# 1. Dados e Business Case
# -----------------------------
with tab1:
    st.header("Dados de entrada e Business Case")
    st.caption("Os valores abaixo são entradas do protótipo. Em uma execução real, cada variável deverá estar vinculada a uma fonte, unidade, período e evidência.")

    c = st.columns(5)
    sm = c[0].number_input("Economia de materiais/ano (R$)", min_value=0.0, value=30000.0, step=1000.0)
    sw = c[1].number_input("Economia com resíduos/ano (R$)", min_value=0.0, value=10000.0, step=1000.0)
    se = c[2].number_input("Economia de energia/ano (R$)", min_value=0.0, value=5000.0, step=500.0)
    swa = c[3].number_input("Economia de água/ano (R$)", min_value=0.0, value=2000.0, step=500.0)
    rev = c[4].number_input("Receita adicional/ano (R$)", min_value=0.0, value=20000.0, step=1000.0)

    other = st.number_input("Outros benefícios econômicos quantificáveis/ano (R$)", min_value=0.0, value=0.0, step=500.0)
    gross = annual_gross_benefit(sm, sw, se, swa, rev, other)
    net = net_annual_benefit(gross, opex)
    roi = project_roi_percent(gross, opex, investment) if investment > 0 else 0.0
    payback = simple_payback_months(investment, net)

    metrics = st.columns(4)
    metrics[0].metric("Benefício Econômico Anual Bruto — BEA", f"R$ {gross:,.0f}")
    metrics[1].metric("Benefício Econômico Anual Líquido — BEN", f"R$ {net:,.0f}")
    metrics[2].metric("ROI projetado do projeto", f"{roi:.1f}%")
    metrics[3].metric("Payback simples", "∞" if math.isinf(payback) else f"{payback:.1f} meses")

    st.subheader("Dados físicos para normalização da baseline")
    pcols = st.columns(4)
    producao_baseline = pcols[0].number_input("Produção — baseline", min_value=0.0, value=10000.0)
    residuos_baseline = pcols[1].number_input("Resíduos — baseline (t)", min_value=0.0, value=1000.0)
    producao_real = pcols[2].number_input("Produção — período atual", min_value=0.0, value=20000.0)
    residuos_real = pcols[3].number_input("Resíduos — período atual (t)", min_value=0.0, value=1200.0)

    if producao_baseline > 0 and producao_real > 0:
        intensidade_base = residuos_baseline / producao_baseline
        intensidade_real = residuos_real / producao_real
        melhoria = (1 - intensidade_real / intensidade_base) * 100 if intensidade_base > 0 else 0.0
        st.info(f"Intensidade de resíduos: baseline = {intensidade_base:.4f} t/t; período atual = {intensidade_real:.4f} t/t; melhoria normalizada = {melhoria:.1f}%.")

# -----------------------------
# 2. Metodologia
# -----------------------------
with tab2:
    st.header("Metodologia Vitenus")
    st.markdown("""
    ### Objetivo
    Transformar dados operacionais e econômicos em diagnóstico, oportunidades circulares, priorização, Business Case, Payback, ROI e monitoramento de desempenho.

    ### Cadeia metodológica
    **Dados → Medição → Baseline → Diagnóstico → Oportunidades → Seis Índices → IPC → Business Case → Payback → Implementação → Medição → ROI realizado → KPI.**

    ### Referenciais utilizados no protótipo
    - **ISO 14051 / MFCA:** fluxos físicos de materiais associados a custos.
    - **ISO 14053:** implementação faseada do MFCA.
    - **ISO 59004:** princípios e vocabulário de economia circular.
    - **ISO 59010:** modelos de negócio e redes de valor circulares.
    - **ISO 59020:** medição e avaliação da circularidade.
    - **ISO 14007:** determinação de custos e benefícios ambientais.
    - **ISO 14031:** avaliação de desempenho ambiental e indicadores.
    - **ISO 50015:** princípios de medição e verificação de desempenho energético, quando aplicável.

    > **Nota:** os pesos, escalas, faixas de classificação e regras de decisão do Vitenus V0.1 são hipóteses metodológicas proprietárias para teste-piloto. Eles não são pesos ou limites estabelecidos pelas normas ISO.
    """)

    with st.expander("Arquitetura dos seis índices", expanded=True):
        st.markdown("""
        | Código | Índice | Natureza | Peso inicial |
        |---|---|---|---:|
        | IE | Impacto Econômico | benefício | 30% |
        | FT | Viabilidade Técnica | benefício | 20% |
        | IA | Impacto Ambiental | benefício | 20% |
        | CI | Complexidade de Implementação | custo | 10% |
        | TN | Tempo Necessário | custo | 10% |
        | GR | Grau de Risco | custo | 10% |
        """)

    with st.expander("Regras de qualidade dos dados"):
        st.markdown("""
        **Nível 5:** medição instrumentada, ERP ou documento financeiro verificável.

        **Nível 4:** documento oficial ou registro interno verificável.

        **Nível 3:** declaração operacional ou registro sem validação independente.

        **Nível 2:** estimativa técnica.

        **Nível 1:** hipótese de mercado ou premissa exploratória.

        O DCS é um indicador de governança da qualidade dos dados; ele **não é um intervalo estatístico de confiança**.
        """)

# -----------------------------
# 3. Seis índices
# -----------------------------
with tab3:
    st.header("Seis Índices e Índice de Priorização Circular")

    left, right = st.columns(2)
    with left:
        st.subheader("IE — Impacto Econômico")
        rea = (net / investment * 100) if investment > 0 else 0.0
        ie = economic_index(rea)
        st.metric("IE", f"{ie:.1f}/100")
        st.caption("A escala V0.1 usa o retorno econômico anual como variável principal. Os limites devem ser calibrados com casos-piloto.")

        st.subheader("FT — Viabilidade Técnica")
        ft_labels = [
            ("Compatibilidade do processo", "process_compatibility"),
            ("Maturidade tecnológica", "technology_maturity"),
            ("Disponibilidade dos equipamentos", "equipment_availability"),
            ("Complexidade das modificações", "modification_complexity"),
            ("Dependência de terceiros", "third_party_dependency"),
            ("Necessidade de piloto/validação", "pilot_validation_need"),
        ]
        ft_inputs = {k: st.slider(label, 1, 10, 7, key=f"ft_{k}") for label, k in ft_labels}
        ft = technical_feasibility_index(ft_inputs)
        st.metric("FT", f"{ft:.1f}/100")

        st.subheader("IA — Impacto Ambiental")
        imp = {}
        for label, key, val in [
            ("Material virgem evitado (%)", "virgin_material_avoided", 20.0),
            ("Resíduos evitados/recuperados (%)", "waste_avoided_recovered", 30.0),
            ("Energia evitada (%)", "energy_avoided", 10.0),
            ("Água evitada (%)", "water_avoided", 5.0),
            ("Emissões evitadas (%)", "emissions_avoided", 15.0),
        ]:
            imp[key] = st.number_input(label, min_value=0.0, max_value=100.0, value=val, key=f"ia_{key}")
        ia, ia_raw = environmental_index(imp)
        st.metric("IA", f"{ia:.1f}/100")

    with right:
        st.subheader("CI — Complexidade de Implementação")
        ci_labels = [
            ("Departamentos envolvidos", "departments"),
            ("Mudanças no processo", "process_changes"),
            ("Complexidade de fornecedores", "suppliers"),
            ("Complexidade de parceiros", "partners"),
            ("Complexidade do CAPEX", "capex_complexity"),
            ("Parada de produção", "production_downtime"),
            ("Mudança organizacional", "organizational_change"),
        ]
        ci_inputs = {k: st.slider(label, 1, 10, 4, key=f"ci_{k}") for label, k in ci_labels}
        ci = implementation_complexity_index(ci_inputs)
        st.metric("CI", f"{ci:.1f}/100")
        st.caption("Quanto maior a complexidade de implementação, menor o índice CI.")

        st.subheader("TN — Tempo Necessário")
        tn = time_index(months)
        st.metric("TN", f"{tn:.1f}/100")
        st.caption("Quanto maior o prazo de implementação, menor o índice TN.")

        st.subheader("GR — Grau de Risco")
        gr_labels = [
            ("Técnico", "technical"), ("Financeiro", "financial"),
            ("Operacional", "operational"), ("Regulatório", "regulatory"),
            ("Mercado", "market"), ("Fornecedor", "supplier"), ("Qualidade", "quality")
        ]
        gr_inputs = {k: st.slider(label, 1, 10, 3, key=f"gr_{k}") for label, k in gr_labels}
        gr = risk_index(gr_inputs)
        st.metric("GR", f"{gr:.1f}/100")
        st.caption("Quanto maior o risco, menor o índice GR.")

    indices = {"IE": ie, "FT": ft, "IA": ia, "CI": ci, "TN": tn, "GR": gr}
    ipc_value = ipc(indices)

    st.divider()
    st.subheader("IPC — Índice de Priorização Circular")
    st.metric("IPC", f"{ipc_value:.1f}/100")
    st.write(f"Classificação operacional V0.1: **{ipc_band(ipc_value)}**")
    st.caption("As faixas são regras operacionais do protótipo e deverão ser calibradas após testes-piloto.")

# -----------------------------
# 4. Payback e ROI
# -----------------------------
with tab4:
    st.header("Payback e ROI")
    st.subheader("Payback projetado")
    st.write("O Payback projetado é uma estimativa anterior à implementação. Ele não representa uma garantia de retorno.")

    scenario = st.selectbox("Cenário", ["Conservador", "Central", "Otimista"])
    factors = {"Conservador": 0.70, "Central": 1.00, "Otimista": 1.20}
    factor = factors[scenario]
    scenario_net = net * factor
    scenario_payback = simple_payback_months(investment, scenario_net)
    scenario_roi = project_roi_percent(gross * factor, opex, investment) if investment > 0 else 0.0

    sc = st.columns(3)
    sc[0].metric("Benefício líquido anual ajustado", f"R$ {scenario_net:,.0f}")
    sc[1].metric("Payback projetado", "∞" if math.isinf(scenario_payback) else f"{scenario_payback:.1f} meses")
    sc[2].metric("ROI projetado", f"{scenario_roi:.1f}%")

    st.subheader("Distinção entre os retornos")
    st.markdown("""
    - **ROI do projeto:** mede o retorno econômico da solução industrial implementada.
    - **ROI do serviço Vitenus:** mede o retorno incremental associado à contratação do serviço de consultoria, considerando benefícios incrementais, custos de implementação atribuíveis e honorários.
    - **ROI realizado:** calculado depois da implementação, usando dados observados e a baseline definida.
    - **ROI acumulado:** acompanha a evolução do retorno ao longo dos períodos de monitoramento.
    """)

    consulting_fee = st.number_input("Honorários Vitenus (R$)", min_value=0.0, value=20000.0, step=1000.0)
    service_roi = vitenus_service_roi_percent(gross, investment, consulting_fee) if investment + consulting_fee > 0 else 0.0
    st.metric("ROI do serviço Vitenus — cenário atual", f"{service_roi:.1f}%")

    st.subheader("Limites de interpretação do ROI")
    st.markdown("""
    O protótipo utiliza faixas de governança para apoiar a análise:

    - ROI < 0% → retorno negativo no horizonte/modelo utilizado;
    - 0% a <10% → retorno positivo baixo;
    - 10% a <20% → retorno positivo;
    - 20% a <35% → retorno elevado;
    - ≥35% → retorno muito elevado.

    **Essas faixas são hipóteses de governança V0.1, não padrões universais de investimento.**
    """)

# -----------------------------
# 5. Recomendação / governança
# -----------------------------
with tab5:
    st.header("Recomendação e governança")
    st.caption("O IPC não é o único mecanismo de decisão. Bloqueios regulatórios, de segurança, técnicos ou de mercado podem impedir uma recomendação.")

    reg = st.checkbox("Restrição/bloqueio regulatório")
    safety = st.checkbox("Restrição de segurança")
    tech = st.checkbox("Incompatibilidade técnica")
    critical = st.checkbox("Risco crítico")
    market = st.checkbox("Mercado disponível", True)
    supplier = st.checkbox("Fornecedor disponível", True)

    decision = recommend(ipc_value, roi, payback, dcs, hurdle, reg, safety, tech, critical, market, supplier)
    translations = {
        "blocked": "bloqueado por governança",
        "pilot_data_insufficient": "dados-piloto insuficientes",
        "economic_review": "revisão econômica necessária",
        "no_payback_within_model_horizon": "sem Payback no horizonte modelado",
        "low_priority": "baixa prioridade operacional",
        "conditional_priority": "prioridade condicional",
        "high_priority": "alta prioridade operacional",
        "immediate_priority": "prioridade imediata operacional",
    }
    st.subheader("Resultado")
    st.metric("Decisão operacional", translations.get(decision["decision"], decision["decision"]))
    st.json({
        "IPC": round(ipc_value, 2),
        "faixa_IPC": ipc_band(ipc_value),
        "ROI_projetado_%": round(roi, 2),
        "Payback_meses": None if math.isinf(payback) else round(payback, 2),
        "DCS": dcs,
        "atende_hurdle_rate": decision["roi_meets_hurdle_rate"],
        "bloqueadores": decision["blockers"],
        "alertas": decision["warnings"],
    })

# -----------------------------
# 6. Dashboard
# -----------------------------
with tab6:
    st.header("Dashboard do projeto")
    df_indices = pd.DataFrame({"Índice": list(indices.keys()), "Pontuação": list(indices.values())})
    fig = px.bar(df_indices, x="Índice", y="Pontuação", range_y=[0, 100], title="Seis Índices Vitenus")
    st.plotly_chart(fig, use_container_width=True)

    econ_df = pd.DataFrame({
        "Categoria": ["Materiais", "Resíduos", "Energia", "Água", "Receita adicional", "Outros"],
        "Valor (R$)": [sm, sw, se, swa, rev, other],
    })
    fig2 = px.bar(econ_df, x="Categoria", y="Valor (R$)", title="Composição do benefício econômico anual bruto")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Resumo executivo")
    st.write(
        f"Para **{empresa}**, o protótipo estima um benefício bruto anual de **R$ {gross:,.0f}**, "
        f"benefício líquido anual de **R$ {net:,.0f}**, ROI projetado de **{roi:.1f}%**, "
        f"Payback de **{'infinito' if math.isinf(payback) else f'{payback:.1f} meses'}** e IPC de **{ipc_value:.1f}/100**."
    )

# -----------------------------
# 7. Supabase / rastreabilidade
# -----------------------------
with tab7:
    st.header("Supabase e rastreabilidade")
    st.markdown("""
    A rastreabilidade planejada segue a cadeia:

    **KPI → fórmula → variável → unidade → período → observação → fonte/evidência → responsável → versão metodológica.**

    A aplicação usa as tabelas criadas pelo SQL V0.1. Os scripts SQL não precisam ser executados novamente apenas por causa da tradução da interface.
    """)

    st.subheader("Salvar avaliação")
    if st.button("Salvar cálculo no Supabase", type="primary"):
        try:
            client = get_client()
            trace = {
                "indices": indices,
                "weights": {"IE": .30, "FT": .20, "IA": .20, "CI": .10, "TN": .10, "GR": .10},
                "formula_version": "VITENUS-METHODOLOGY-0.1",
                "interface_language": "pt-BR",
                "company": empresa,
            }
            payload = {
                **indices,
                "IPC": ipc_value,
                "recommendation": translations.get(decision["decision"], decision["decision"]),
                "trace": trace,
            }
            result = save_assessment(client, empresa, projeto, opportunity_name, payload, roi, payback, dcs)
            st.success(f"Cálculo salvo com sucesso. ID do score: {result[3]['id']}")
        except Exception as exc:
            st.error(f"Não foi possível salvar no Supabase: {exc}")

    st.subheader("Versão")
    st.info(f"VITENUS-METHODOLOGY-0.1 • Interface pt-BR • {date.today().isoformat()}")
