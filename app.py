import math
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from scoring import (
    economic_index,
    technical_feasibility_index,
    environmental_index,
    implementation_complexity_index,
    time_index,
    risk_index,
    ipc,
    ipc_band,
    WEIGHTS_IPC,
    FT_WEIGHTS,
    CI_WEIGHTS,
    GR_WEIGHTS,
    TN_THRESHOLDS,
    ROI_BANDS,
)
from economics import (
    annual_gross_benefit,
    net_annual_benefit,
    simple_payback_months,
    project_roi_percent,
    vitenus_service_roi_percent,
)
from recommendation import recommend
from db import get_client, save_assessment, save_service_request, save_proposal

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

st.set_page_config(page_title="VITENUS Circular Engine", page_icon="♻️", layout="wide", initial_sidebar_state="expanded")

# -----------------------------------------------------------------------------
# Visual system — application-like interface
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root { --vt-green:#0f6b50; --vt-dark:#12352b; --vt-soft:#eef7f3; --vt-border:#d9e6e0; --vt-warn:#fff6df; }
    .block-container {max-width: 1480px; padding-top: 1.4rem; padding-bottom: 3rem;}
    .hero {padding: 1.35rem 1.5rem; border:1px solid var(--vt-border); border-radius:20px; background:linear-gradient(135deg,#f7fcfa 0%,#eef7f3 100%); margin-bottom:1rem;}
    .hero h1 {margin:0; color:var(--vt-dark); font-size:2.0rem;}
    .hero p {margin:.35rem 0 0; color:#557066; font-size:1rem;}
    .eyebrow {font-size:.76rem; letter-spacing:.12em; text-transform:uppercase; font-weight:700; color:var(--vt-green);}
    .card {border:1px solid var(--vt-border); border-radius:16px; padding:1rem 1.05rem; background:white; margin:.35rem 0 .8rem; min-height:120px;}
    .card h3 {margin:.1rem 0 .35rem; color:var(--vt-dark); font-size:1.02rem;}
    .card p {margin:.2rem 0; color:#5f716a; font-size:.9rem; line-height:1.45;}
    .tag {display:inline-block; padding:.22rem .55rem; border-radius:999px; background:var(--vt-soft); color:var(--vt-green); font-size:.72rem; font-weight:700; margin-bottom:.4rem;}
    .why {background:#f8faf9; border-left:4px solid var(--vt-green); padding:.7rem .85rem; border-radius:8px; color:#44574f; margin:.6rem 0 1rem;}
    .formula {background:#10251f; color:#f4fbf7; border-radius:12px; padding:.85rem 1rem; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.88rem; margin:.5rem 0; overflow-x:auto;}
    .stage {padding:.7rem .8rem; border-radius:12px; border:1px solid var(--vt-border); background:#fff; text-align:center; font-size:.8rem; min-height:72px;}
    .stage.active {background:var(--vt-soft); border-color:#9acbb9;}
    .stage .n {font-weight:800; color:var(--vt-green); font-size:.75rem;}
    .stage .t {font-weight:700; color:var(--vt-dark); margin-top:.15rem;}
    .kpi-card {border:1px solid var(--vt-border); border-radius:15px; padding:.85rem 1rem; background:#fff;}
    .muted {color:#6c7d76; font-size:.84rem;}
    .danger-note {background:#fff0ef; border-left:4px solid #b53b32; padding:.75rem .9rem; border-radius:8px;}
    .warning-note {background:var(--vt-warn); border-left:4px solid #c78a13; padding:.75rem .9rem; border-radius:8px;}
    .success-note {background:#edf8f1; border-left:4px solid #2d8758; padding:.75rem .9rem; border-radius:8px;}
    div[data-testid="stMetric"] {background:#fff; border:1px solid var(--vt-border); padding:.65rem .75rem; border-radius:14px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
DEFAULTS = {
    "page": "Demandas em espera",
    "empresa": "Empresa piloto",
    "projeto": "Diagnóstico de circularidade V0.1",
    "oportunidade": "Oportunidade piloto",
    "investment": 100000.0,
    "opex": 5000.0,
    "hurdle": 15.0,
    "months": 6.0,
    "dcs": 80,
    "demanda_status": "Em análise",
    "demanda_origem": "Prospecção / contato inicial",
    "demanda_data": str(date.today()),
    "demanda_resumo": "Empresa industrial busca reduzir perdas materiais e custos associados aos resíduos.",
    "demanda_dor": "Reduzir desperdícios e identificar oportunidades de valorização circular.",
    "demanda_escopo_inicial": "Diagnóstico de matéria-prima, resíduos, perdas e oportunidades circulares.",
    "demanda_dados_disponiveis": "Volume de produção, principais matérias-primas e resíduos; custos ainda parciais.",
    "proposta_aderencia": 75,
    "proposta_dados_minimos": 70,
    "proposta_complexidade": 4,
    "proposta_potencial": 4,
    "proposta_risco": 3,
    "proposta_justificativa": "Há aderência preliminar entre a dor apresentada e o escopo do serviço, mas a proposta deve explicitar as limitações dos dados disponíveis e as informações que serão confirmadas no diagnóstico.",
    "sm": 30000.0, "sw": 10000.0, "se": 5000.0, "swa": 2000.0, "rev": 20000.0, "other": 0.0,
    "production_baseline": 10000.0, "residues_baseline": 1000.0,
    "production_current": 20000.0, "residues_current": 1200.0,
    "consulting_fee": 20000.0,
    "reg": False, "safety": False, "tech": False, "critical": False, "market": True, "supplier": True,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def card(title, text, tag=None):
    tag_html = f'<div class="tag">{tag}</div>' if tag else ""
    st.markdown(f'<div class="card">{tag_html}<h3>{title}</h3><p>{text}</p></div>', unsafe_allow_html=True)


def why(text):
    st.markdown(f'<div class="why"><strong>Por que isso existe?</strong><br>{text}</div>', unsafe_allow_html=True)


def formula(text):
    st.markdown(f'<div class="formula">{text}</div>', unsafe_allow_html=True)


def money(v):
    return f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v):
    return f"{v:.1f}%".replace(".", ",")


def stage_nav():
    stages = [
        ("Demandas em espera", "00", "Demandas em espera"),
        ("Proposta / qualificação", "01", "Proposta / qualificação"),
        ("Cadrage", "02", "Cadrage"),
        ("Diagnóstico industrial", "03", "Diagnóstico industrial"),
        ("Transformação dos dados", "04", "Transformação dos dados"),
        ("Identificação de perdas", "05", "Identificação de perdas"),
        ("Oportunidades circulares", "06", "Oportunidades circulares"),
        ("Priorização", "07", "Priorização"),
        ("Plano + ROI", "08", "Plano + ROI"),
        ("Monitoramento", "09", "Monitoramento"),
        ("Metodologia", "10", "Metodologia"),
        ("Dashboard", "11", "Dashboard"),
        ("Rastreabilidade", "12", "Rastreabilidade"),
    ]
    cols = st.columns(7)
    for i, (label, n, key) in enumerate(stages[:7]):
        with cols[i]:
            active = st.session_state.page == key
            st.markdown(f'<div class="stage {"active" if active else ""}"><div class="n">{n}</div><div class="t">{label}</div></div>', unsafe_allow_html=True)
    cols2 = st.columns(6)
    for i, (label, n, key) in enumerate(stages[7:]):
        with cols2[i]:
            active = st.session_state.page == key
            st.markdown(f'<div class="stage {"active" if active else ""}"><div class="n">{n}</div><div class="t">{label}</div></div>', unsafe_allow_html=True)
    nav = st.radio("Navegação cronológica do serviço", [s[2] for s in stages], index=[s[2] for s in stages].index(st.session_state.page), horizontal=True, label_visibility="collapsed")
    if nav != st.session_state.page:
        st.session_state.page = nav
        st.rerun()


def method_card(code, title, purpose, inputs, outputs, foundation, status):
    with st.container(border=True):
        c1, c2 = st.columns([1, 5])
        c1.markdown(f"### {code}")
        c2.markdown(f"**{title}**\n\n{purpose}")
        d1, d2, d3 = st.columns(3)
        d1.markdown(f"**Entradas**\n\n{inputs}")
        d2.markdown(f"**Saídas**\n\n{outputs}")
        d3.markdown(f"**Fundamento / status**\n\n{foundation}\n\n`{status}`")


# -----------------------------------------------------------------------------
# Global context sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ♻️ VITENUS")
    st.caption("Circular Engine • protótipo metodológico")
    st.divider()
    st.markdown("### Contexto do projeto")
    st.session_state.empresa = st.text_input("Empresa", st.session_state.empresa)
    st.session_state.projeto = st.text_input("Projeto", st.session_state.projeto)
    st.session_state.oportunidade = st.text_input("Oportunidade em análise", st.session_state.oportunidade)
    st.divider()
    st.markdown("### Estado do diagnóstico")
    st.progress(0.18, text="Fluxo cronológico: demanda → proposta → execução")
    st.caption("A interface foi desenhada para guiar o consultor da evidência bruta até a recomendação, sem esconder as hipóteses do modelo.")
    with st.popover("ℹ️ Como usar"):
        st.markdown("""
        **1.** Comece pelas demandas em espera e avance na ordem cronológica.  
        **2.** Na proposta, use somente os dados limitados realmente disponíveis.  
        **3.** Após o aceite, faça o cadrage e a visita/diagnóstico.  
        **4.** Transforme observações em dados, depois perdas e oportunidades.  
        **5.** Só depois pontue e priorize as soluções.  
        **6.** Toda conclusão deverá apontar para dados, fontes e versão metodológica.
        """)

st.markdown('<div class="hero"><div class="eyebrow">VITENUS • ENGINE METODOLÓGICO V0.3</div><h1>Diagnóstico e Valorização Circular</h1><p>Uma interface guiada pela ordem real de execução: demanda em espera → proposta fundamentada com dados limitados → diagnóstico → perdas → oportunidades → priorização → plano de ação → retorno e monitoramento.</p></div>', unsafe_allow_html=True)
stage_nav()

# -----------------------------------------------------------------------------
# Calculations shared by pages
# -----------------------------------------------------------------------------
S = st.session_state
gross = annual_gross_benefit(S.sm, S.sw, S.se, S.swa, S.rev, S.other)
net = net_annual_benefit(gross, S.opex)
roi = project_roi_percent(gross, S.opex, S.investment) if S.investment > 0 else 0.0
payback = simple_payback_months(S.investment, net)
rea = (net / S.investment * 100) if S.investment > 0 else 0.0
ie = economic_index(rea)

# Technical defaults — all are editable on the prioritization page.
ft_inputs = {k: st.session_state.get(f"ft_{k}", 7) for k in FT_WEIGHTS}
ft = technical_feasibility_index(ft_inputs)
imp = {k: st.session_state.get(f"ia_{k}", v) for k, v in {
    "virgin_material_avoided":20.0,"waste_avoided_recovered":30.0,"energy_avoided":10.0,"water_avoided":5.0,"emissions_avoided":15.0}.items()}
ia, ia_raw = environmental_index(imp)
ci_inputs = {k: st.session_state.get(f"ci_{k}", 4) for k in CI_WEIGHTS}
ci = implementation_complexity_index(ci_inputs)
tn = time_index(S.months)
gr_inputs = {k: st.session_state.get(f"gr_{k}", 3) for k in GR_WEIGHTS}
gr = risk_index(gr_inputs)
indices = {"IE":ie,"FT":ft,"IA":ia,"CI":ci,"TN":tn,"GR":gr}
ipc_value = ipc(indices)

# -----------------------------------------------------------------------------
# 00 Demandas em espera
# -----------------------------------------------------------------------------
if S.page == "Demandas em espera":
    st.subheader("00 • Tratamento das demandas em espera")
    st.caption("Primeiro estágio comercial-operacional: registrar, organizar e qualificar as solicitações antes de mobilizar o diagnóstico técnico.")
    why("A demanda em espera é a porta de entrada do serviço. Antes de visitar a fábrica ou construir um Business Case, a VITENUS precisa saber quem solicitou, qual dor foi declarada, qual é o escopo percebido e quais informações já existem. Isso evita iniciar um diagnóstico sem pergunta de negócio definida.")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Status", S.demanda_status)
    c2.metric("Dados iniciais", f"{S.dcs}/100", help="Indicador preliminar de qualidade das informações disponíveis no backlog; não é o DCS final do diagnóstico.")
    c3.metric("Aderência preliminar", f"{S.proposta_aderencia}/100")
    c4.metric("Potencial preliminar", f"{S.proposta_potencial}/5")
    st.markdown("### Ficha da demanda")
    a,b=st.columns(2)
    with a:
        opts=["Em espera","Em análise","Qualificada para proposta","Não aderente","Convertida em projeto"]
        S.demanda_status=st.selectbox("Status da demanda",opts,index=opts.index(S.demanda_status))
        S.demanda_origem=st.text_input("Origem da demanda", S.demanda_origem)
        dt=date.fromisoformat(S.demanda_data) if isinstance(S.demanda_data,str) else S.demanda_data
        S.demanda_data=st.date_input("Data de entrada", value=dt).isoformat()
        S.demanda_resumo=st.text_area("Resumo da solicitação do cliente", S.demanda_resumo)
    with b:
        S.demanda_dor=st.text_area("Dor / problema declarado", S.demanda_dor)
        S.demanda_escopo_inicial=st.text_area("Escopo inicialmente percebido", S.demanda_escopo_inicial)
        S.demanda_dados_disponiveis=st.text_area("Dados já fornecidos pelo cliente", S.demanda_dados_disponiveis)
    st.divider()
    st.markdown("### Fila de demandas")
    queue=pd.DataFrame({
        "ID":["DEM-001","DEM-002","DEM-003"],
        "Empresa":[S.empresa,"Indústria B","Indústria C"],
        "Dor declarada":["Perdas de matéria e resíduos","Custo de destinação","Uso elevado de matéria-prima"],
        "Dados iniciais":["Parciais","Limitados","Parciais"],
        "Status":[S.demanda_status,"Em espera","Em espera"]
    })
    st.data_editor(queue,num_rows="dynamic",use_container_width=True,key="demand_queue")
    st.markdown("### Triagem da demanda selecionada")
    triage=pd.DataFrame({
        "Critério":["Dor de negócio clara","Relação com economia circular","Dados mínimos disponíveis","Escopo potencialmente executável pela VITENUS","Resultado potencialmente mensurável"],
        "Situação":["Sim","Sim","Parcial","Sim","A investigar"],
        "Evidência / observação":["Relato inicial do cliente","Descrição preliminar","Dados fornecidos ainda incompletos","Escopo informado","Hipótese a validar"]
    })
    st.data_editor(triage,num_rows="dynamic",use_container_width=True,key="demand_triage")
    st.info("A triagem não é ainda o diagnóstico. Ela decide se existe informação suficiente para construir uma proposta responsável e quais lacunas precisam ser explicitadas.")
    if st.button("Registrar demanda no Supabase", type="primary", key="save_demand_v03"):
        try:
            client=get_client()
            saved=save_service_request(client,{"company_name":S.empresa,"origin":S.demanda_origem,"received_at":S.demanda_data,"status":S.demanda_status,"summary":S.demanda_resumo,"declared_problem":S.demanda_dor,"initial_scope":S.demanda_escopo_inicial,"initial_data":S.demanda_dados_disponiveis})
            st.session_state["service_request_id"]=saved["id"]
            st.success(f"Demanda registrada: {saved['id']}")
        except Exception as exc:
            st.error(f"Não foi possível registrar a demanda: {exc}")
    st.markdown("### Saída desta etapa")
    cols=st.columns(4)
    for col,(t,b) in zip(cols,[
        ("Demanda registrada","Pedido do cliente estruturado e identificável."),
        ("Problema declarado","Dor de negócio documentada sem tratá-la ainda como causa comprovada."),
        ("Dados disponíveis","Inventário preliminar do que o cliente já consegue fornecer."),
        ("Pronta para proposta","Passagem controlada para a fase de qualificação e proposta.")]):
        with col: card(t,b,"SAÍDA")

# -----------------------------------------------------------------------------
# 01 Proposta / qualificação
# -----------------------------------------------------------------------------
elif S.page == "Proposta / qualificação":
    st.subheader("01 • Proposta e qualificação técnica preliminar")
    st.caption("A proposta usa somente os dados limitados disponíveis antes do diagnóstico para testar aderência, justificar o escopo e explicitar o que ainda precisa ser confirmado.")
    why("Esta fase foi incorporada ao fluxo cronológico: ela não pretende provar o problema. Ela responde se, com as informações disponíveis, existe justificativa suficiente para propor o serviço, quais são suas limitações e o que será confirmado depois.")
    st.markdown("### 1. Matriz de pertinência preliminar")
    st.caption("A proposta não usa o IPC e não tenta quantificar um retorno que ainda não foi diagnosticado. Cada critério é classificado como **Sim / Parcial / Não** com base exclusivamente nas informações disponíveis nesta fase.")
    fit_df=pd.DataFrame({
        "Critério":["A dor declarada é compatível com o serviço?","Há relação clara com matéria, resíduos ou criação de valor circular?","Existem dados suficientes para definir uma investigação?","O escopo parece executável com visita e coleta por processo?","Existe resultado potencial que poderá ser medido depois?"],
        "Situação":["Sim","Sim","Parcial","Sim","A investigar"],
        "Evidência disponível":[S.demanda_dor,"Descrição inicial da demanda",S.demanda_dados_disponiveis,"Escopo preliminar informado","Ainda sem baseline ou medição de desempenho"],
        "Lacuna / ação necessária":["Confirmar causa no diagnóstico","Classificar fluxos e perdas","Solicitar documentos e medições","Definir perímetro no cadrage","Construir baseline e KPI"]
    })
    fit_edit=st.data_editor(fit_df,num_rows="dynamic",use_container_width=True,key="proposal_fit_matrix")
    st.markdown("### Regra de passagem da proposta")
    st.info("**Não há aprovação automática por score.** A proposta é considerada tecnicamente justificável quando não existe uma incompatibilidade crítica conhecida e as lacunas são investigáveis dentro do escopo. Se surgir uma restrição crítica ou falta de dados que impeça a investigação, a proposta deve ser revista antes do aceite.")
    st.markdown("### Sinalização interna")
    p1,p2,p3=st.columns(3)
    with p1: st.metric("Aderência", "Preliminar", help="Não é uma nota de sucesso; é uma conclusão qualitativa baseada na matriz.")
    with p2: st.metric("Evidência", "Limitada", help="Os dados desta fase são pré-diagnóstico.")
    with p3: st.metric("Decisão", "Propor / revisar", help="A decisão final depende da matriz preenchida e das restrições identificadas.")
    st.markdown("### 2. Justificativa da oferta")
    S.proposta_justificativa=st.text_area("Justificativa técnica preliminar",S.proposta_justificativa,min_height=140,help="Explique por que o serviço é pertinente com os dados limitados, quais hipóteses sustentam a proposta e quais pontos serão obrigatoriamente validados.")
    st.markdown("### 3. O que a proposta pode afirmar — e o que não pode afirmar")
    ok,notok=st.columns(2)
    with ok:
        st.success("**Pode afirmar**\n\n• existe aderência preliminar ao serviço;\n• quais perguntas serão investigadas;\n• quais dados serão coletados;\n• qual é o escopo, método e entregável;\n• quais hipóteses serão testadas.")
    with notok:
        st.warning("**Ainda não pode afirmar**\n\n• causa definitiva da perda;\n• economia garantida;\n• ROI garantido;\n• Payback garantido;\n• impacto ambiental definitivo;\n• viabilidade técnica comprovada.")
    st.markdown("### 4. Estrutura da proposta")
    prop=pd.DataFrame({"Bloco":["Problema declarado","Hipótese a investigar","Dados disponíveis","Lacunas de informação","Escopo do diagnóstico","Método de coleta","Entregáveis","Limitações e premissas"],"Conteúdo":[S.demanda_dor,"Perdas e oportunidades circulares podem existir.",S.demanda_dados_disponiveis,"Quantidades, custos, fontes, períodos e evidências precisam ser validados.",S.demanda_escopo_inicial,"Reunião + visita imersiva + coleta por processo.","Diagnóstico + oportunidades + priorização + plano/ROI","Resultados financeiros e ambientais serão condicionados à validação dos dados."]})
    st.data_editor(prop,num_rows="dynamic",use_container_width=True,key="proposal_structure")
    if st.button("Registrar proposta / qualificação no Supabase", type="primary", key="save_proposal_v03"):
        try:
            client=get_client()
            saved=save_proposal(client,{"service_request_id":st.session_state.get("service_request_id"),"company_name":S.empresa,"fit_conclusion":"Propor / revisar","justification":S.proposta_justificativa,"limitations":"Dados limitados; diagnóstico ainda não executado.","scope":S.demanda_escopo_inicial})
            st.session_state["proposal_id"]=saved["id"]
            st.success(f"Proposta registrada: {saved['id']}")
        except Exception as exc:
            st.error(f"Não foi possível registrar a proposta: {exc}")
    st.markdown("### Critério de passagem")
    st.info("Se a proposta for aceita, o sistema avança para o Cadrage. Os dados usados aqui permanecem identificados como **pré-diagnóstico / dados limitados** e não devem ser confundidos com as evidências coletadas durante a execução.")

# -----------------------------------------------------------------------------
# 02 Cadrage
# -----------------------------------------------------------------------------
elif S.page == "Cadrage":
    st.subheader("02 • Cadrage — entender antes de medir")
    st.caption("Baseado na Fase 0 do esqueleto do serviço: reunião inicial, compreensão da empresa, processo, fluxos, agentes, perímetros e objetivos.")
    why("O cadrage reduz o risco de coletar números corretos para a pergunta errada. O escopo precisa ser definido antes da medição para que volumes, custos e indicadores sejam comparáveis e rastreáveis.")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### Empresa e operação")
        S.setor = st.text_input("Setor / atividade", S.get("setor", "Indústria"))
        S.produto = st.text_input("Produto principal", S.get("produto", "Produto piloto"))
        S.volume_producao = st.number_input("Volume de produção no período de referência", min_value=0.0, value=S.get("volume_producao",10000.0), step=100.0)
        S.unidade_producao = st.text_input("Unidade de produção", S.get("unidade_producao","t"))
    with c2:
        st.markdown("### Perímetro")
        S.planta = st.text_input("Planta / unidade", S.get("planta","Unidade piloto"))
        S.processos = st.text_area("Processos / linhas incluídos", S.get("processos","Recebimento → transformação → acabamento → expedição"))
        S.perimetro = st.text_area("Limites do estudo", S.get("perimetro","Do recebimento da matéria-prima ao destino das perdas e resíduos"))
        S.objetivo = st.text_area("Objetivo do diagnóstico", S.get("objetivo","Identificar perdas materiais e econômicas e oportunidades circulares com retorno mensurável."))
    st.divider()
    st.markdown("### Checklist de preparação da visita")
    checklist = [
        "Dados de produção por período disponíveis",
        "Compras / consumo de matérias-primas disponíveis",
        "Custos e contratos de gestão de resíduos disponíveis",
        "Fluxos e pontos de geração identificados",
        "Responsáveis operacionais definidos",
        "Documentos e indicadores existentes listados",
        "Visita imersiva planejada em áreas/turnos relevantes",
    ]
    done = 0
    for item in checklist:
        if st.checkbox(item, key="check_"+item): done += 1
    st.progress(done/len(checklist), text=f"Preparação: {done}/{len(checklist)} itens")
    st.info("O esqueleto do serviço prevê uma visita imersiva, com observação e entrevistas em diferentes áreas. A aplicação deve registrar isso como evidência do diagnóstico, não como simples checklist administrativo.")

# -----------------------------------------------------------------------------
# 02 Diagnóstico
# -----------------------------------------------------------------------------
elif S.page == "Diagnóstico industrial":
    st.subheader("03 • Diagnóstico industrial da matéria-prima")
    st.caption("A etapa central é observar como a matéria entra, é transformada, é segregada e sai do sistema.")
    why("A lógica segue o princípio do MFCA: rastrear fluxos e estoques materiais em unidades físicas e associar custos a esses fluxos. Isso permite enxergar custo de perda que pode ficar invisível na contabilidade convencional.")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Pontos de geração", 4, help="Exemplo de protótipo — substitua pelos pontos observados.")
    c2.metric("Tipos de materiais", 3)
    c3.metric("Fluxos observados", 6)
    c4.metric("Fontes de evidência", 8)
    st.markdown("### Mapa de coleta")
    df = pd.DataFrame({
        "Processo":["Recebimento","Transformação","Acabamento","Expedição"],
        "Entrada física":["Matéria-prima","Material em processo","Produto semiacabado","Produto"],
        "Perda/resíduo observado":["Embalagem","Aparas","Retrabalho","Avarias"],
        "Destino atual":["Reciclagem","Descarte/reciclagem","Retrabalho","Descarte/retorno"],
        "Fonte principal":["NF/ERP","Balança/ERP","Produção/qualidade","Expedição/qualidade"],
    })
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="diagnostic_table")
    st.caption("A tabela é uma representação operacional. Na versão seguinte, cada linha será persistida como fluxo físico com unidade, período, fonte, qualidade e evidência.")
    st.divider()
    cols = st.columns(4)
    for col, (title, body) in zip(cols,[
        ("Pontos de geração","Onde nasce o resíduo ou perda?"),
        ("Quantidade","Quanto é gerado por período? Em qual unidade?"),
        ("Destino","O que acontece com o material hoje?"),
        ("Custo","Quanto custa comprar, movimentar, tratar ou eliminar?"),
    ]):
        with col: card(title,body,"DADO MÍNIMO")

# -----------------------------------------------------------------------------
# 03 Data & baseline
# -----------------------------------------------------------------------------
elif S.page == "Transformação dos dados":
    st.subheader("04 • Transformação de informação em dado auditável")
    st.caption("O objetivo é transformar observações da visita em variáveis com unidade, período, fonte e qualidade.")
    why("Um número sem unidade, período ou fonte não é suficiente para sustentar um cálculo auditável. A aplicação separa dado bruto, transformação e resultado para permitir reprodução.")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### Baseline")
        S.production_baseline = st.number_input("Produção — baseline", min_value=0.0, value=S.production_baseline, step=100.0)
        S.residues_baseline = st.number_input("Resíduos — baseline", min_value=0.0, value=S.residues_baseline, step=10.0)
        S.production_current = st.number_input("Produção — período atual", min_value=0.0, value=S.production_current, step=100.0)
        S.residues_current = st.number_input("Resíduos — período atual", min_value=0.0, value=S.residues_current, step=10.0)
        if S.production_baseline>0 and S.production_current>0:
            ib = S.residues_baseline/S.production_baseline
            ip = S.residues_current/S.production_current
            improvement = (1-ip/ib)*100 if ib>0 else 0
            formula("I_B = X_B / Q_B    •    I_P = X_P / Q_P    •    Melhoria = (I_B − I_P) / I_B × 100")
            st.metric("Intensidade baseline", f"{ib:.4f}")
            st.metric("Intensidade período atual", f"{ip:.4f}")
            st.metric("Melhoria normalizada", pct(improvement))
    with c2:
        st.markdown("### Qualidade da evidência")
        quality = {
            5:"Medição instrumentada / ERP / documento financeiro verificável",
            4:"Documento oficial / registro interno verificável",
            3:"Declaração operacional / registro sem validação independente",
            2:"Estimativa técnica",
            1:"Hipótese de mercado / premissa exploratória",
        }
        q = st.select_slider("Qualidade predominante do conjunto de dados", options=list(quality.keys()), value=int(S.dcs/20) if 1<=int(S.dcs/20)<=5 else 4)
        S.dcs = int((q-1)/4*100)
        st.metric("DCS — confiança de dados", f"{S.dcs}/100")
        st.caption(quality[q])
        st.markdown("**Regra de governança:** DCS é um indicador de qualidade da evidência; não é intervalo estatístico de confiança.")
    st.divider()
    st.markdown("### Registro mínimo de uma observação")
    obs = pd.DataFrame({"Variável":["Resíduos gerados"],"Valor":[S.residues_baseline],"Unidade":["t"],"Período":["12 meses"],"Fonte":["ERP / balança"],"Qualidade":[q],"Verificado":[True]})
    st.data_editor(obs, num_rows="dynamic", use_container_width=True, key="observations")
    st.info("Na arquitetura final, cada observação deve apontar para uma fonte/evidência e uma versão metodológica. Isso implementa a cadeia KPI → fórmula → variável → dado → fonte.")

# -----------------------------------------------------------------------------
# 05 Identificação de perdas
# -----------------------------------------------------------------------------
elif S.page == "Identificação de perdas":
    st.subheader("05 • Identificação e classificação de perdas")
    st.caption("A análise ocorre depois da coleta e transformação dos dados. O objetivo é descobrir onde valor material, econômico, potencial ou estratégico está sendo perdido.")
    why("A perda não é apenas resíduo. Uma matéria-prima comprada e não transformada, um custo de transporte ou tratamento, uma oportunidade de reutilização não capturada ou uma dependência estratégica podem representar formas diferentes de perda.")
    loss_cols = st.columns(4)
    losses=[("Perda de matéria-prima","Material comprado que não se transforma em produto.","Física"),("Perda econômica","Compras, transporte, estoque, tratamento e eliminação associados ao desperdício.","Financeira"),("Perda de potencial","Material que poderia ter segunda utilização ou outro valor.","Circular"),("Perda estratégica","Mercados, fornecedores, simbiose, riscos e conformidade não capturados.","Estratégica")]
    for col,(t,b,tag) in zip(loss_cols,losses):
        with col: card(t,b,tag)
    st.markdown("### Registro das perdas")
    loss_df=pd.DataFrame({"Processo":["Recebimento","Transformação","Acabamento"],"Material/fluxo":["Matéria X","Aparas","Produto fora de especificação"],"Tipo de perda":["Perda econômica","Perda de matéria-prima","Perda de potencial"],"Quantidade/ano":[100,250,50],"Custo associado (R$/ano)":[10000,30000,5000],"Evidência":["ERP/NF","Balança","Qualidade"]})
    st.data_editor(loss_df,num_rows="dynamic",use_container_width=True,key="loss_register")
    st.info("A perda deve permanecer ligada à evidência. Se o valor for estimado, a aplicação deve mostrar explicitamente que se trata de estimativa e não de medição validada.")

# -----------------------------------------------------------------------------
# 06 Oportunidades circulares
# -----------------------------------------------------------------------------
elif S.page == "Oportunidades circulares":
    st.subheader("06 • Identificação de oportunidades circulares")
    st.caption("As perdas identificadas são convertidas em soluções candidatas organizadas por redução, reutilização e valorização.")
    why("Uma oportunidade só faz sentido se responder a uma perda ou causa identificada. A matriz impede que a aplicação gere soluções genéricas desconectadas da realidade observada.")
    st.markdown("### Matriz de oportunidades")
    op_df=pd.DataFrame({"Oportunidade":["Otimização de processo","Reintegração interna","Reciclagem externa"],"Família":["Redução","Reutilização","Valorização"],"Perda atacada":["Perda de matéria","Perda de potencial","Perda econômica"],"Hipótese de valor (R$/ano)":[30000,15000,10000],"Evidência necessária":["Medição de consumo","Teste de qualidade","Cotação/contrato"],"Status":["Hipótese","Hipótese","Hipótese"]})
    st.data_editor(op_df,num_rows="dynamic",use_container_width=True,key="opportunity_matrix")
    cols=st.columns(3)
    for col,(t,b) in zip(cols,[("Redução","Evitar a perda na origem: otimização de processo, redução de consumo, melhoria de rendimento."),("Reutilização","Reintegrar material ou produto em outro ponto do sistema, quando tecnicamente possível."),("Valorização","Dar novo valor ao material: reciclagem externa, simbiose, novos produtos ou mercados.")]):
        with col: card(t,b,"FAMÍLIA")
    st.warning("Valor potencial ainda é hipótese. Antes de entrar no Business Case, deve existir validação técnica, econômica e de mercado suficiente para transformar hipótese em benefício elegível.")

# -----------------------------------------------------------------------------
# 07 Priorização
# -----------------------------------------------------------------------------
elif S.page == "Priorização":
    st.subheader("07 • Priorização multicritério")
    st.caption("Os seis índices transformam dimensões diferentes em uma escala comum de 0–100 para tornar os trade-offs explícitos.")
    why("Uma oportunidade pode ser economicamente atraente e, ao mesmo tempo, tecnicamente difícil ou arriscada. O IPC mantém essas dimensões visíveis. Ele é um modelo de governança V0.1, não uma lei física nem uma classificação ISO.")
    left,right = st.columns(2)
    with left:
        st.markdown("### IE • Impacto Econômico")
        st.metric("IE",f"{ie:.1f}/100")
        st.caption(f"REA = BEN / investimento × 100 = {pct(rea)}. A escala V0.1 converte esse retorno anual em 1–10 e depois ×10.")
        st.markdown("**Faixas V0.1 do REA:** ≤0→1; >0–2→2; >2–5→3; >5–10→4; >10–20→5; >20–35→6; >35–50→7; >50–75→8; >75–100→9; >100→10.")
        st.markdown("### FT • Viabilidade Técnica")
        for k,w in FT_WEIGHTS.items():
            label = {"process_compatibility":"Compatibilidade do processo","technology_maturity":"Maturidade tecnológica","equipment_availability":"Disponibilidade de equipamentos","modification_complexity":"Complexidade das modificações","third_party_dependency":"Dependência de terceiros","pilot_validation_need":"Necessidade de piloto/validação"}[k]
            st.session_state[f"ft_{k}"] = st.slider(label,1,10,int(st.session_state.get(f"ft_{k}",7)),help=f"Peso interno: {w*100:.0f}%")
        ft = technical_feasibility_index({k:st.session_state[f"ft_{k}"] for k in FT_WEIGHTS})
        st.metric("FT",f"{ft:.1f}/100")
    with right:
        st.markdown("### IA • Impacto Ambiental")
        for k,w in {"virgin_material_avoided":.30,"waste_avoided_recovered":.25,"energy_avoided":.15,"water_avoided":.10,"emissions_avoided":.20}.items():
            label={"virgin_material_avoided":"Material virgem evitado (%)","waste_avoided_recovered":"Resíduos evitados/recuperados (%)","energy_avoided":"Energia evitada (%)","water_avoided":"Água evitada (%)","emissions_avoided":"Emissões evitadas (%)"}[k]
            st.session_state[f"ia_{k}"]=st.number_input(label,0.0,100.0,float(st.session_state.get(f"ia_{k}",20.0)),step=1.0,help=f"Peso interno: {w*100:.0f}%. O percentual deve ser derivado de dados físicos e fatores documentados quando aplicável.")
        ia,_=environmental_index({k:st.session_state[f"ia_{k}"] for k in ["virgin_material_avoided","waste_avoided_recovered","energy_avoided","water_avoided","emissions_avoided"]})
        st.metric("IA",f"{ia:.1f}/100")
        st.caption("Os pesos ambientais são hipóteses V0.1. A versão final deve usar quantidades físicas e fatores versionados, evitando atribuir benefício ambiental sem evidência.")
        st.markdown("### CI • Complexidade | TN • Tempo | GR • Risco")
        st.caption("Para CI e GR: 1 = baixo / favorável; 10 = alto / desfavorável. O resultado é invertido para 0–100. Para TN, quanto maior o prazo, menor o índice.")
        for k in CI_WEIGHTS:
            st.session_state[f"ci_{k}"]=st.slider(k.replace("_"," ").title(),1,10,int(st.session_state.get(f"ci_{k}",4)),key=f"cislider_{k}")
        ci=implementation_complexity_index({k:st.session_state[f"ci_{k}"] for k in CI_WEIGHTS})
        st.metric("CI",f"{ci:.1f}/100")
        for k in GR_WEIGHTS:
            st.session_state[f"gr_{k}"]=st.slider("Risco — "+k.title(),1,10,int(st.session_state.get(f"gr_{k}",3)),key=f"grslider_{k}")
        gr=risk_index({k:st.session_state[f"gr_{k}"] for k in GR_WEIGHTS})
        st.metric("GR",f"{gr:.1f}/100")
    tn=time_index(S.months)
    indices={"IE":ie,"FT":ft,"IA":ia,"CI":ci,"TN":tn,"GR":gr}
    ipc_value=ipc(indices)
    st.divider()
    m=st.columns(4)
    m[0].metric("TN",f"{tn:.1f}/100")
    m[1].metric("IPC",f"{ipc_value:.1f}/100")
    m[2].metric("Faixa operacional",ipc_band(ipc_value))
    m[3].metric("DCS",f"{S.dcs}/100")
    formula("IPC = 0,30·IE + 0,20·FT + 0,20·IA + 0,10·CI + 0,10·TN + 0,10·GR")
    st.markdown("### Por que esses pesos?")
    st.write("30% para economia, 20% para viabilidade técnica e 20% para impacto ambiental colocam resultado econômico, possibilidade de execução e efeito ambiental como dimensões centrais. Complexidade, tempo e risco recebem 10% cada para evitar que sejam ignorados. **Isso é uma hipótese de desenho V0.1 e deve ser calibrado com casos reais e análise de sensibilidade.**")
    st.markdown("### Sensibilidade simples ±10% nos pesos")
    sens = []
    base = WEIGHTS_IPC.copy()
    for key in base:
        for delta in (-0.10,0.10):
            w=base.copy(); w[key]=max(0,w[key]*(1+delta)); total=sum(w.values()); w={k:v/total for k,v in w.items()}
            sens.append({"Peso alterado":key,"Variação":f"{delta*100:+.0f}%","IPC":ipc(indices,w)})
    st.dataframe(pd.DataFrame(sens),use_container_width=True,hide_index=True)

# -----------------------------------------------------------------------------
# 06 Business case
# -----------------------------------------------------------------------------
elif S.page == "Plano + ROI":
    st.subheader("08 • Plano de Ação Circular + Business Case, Payback e ROI")
    st.caption("Aqui a hipótese circular vira uma hipótese financeira explícita — com custos, benefícios, horizonte e cenários.")
    why("O Business Case separa benefício bruto, OPEX adicional e investimento. Isso evita misturar economia anual com investimento inicial e permite calcular Payback e ROI de forma transparente.")
    c=st.columns(5)
    S.sm=c[0].number_input("Materiais / ano",0.0,S.sm,step=1000.0)
    S.sw=c[1].number_input("Resíduos / ano",0.0,S.sw,step=1000.0)
    S.se=c[2].number_input("Energia / ano",0.0,S.se,step=500.0)
    S.swa=c[3].number_input("Água / ano",0.0,S.swa,step=500.0)
    S.rev=c[4].number_input("Receita adicional / ano",0.0,S.rev,step=1000.0)
    S.other=st.number_input("Outros benefícios quantificáveis / ano",0.0,S.other,step=500.0)
    S.investment=st.number_input("Investimento total elegível",0.0,S.investment,step=5000.0)
    S.opex=st.number_input("OPEX adicional anual",0.0,S.opex,step=500.0)
    gross=annual_gross_benefit(S.sm,S.sw,S.se,S.swa,S.rev,S.other)
    net=net_annual_benefit(gross,S.opex)
    roi=project_roi_percent(gross,S.opex,S.investment) if S.investment>0 else 0
    payback=simple_payback_months(S.investment,net)
    m=st.columns(4); m[0].metric("BEA",money(gross));m[1].metric("BEN",money(net));m[2].metric("Payback", "∞" if math.isinf(payback) else f"{payback:.1f} meses");m[3].metric("ROI projetado",pct(roi))
    formula("BEA = economias de materiais + resíduos + energia + água + receita adicional + outros benefícios")
    formula("BEN = BEA − OPEX adicional anual")
    formula("ROI projetado = (benefícios − OPEX − investimento) / investimento × 100")
    formula("Payback simples = investimento / (BEN anual / 12)")
    st.markdown("### Cenários")
    scen_df=pd.DataFrame({"Cenário":["Conservador","Central","Otimista"],"Fator de benefício":[0.70,1.00,1.20]})
    scen_df["BEN anual"]=[net*x for x in scen_df["Fator de benefício"]]
    scen_df["Payback (meses)"]=[simple_payback_months(S.investment,x) for x in scen_df["BEN anual"]]
    scen_df["ROI projetado"]=[project_roi_percent(gross*x,S.opex,S.investment) if S.investment>0 else 0 for x in scen_df["Fator de benefício"]]
    st.dataframe(scen_df,use_container_width=True,hide_index=True)
    st.caption("Os fatores 70% / 100% / 120% são convenções de cenário do protótipo, não probabilidades nem garantias. Na versão final, deverão ser alimentados por premissas explícitas de volume, preço, ramp-up e CAPEX.")
    st.markdown("### ROI do projeto ≠ ROI do serviço Vitenus")
    S.consulting_fee=st.number_input("Honorários Vitenus",0.0,S.consulting_fee,step=1000.0)
    service_roi=vitenus_service_roi_percent(gross,S.investment,S.consulting_fee) if S.investment+S.consulting_fee>0 else 0
    cols=st.columns(3); cols[0].metric("ROI projeto",pct(roi)); cols[1].metric("ROI serviço Vitenus",pct(service_roi)); cols[2].metric("ROI realizado","A medir após implementação")
    st.warning("ROI do serviço Vitenus é apenas um cálculo de triagem nesta V0.3. O modelo final deve separar benefícios incrementais atribuíveis ao serviço, custos de implementação e honorários, com regra de atribuição explícita.")
    st.divider()
    st.markdown("### Plano de Ação Circular")
    st.caption("A análise vira execução quando existe uma sequência de implementação, responsável, custo, prazo, KPI e critério de liberação.")
    plan=pd.DataFrame({"Etapa":["Validar causa","Detalhar solução","Orçar CAPEX/OPEX","Piloto","Implantação","Medição"],"Responsável":["Operações","Engenharia","Financeiro","Operações + VITENUS","Operações","Controladoria/Engenharia"],"Prazo (semanas)":[1,2,2,4,8,4],"Custo estimado (R$)":[0,5000,0,10000,80000,5000],"KPI":["Causa confirmada","Projeto validado","Orçamento aprovado","Resultado piloto","Implementação concluída","Benefício realizado"],"Status":["Pendente"]*6})
    st.data_editor(plan,num_rows="dynamic",use_container_width=True,key="action_plan_v03")
    st.markdown("### Gates antes da implementação")
    for text in ["Dados críticos validados","Restrição regulatória verificada","Segurança avaliada","Compatibilidade técnica avaliada","Mercado/fornecedor confirmados","Business Case revisado"]:
        st.checkbox(text,key="gate_v03_"+text)
    st.info("O IPC não substitui gates. Uma solução pode ter score alto e ainda assim permanecer bloqueada até que uma condição crítica seja resolvida.")

# -----------------------------------------------------------------------------
# 07 Action plan
# -----------------------------------------------------------------------------
elif S.page == "__Plano de ação legacy__":
    st.subheader("07 • Plano de Ação Circular")
    st.caption("A recomendação precisa virar execução: ação, responsável, custo, prazo, evidência e KPI.")
    why("O plano é a ponte entre a análise e o resultado real. Sem responsável, prazo, custo e KPI, o diagnóstico não é uma solução implementável.")
    plan=pd.DataFrame({
        "Etapa":["Validar causa","Detalhar solução","Orçar CAPEX/OPEX","Piloto","Implantação","Medição"],
        "Responsável":["Operações","Engenharia","Financeiro","Operações + Vitenus","Operações","Controladoria/Engenharia"],
        "Prazo (semanas)":[1,2,2,4,8,4],
        "Custo estimado (R$)":[0,5000,0,10000,80000,5000],
        "KPI":["Causa confirmada","Projeto validado","Orçamento aprovado","Resultado piloto","Implementação concluída","Benefício realizado"],
        "Status":["Pendente"]*6,
    })
    st.data_editor(plan,num_rows="dynamic",use_container_width=True,key="action_plan")
    st.markdown("### Critérios de liberação")
    for text in ["Dados críticos validados","Restrição regulatória verificada","Segurança avaliada","Compatibilidade técnica avaliada","Mercado/fornecedor confirmados","Business Case revisado"]:
        st.checkbox(text,key="gate_"+text)
    st.info("O IPC não substitui gates. Uma solução pode ter score alto e ainda assim permanecer bloqueada até que uma condição crítica seja resolvida.")

# -----------------------------------------------------------------------------
# 08 Monitoring
# -----------------------------------------------------------------------------
elif S.page == "Monitoramento":
    st.subheader("09 • Monitoramento e ROI realizado")
    st.caption("Depois da implementação, a pergunta muda: o que realmente aconteceu?")
    why("O desempenho realizado deve ser comparado com uma baseline e normalizado por atividade quando necessário. A lógica segue a disciplina de medição: definir referência, medir período de desempenho e documentar variáveis que mudaram.")
    c1,c2=st.columns(2)
    with c1:
        actual_benefit=st.number_input("Benefício econômico observado no período",0.0,5000000.0,net if net>0 else 0.0,step=1000.0)
        actual_opex=st.number_input("OPEX adicional observado",0.0,5000000.0,S.opex,step=500.0)
        actual_invest=st.number_input("Investimento efetivamente realizado",0.0,5000000.0,S.investment,step=5000.0)
    with c2:
        actual_roi=(actual_benefit-actual_opex-actual_invest)/actual_invest*100 if actual_invest>0 else 0
        variance_roi=actual_roi-roi
        st.metric("ROI realizado",pct(actual_roi))
        st.metric("Variação vs projetado",pct(variance_roi))
        st.metric("Realização do benefício",pct(actual_benefit/net*100) if net>0 else "n/a")
    st.markdown("### Cadeia de medição")
    chain=["Baseline","Variável de atividade","Medição real","Ajustes documentados","Benefício calculado","ROI realizado"]
    cols=st.columns(len(chain))
    for i,(col,label) in enumerate(zip(cols,chain)):
        with col: card(f"{i+1:02d}",label,"M&V")
    st.markdown("### KPI de aprendizagem metodológica")
    st.write("Forecast Accuracy, ROI Realization e Payback Accuracy devem ser usados para calibrar a metodologia depois de uma amostra suficiente de projetos.")

# -----------------------------------------------------------------------------
# 09 Methodology
# -----------------------------------------------------------------------------
elif S.page == "Metodologia":
    st.subheader("10 • Metodologia explicada — o manual dentro do programa")
    st.caption("Esta tela existe para que o consultor entenda o motivo de cada campo e de cada cálculo antes de usar o resultado.")
    st.markdown("### 1. O que é normativo e o que é proprietário?")
    st.markdown("""
    **Base técnica:** MFCA e economia circular orientam o problema e a disciplina de medição. A ISO 14051 estrutura o rastreamento físico e monetário dos fluxos materiais; a ISO 14053 trata da implementação faseada; ISO 59004 fornece princípios e vocabulário de economia circular; ISO 59010 trata da transição de modelos de criação de valor e redes; ISO 59020 estrutura a medição e avaliação da circularidade em um sistema definido.  
    **Proprietário VITENUS V0.1:** pesos, escalas 1–10, faixas do IE, limiares de tempo, faixas de ROI, bandas do IPC e regras de governança. Essas escolhas não são apresentadas como limites das normas.
    """)
    st.markdown("### 2. Por que existe uma fase de proposta antes do diagnóstico?")
    st.write("A proposta é uma etapa de qualificação anterior à execução técnica. Ela utiliza somente as informações que o cliente consegue fornecer naquele momento para verificar aderência, definir o escopo proposto, identificar lacunas e fortalecer a justificativa da contratação. Ela não deve ser confundida com o diagnóstico industrial: causas, perdas, benefícios, ROI e Payback permanecem hipóteses até serem sustentados pelos dados coletados durante a execução.")
    st.markdown("### 3. Ordem cronológica de execução do serviço")
    formula("DEMANDA EM ESPERA → PROPOSTA / QUALIFICAÇÃO → CADRAGE → DIAGNÓSTICO INDUSTRIAL → TRANSFORMAÇÃO DOS DADOS → IDENTIFICAÇÃO DE PERDAS → OPORTUNIDADES CIRCULARES → PRIORIZAÇÃO → PLANO + BUSINESS CASE + PAYBACK + ROI → IMPLEMENTAÇÃO → MONITORAMENTO → ROI REALIZADO")
    st.markdown("### 4. Pipeline de dados interno")
    formula("EMPRESA → PROJETO → PROCESSO → FLUXO → DADO → BASELINE → PERDA → OPORTUNIDADE → SOLUÇÃO → 6 ÍNDICES → IPC → BUSINESS CASE → PAYBACK → ROI → PLANO → IMPLEMENTAÇÃO → MEDIÇÃO → ROI REALIZADO")
    st.divider()
    method_card("M00","Demanda em espera","Registra a solicitação, dor declarada, dados disponíveis e escopo percebido.","demanda, dor, origem, dados iniciais, escopo preliminar","ficha de demanda e triagem","governança comercial e preparação do serviço","processo VITENUS")
    method_card("M01","Proposta / qualificação","Testa a aderência preliminar da oferta usando dados limitados, sem confundir hipótese com diagnóstico.","dor declarada, dados limitados, aderência, lacunas, riscos preliminares","proposta, justificativa, escopo, premissas e limitações","etapa proprietária do fluxo cronológico; não é diagnóstico nem previsão financeira","processo VITENUS")
    method_card("M02","Cadrage","Define sistema, fronteiras, objetivos e perguntas.","empresa, planta, produto, processo, período, perímetro","escopo e plano de coleta","disciplina de definição de fronteira; necessária para comparabilidade","fundamento técnico")
    method_card("M03","MFCA / fluxo material","Rastreia materiais e custos por fluxo/processo.","massa/volume, consumo, resíduos, custos, destinos","fluxos físicos + custos associados","ISO 14051 e ISO 14053","referencial normativo")
    method_card("M04","Baseline","Define o estado de referência contra o qual a mudança será comparada.","X_B, Q_B, período e variáveis independentes","intensidade de referência","disciplina de medição e verificação; ajuste por atividade quando necessário","referencial de M&V")
    method_card("M05","Perdas","Classifica onde valor material/econômico/potencial/estratégico é perdido.","fluxos, custos, destinos, observações","perdas quantificadas e hipóteses","estrutura do serviço Vitenus","proprietário")
    method_card("M06","Oportunidades","Converte perdas em ações de redução, reutilização ou valorização.","causa + fluxo + restrições","soluções candidatas","economia circular + lógica do serviço","proprietário")
    method_card("M07","Seis índices","Cria visão multicritério da solução.","retorno, ratings técnicos, impactos, complexidade, tempo, risco","IE, FT, IA, CI, TN, GR","modelo de decisão multicritério interno","hipótese V0.1")
    method_card("M08","IPC","Combina os seis índices em uma pontuação 0–100.","IE, FT, IA, CI, TN, GR + pesos","IPC e faixa operacional","modelo de governança interno; sensibilidade obrigatória","hipótese V0.1")
    method_card("M09","Business Case","Traduz a solução em economia anual e investimento.","benefícios, OPEX, CAPEX/custos elegíveis","BEA, BEN, ROI, Payback","análise financeira do projeto","modelo financeiro")
    method_card("M10","M&V / ROI realizado","Compara projeção e resultado observado.","baseline, período de desempenho, medição, ajustes","benefício realizado, ROI realizado, variâncias","princípios de medição e verificação","monitoramento")
    st.divider()
    st.markdown("### 5. Dicionário das variáveis e por que cada uma existe")
    var_df=pd.DataFrame([
        ["IE","Impacto Econômico","0–100","retorno econômico anual normalizado","capturar valor financeiro"],
        ["FT","Viabilidade Técnica","0–100","rating ponderado 1–10","avaliar possibilidade de execução"],
        ["IA","Impacto Ambiental","0–100","melhorias ambientais normalizadas","capturar efeito ambiental"],
        ["CI","Complexidade de Implementação","0–100","rating invertido 1–10","penalizar esforço organizacional/técnico"],
        ["TN","Tempo Necessário","0–100","meses → score","penalizar demora"],
        ["GR","Grau de Risco","0–100","rating invertido 1–10","penalizar exposição"],
        ["DCS","Confiança dos Dados","0–100","qualidade 1–5 escalada","qualificar a força da evidência"],
        ["IPC","Prioridade Circular","0–100","combinação ponderada","apoiar priorização"],
        ["BEA","Benefício Econômico Anual Bruto","R$/ano","soma das fontes de benefício","mostrar valor bruto"],
        ["BEN","Benefício Econômico Anual Líquido","R$/ano","BEA − OPEX adicional","mostrar benefício após OPEX"],
        ["Payback","Tempo de recuperação","meses","investimento / benefício mensal","mostrar velocidade de recuperação"],
        ["ROI","Retorno do projeto","%","(benefícios − OPEX − investimento)/investimento","comparar retorno econômico do projeto"],
    ],columns=["Código","Variável","Escala","Como nasce","Por que existe"])
    st.dataframe(var_df,use_container_width=True,hide_index=True)
    st.markdown("### 6. Números que NÃO devem ser tratados como verdades universais")
    st.warning("Pesos 30/20/20/10/10/10; faixas do IE; pesos internos de FT/IA; igualdade de pesos em CI/GR; limiares de TN; faixas de ROI; bandas do IPC; DCS <60 como alerta; e cenários 70/100/120% são hipóteses de V0.1. A versão metodológica final deve submetê-los a testes de sensibilidade, concordância entre avaliadores, calibração com projetos reais e análise de incerteza.")
    st.markdown("### 7. Referenciais externos consultados")
    st.markdown("- ISO 14051: MFCA — fluxos e estoques materiais em unidades físicas e custos associados.")
    st.markdown("- ISO 14053: implementação faseada do MFCA.")
    st.markdown("- ISO 59004: princípios e vocabulário de economia circular.")
    st.markdown("- ISO 59010: transição de modelos de criação de valor e redes de valor.")
    st.markdown("- ISO 59020: medição e avaliação da circularidade em sistema definido.")
    st.info("A aplicação não afirma conformidade/certificação ISO. Ela usa os referenciais como base conceitual e mantém as decisões proprietárias explicitamente separadas.")

# -----------------------------------------------------------------------------
# 10 Dashboard
# -----------------------------------------------------------------------------
elif S.page == "Dashboard":
    st.subheader("11 • Dashboard executivo")
    st.caption("O dashboard é a saída visual do motor; ele não é a entrada do diagnóstico.")
    d1,d2,d3=st.columns(3)
    d1.metric("IPC",f"{ipc_value:.1f}/100"); d2.metric("ROI projetado",pct(roi)); d3.metric("Payback", "∞" if math.isinf(payback) else f"{payback:.1f} meses")
    df_idx=pd.DataFrame({"Índice":list(indices.keys()),"Pontuação":list(indices.values())})
    fig=px.bar(df_idx,x="Índice",y="Pontuação",range_y=[0,100],text_auto=".0f",title="Seis índices — leitura multicritério")
    fig.update_layout(height=430,margin=dict(l=20,r=20,t=55,b=20))
    st.plotly_chart(fig,use_container_width=True)
    econ=pd.DataFrame({"Fonte":["Materiais","Resíduos","Energia","Água","Receita","Outros"],"Valor":[S.sm,S.sw,S.se,S.swa,S.rev,S.other]})
    fig2=px.bar(econ,x="Fonte",y="Valor",text_auto=".0f",title="Composição do benefício econômico anual bruto")
    st.plotly_chart(fig2,use_container_width=True)
    st.markdown("### Leitura executiva")
    st.markdown(f'<div class="success-note"><strong>{S.empresa}</strong> • {S.oportunidade}<br>BEN anual: <strong>{money(net)}</strong> • ROI projetado: <strong>{pct(roi)}</strong> • Payback: <strong>{"sem recuperação no modelo" if math.isinf(payback) else f"{payback:.1f} meses"}</strong> • IPC: <strong>{ipc_value:.1f}/100</strong>.<br><span class="muted">A interpretação deve considerar DCS, gates de governança, riscos e sensibilidade.</span></div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 11 Supabase
# -----------------------------------------------------------------------------
elif S.page == "Rastreabilidade":
    st.subheader("12 • Rastreabilidade, Supabase e versão")
    st.caption("A base não é apenas armazenamento: ela deve preservar a história de como cada resultado foi produzido.")
    formula("KPI → fórmula → variável → unidade → período → observação → fonte/evidência → responsável → versão metodológica")
    trace={"indices":indices,"weights":WEIGHTS_IPC,"formula_version":"VITENUS-METHODOLOGY-0.3","interface_language":"pt-BR","company":S.empresa,"project":S.projeto}
    st.json(trace)
    if st.button("Salvar avaliação no Supabase",type="primary"):
        try:
            client=get_client()
            decision=recommend(ipc_value,roi,payback,S.dcs,S.hurdle,S.reg,S.safety,S.tech,S.critical,S.market,S.supplier)
            payload={**indices,"IPC":ipc_value,"recommendation":decision["decision"],"trace":trace}
            result=save_assessment(client,S.empresa,S.projeto,S.oportunidade,payload,roi,payback,S.dcs)
            st.success(f"Avaliação salva. Score ID: {result[3]['id']}")
        except Exception as exc:
            st.error(f"Não foi possível salvar no Supabase: {exc}")
    st.divider()
    st.markdown("### Versão")
    st.info(f"VITENUS-METHODOLOGY-0.3 • Interface pt-BR • {date.today().isoformat()}")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.divider()
st.caption("VITENUS Circular Engine V0.3 • Protótipo de pesquisa aplicada • Pesos, escalas e faixas proprietárias em validação • Não representa certificação ISO nem garantia de retorno.")
