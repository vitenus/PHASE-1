import json, math
from datetime import date
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

from economics import annual_gross_benefit, net_annual_benefit, simple_payback_months, project_roi_percent, vitenus_service_roi_percent, projected_payback_periods
from scoring import economic_index, technical_feasibility_index, environmental_index, implementation_complexity_index, time_index, risk_index, ipc, ipc_band, FT_WEIGHTS, CI_WEIGHTS, GR_WEIGHTS
from db import get_client, save_assessment, save_service_request, save_proposal, save_workspace

st.set_page_config(page_title="VITENUS | Circular Engine", page_icon="◉", layout="wide", initial_sidebar_state="expanded")

# ----------------------------- Visual system -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{color-scheme:light;--ink:#17231f;--muted:#68756f;--line:#dfe7e2;--soft:#f5f8f6;--surface:#ffffff;--surface-2:#f8faf9;--deep:#12352c;--mint:#dff3e9;--lime:#bde56d;--accent:#2f8f6b;--gold:#e7b84b;--danger:#c95858;--input:#ffffff;--input-text:#17231f;--shadow:rgba(20,40,32,.06)}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink)}
html,body{background:var(--surface);color:var(--ink)}
body{color-scheme:light}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif;letter-spacing:-.03em;color:var(--ink)}
.block-container{padding-top:1.1rem;padding-bottom:4rem;max-width:1500px}
[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"] .main{background:var(--surface);color:var(--ink)}
[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#102f28 0%,#0b241f 100%)}
[data-testid="stSidebar"] *{color:#eaf4ef!important}
[data-testid="stSidebar"] .stButton button{border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.05);text-align:left;border-radius:12px}
[data-testid="stSidebar"] .stButton button:hover{background:rgba(189,229,109,.14);border-color:rgba(189,229,109,.4)}
.hero{background:radial-gradient(circle at 85% 10%,rgba(189,229,109,.24),transparent 28%),linear-gradient(135deg,#12352c,#1b5a47);border-radius:28px;padding:34px 38px;color:#fff;box-shadow:0 18px 50px rgba(18,53,44,.16);margin-bottom:22px}
.hero h1{font-size:42px;margin:8px 0;color:#fff}.hero p{max-width:850px;color:#d8e8e1;font-size:16px}.eyebrow{font-size:12px;letter-spacing:.15em;text-transform:uppercase;color:#cceaa8;font-weight:700}
.section{border:1px solid var(--line);border-radius:22px;padding:22px;background:var(--surface);box-shadow:0 7px 25px var(--shadow);margin-bottom:18px}
.card{border:1px solid var(--line);border-radius:18px;padding:18px;background:var(--surface);box-shadow:0 6px 20px var(--shadow);height:100%}
.card .label{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}.card .value{font-family:'Space Grotesk';font-size:30px;font-weight:700;margin-top:5px;color:var(--ink)}.card .hint{font-size:12px;color:var(--muted);margin-top:4px}
.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:12px 0 22px}.metric{background:var(--soft);border-radius:18px;padding:18px;border:1px solid var(--line)}
.metric strong{font-family:'Space Grotesk';font-size:27px;color:var(--ink)}.metric span{display:block;color:var(--muted);font-size:12px;margin-top:3px}
.pill{display:inline-block;padding:6px 10px;border-radius:999px;background:var(--mint);color:var(--deep);font-size:12px;font-weight:700}.pill.gold{background:#fff3cf;color:#6d5410}.pill.red{background:#fde5e5;color:#8e3333}
.callout{border-left:4px solid var(--accent);background:#f2f8f5;color:var(--ink);padding:14px 17px;border-radius:0 14px 14px 0;margin:12px 0}.warn{border-left-color:var(--gold);background:#fff9e9}.danger{border-left-color:var(--danger);background:#fff2f2}
.flow{display:flex;gap:8px;align-items:center;overflow-x:auto;padding:8px 0 14px}.flow .node{min-width:120px;padding:13px;border:1px solid var(--line);border-radius:16px;background:var(--surface);color:var(--ink);text-align:center;font-size:12px}.flow .arrow{color:#8b9892;font-size:18px}
.stButton button{border-radius:12px;font-weight:600;color:var(--ink);background:var(--surface);border-color:var(--line)}
.stButton button:hover{border-color:var(--accent);color:var(--ink)}
.stTextInput input,.stNumberInput input,.stTextArea textarea{border-radius:12px!important;border-color:var(--line)!important;background:var(--input)!important;color:var(--input-text)!important;caret-color:var(--input-text)!important}
.stSelectbox div[data-baseweb="select"]>div,.stMultiSelect div[data-baseweb="select"]>div{border-radius:12px!important;border-color:var(--line)!important;background:var(--input)!important;color:var(--input-text)!important}
.stSelectbox div[data-baseweb="select"] *, .stMultiSelect div[data-baseweb="select"] *{color:var(--input-text)!important}
[data-baseweb="popover"],[data-baseweb="menu"]{background:var(--surface)!important;color:var(--ink)!important}
[data-baseweb="menu"] *{color:var(--ink)!important}
[data-baseweb="option"]:hover{background:var(--soft)!important}
[data-testid="stCheckbox"] label,[data-testid="stRadio"] label,[data-testid="stSlider"] label,[data-testid="stSelectbox"] label,[data-testid="stMultiSelect"] label,[data-testid="stTextInput"] label,[data-testid="stNumberInput"] label,[data-testid="stTextArea"] label{color:var(--ink)!important}
[data-testid="stCaptionContainer"],.stCaption{color:var(--muted)!important}
[data-testid="stExpander"]{border-radius:16px!important;border:1px solid var(--line)!important;background:var(--surface)!important}
[data-testid="stExpander"] summary,[data-testid="stExpander"] summary p{color:var(--ink)!important}
.stTabs [data-baseweb="tab-list"]{gap:8px}.stTabs [data-baseweb="tab"]{color:var(--muted)!important}.stTabs [aria-selected="true"]{color:var(--accent)!important}
.stAlert{color:var(--ink)!important}
.small{font-size:12px;color:var(--muted)}
.js-plotly-plot .plotly .main-svg{background:transparent!important}
.js-plotly-plot .plotly text{fill:var(--ink)!important}
.js-plotly-plot .plotly .gridlayer path,.js-plotly-plot .plotly .zerolinelayer path{stroke:var(--line)!important}
.js-plotly-plot .plotly .axis path,.js-plotly-plot .plotly .axis line{stroke:var(--line)!important}

/* Streamlit dark theme and browser dark preference.  The selectors cover both
   Streamlit's theme attribute and browsers that expose prefers-color-scheme. */
html[data-theme="dark"],body[data-theme="dark"],[data-theme="dark"]{
  color-scheme:dark;--ink:#eef5f1;--muted:#aab9b2;--line:#34463f;--soft:#1d2b27;--surface:#101816;--surface-2:#17221f;--input:#17221f;--input-text:#eef5f1;--shadow:rgba(0,0,0,.24)
}
@media (prefers-color-scheme:dark){
  :root{color-scheme:dark;--ink:#eef5f1;--muted:#aab9b2;--line:#34463f;--soft:#1d2b27;--surface:#101816;--surface-2:#17221f;--input:#17221f;--input-text:#eef5f1;--shadow:rgba(0,0,0,.24)}
  html,body{background:var(--surface);color:var(--ink)}
  .section,.card,.flow .node{background:var(--surface)}
  .metric{background:var(--soft)}
  .callout{background:#172b24}.warn{background:#302a18}.danger{background:#301d20}
  .pill{background:#214838;color:#dff3e9}.pill.gold{background:#403617;color:#f4d67e}.pill.red{background:#482427;color:#ffc4c4}
  .stButton button{background:var(--surface);color:var(--ink);border-color:var(--line)}
}
@media(max-width:900px){.metric-grid{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:32px}}
</style>
""", unsafe_allow_html=True)

# ----------------------------- State -----------------------------
DEFAULT = {
    "page":"Central do projeto","company":"","project":"","sector":"","scope_type":"Linha de produção","scope_name":"",
    "request_status":"Nova", "request_origin":"Indicação", "declared_problem":"", "initial_data":"", "proposal_justification":"",
    "capex":0.0,"initial_costs":0.0,"consulting_fee":0.0,"other_investment":0.0,"savings_material":0.0,"savings_waste":0.0,"savings_energy":0.0,"savings_water":0.0,"revenue_additional":0.0,"other_savings":0.0,"opex":0.0,
    "implementation_months":12.0,"horizon_years":5,"consulting_benefit":0.0,
    "areas":[],"lines":[],"processes":[],"observations":[],"materials":[],"losses":[],"opportunities":[],"visits":[],"kpis":[],"monitor_kpis":[],"proposal_inputs":{},"trace_events":[],
    "ft":{k:7 for k in FT_WEIGHTS},"ci":{k:4 for k in CI_WEIGHTS},"gr":{k:3 for k in GR_WEIGHTS},
    "env":{"virgin_material_avoided":20.0,"waste_avoided_recovered":30.0,"energy_avoided":10.0,"water_avoided":5.0,"emissions_avoided":15.0},
}
for k,v in DEFAULT.items():
    if k not in st.session_state: st.session_state[k]=v.copy() if isinstance(v,dict) else (list(v) if isinstance(v,list) else v)
S=st.session_state

PAGES=[
("Central do projeto","⌂"),("00 Demanda","00"),("01 Proposta","01"),("02 Cadrage","02"),("03 Diagnóstico","03"),("04 Dados","04"),("05 Perdas","05"),("06 Oportunidades","06"),("07 Priorização","07"),("08 Plano + ROI","08"),("09 Monitoramento","09"),("10 Relatórios","10"),("11 Dashboard","11"),("12 Rastreabilidade","12"),("Metodologia VITENUS","M")]

with st.sidebar:
    st.markdown("<div style='padding:8px 4px 18px'><div style='font-family:Space Grotesk;font-size:28px;font-weight:700'>VITENUS<span style='color:#bde56d'>.</span></div><div style='font-size:11px;opacity:.7;letter-spacing:.12em'>CIRCULAR ENGINE · V0.4</div></div>",unsafe_allow_html=True)
    for label,icon in PAGES:
        if st.button(f"{icon}   {label}",key=f"nav_{label}",use_container_width=True): S.page=label; st.rerun()
    st.markdown("<hr style='border-color:rgba(255,255,255,.12)'>",unsafe_allow_html=True)
    st.caption("Projeto ativo")
    st.write(S.company or "Nenhum cliente definido")
    st.write(S.project or "Novo projeto")
    if st.button("💾 Salvar workspace",use_container_width=True):
        try:
            save_workspace(get_client(),S.company,S.project,workspace_payload())
            st.success("Workspace salvo.")
        except Exception as e: st.error(f"Supabase: {e}")

# ----------------------------- Helpers -----------------------------
def money(x): return f"R$ {x:,.0f}".replace(",","X").replace(".",",").replace("X",".")
def pct(x): return f"{x:.1f}%".replace(".",",")
def add_item(key,item): S[key].append(item)
def workspace_payload():
    return {k:S[k] for k in DEFAULT.keys() if k not in {"page"}}

def why(title,text):
    with st.expander(f"ⓘ {title}"):
        st.markdown(text)

def section(title,subtitle=None):
    st.markdown(f"<div class='section'><h2 style='margin-bottom:4px'>{title}</h2>{('<div class=\'small\'>%s</div>'%subtitle) if subtitle else ''}",unsafe_allow_html=True)

def end_section(): st.markdown("</div>",unsafe_allow_html=True)

def metrics(items):
    html="<div class='metric-grid'>"
    for label,value,hint in items: html+=f"<div class='metric'><strong>{value}</strong><span>{label}</span><div class='small'>{hint}</div></div>"
    html+="</div>"; st.markdown(html,unsafe_allow_html=True)

def proposal_investment_total():
    p=S.proposal_inputs
    return sum(float(p.get(k,0) or 0) for k in ["capex","engineering","installation","commissioning","training","consulting","contingency","other_investment"])

def kpi_catalog():
    return [
        {"code":"KPI-M01","name":"Intensidade de perda de material","unit":"kg / unidade de produção","formula":"perda física ÷ produção","family":"Material"},
        {"code":"KPI-M02","name":"Geração específica de resíduos","unit":"kg / unidade de produção","formula":"resíduo gerado ÷ produção","family":"Resíduo"},
        {"code":"KPI-M03","name":"Taxa de recuperação/reutilização","unit":"%","formula":"quantidade recuperada ou reutilizada ÷ quantidade gerada × 100","family":"Circularidade"},
        {"code":"KPI-E01","name":"Custo da perda","unit":"R$ / período","formula":"quantidade perdida × custo unitário + custos associados","family":"Economia"},
        {"code":"KPI-E02","name":"Benefício econômico realizado","unit":"R$ / período","formula":"economias + receitas adicionais − OPEX adicional","family":"Economia"},
        {"code":"KPI-E03","name":"ROI realizado","unit":"%","formula":"(benefício líquido acumulado − investimento) ÷ investimento × 100","family":"Economia"},
        {"code":"KPI-E04","name":"Payback realizado","unit":"meses","formula":"tempo até o fluxo de caixa acumulado se tornar ≥ 0","family":"Economia"},
        {"code":"KPI-EN01","name":"Intensidade energética","unit":"kWh / unidade de produção","formula":"energia consumida ÷ produção","family":"Energia"},
        {"code":"KPI-EN02","name":"Intensidade hídrica","unit":"m³ / unidade de produção","formula":"água consumida ÷ produção","family":"Água"},
        {"code":"KPI-ENV01","name":"Emissões evitadas","unit":"tCO₂e / período","formula":"atividade evitada × fator de emissão versionado","family":"Emissões"},
    ]

def auto_kpis_for_opportunity(o):
    family=o.get("family","")
    codes=["KPI-E02","KPI-E03","KPI-E04"]
    if family in ["Redução","Reutilização"]: codes += ["KPI-M01","KPI-M03"]
    if family=="Valorização": codes += ["KPI-M02","KPI-M03"]
    return [dict(x,opportunity=o.get("id")) for x in kpi_catalog() if x["code"] in codes]

def economic():
    gross=annual_gross_benefit(S.savings_material,S.savings_waste,S.savings_energy,S.savings_water,S.revenue_additional,S.other_savings)
    net=net_annual_benefit(gross,S.opex)
    inv=S.capex+S.initial_costs+S.consulting_fee+S.other_investment
    pb=simple_payback_months(inv,net)
    roi=project_roi_percent(gross,S.opex,inv) if inv>0 else 0
    return gross,net,inv,pb,roi

def scores():
    gross,net,inv,pb,roi=economic(); rea=(net/inv*100) if inv>0 else 0
    ie=economic_index(rea)
    ft=technical_feasibility_index(S.ft)
    ia,_=environmental_index(S.env)
    ci=implementation_complexity_index(S.ci)
    tn=time_index(S.implementation_months)
    gr=risk_index(S.gr)
    ipc_v=ipc({"IE":ie,"FT":ft,"IA":ia,"CI":ci,"TN":tn,"GR":gr})
    return {"IE":ie,"FT":ft,"IA":ia,"CI":ci,"TN":tn,"GR":gr},ipc_v

def show_flow(current):
    labels=["Demanda","Proposta","Cadrage","Diagnóstico","Dados","Perdas","Oportunidades","Priorização","Plano + ROI","Monitoramento"]
    st.markdown("<div class='flow'>"+"".join(f"<div class='node' style='border-color:{'#2f8f6b' if l==current else '#dfe7e2'}'>{l}</div><div class='arrow'>›</div>" for l in labels)+"</div>",unsafe_allow_html=True)

def append_form_item(kind):
    if kind=="area":
        name=st.session_state.get("new_area","").strip();
        if name: add_item("areas",{"name":name,"type":st.session_state.new_area_type,"notes":st.session_state.new_area_notes}); st.rerun()
    if kind=="line":
        name=st.session_state.get("new_line","").strip();
        if name: add_item("lines",{"name":name,"area":st.session_state.new_line_area,"product":st.session_state.new_line_product,"volume":st.session_state.new_line_volume,"unit":st.session_state.new_line_unit}); st.rerun()

# ----------------------------- Header -----------------------------
st.markdown("<div class='hero'><div class='eyebrow'>VITENUS · CIRCULAR ENGINE · V0.4</div><h1>Diagnóstico e Valorização Circular</h1><p>Uma plataforma operacional para conduzir o serviço inteiro: da demanda à proposta, da imersão industrial ao diagnóstico, das perdas às oportunidades, da priorização ao ROI e ao monitoramento.</p></div>",unsafe_allow_html=True)
show_flow(S.page if S.page in [x[0] for x in PAGES] else "")

# ----------------------------- Pages -----------------------------
if S.page=="Central do projeto":
    gross,net,inv,pb,roi=economic(); idx,ipc_v=scores()
    metrics([("Linhas / unidades",len(S.lines)+len(S.areas),"escopo modelado"),("Observações",len(S.observations),"registros de campo"),("Perdas",len(S.losses),"identificadas"),("Potencial anual",money(max(net,0)),"benefício líquido estimado")])
    c1,c2=st.columns([1.35,1])
    with c1:
        section("Mapa do projeto","A plataforma cresce conforme você coleta evidências.")
        st.markdown("**Empresa → Área → Linha → Processo → Etapa → Observação → Perda → Oportunidade → Solução → Business Case**")
        st.info("Comece em **00 Demanda** para um novo cliente. Depois avance cronologicamente; os dados permanecem no mesmo workspace.")
        end_section()
    with c2:
        section("Saúde do projeto")
        st.progress(min(len(S.observations)/20,1.0),text=f"Coleta de campo · {len(S.observations)} observações")
        st.progress(min(len(S.losses)/10,1.0),text=f"Análise · {len(S.losses)} perdas")
        st.progress(min(len(S.opportunities)/8,1.0),text=f"Concepção · {len(S.opportunities)} oportunidades")
        st.markdown(f"**IPC atual:** {ipc_v:.1f}/100 · **{ipc_band(ipc_v).replace('_',' ')}**")
        end_section()
    if S.lines:
        df=pd.DataFrame(S.lines); st.plotly_chart(px.bar(df,x="name",y="volume",color="area",title="Volume modelado por linha"),use_container_width=True)

elif S.page=="00 Demanda":
    section("00 · Entrada da demanda","A porta de entrada comercial-operacional do serviço.")
    why("Por que existe esta etapa?","O documento-base começa pela compreensão do cliente, do produto, do processo, dos fluxos, dos agentes e do perímetro. A demanda deve registrar a dor declarada antes de qualquer diagnóstico técnico.")
    c1,c2=st.columns(2)
    with c1:
        S.company=st.text_input("Empresa",S.company)
        S.project=st.text_input("Nome do projeto",S.project)
        S.sector=st.text_input("Setor industrial",S.sector)
        S.request_origin=st.selectbox("Origem da demanda",["Indicação","Prospecção","Cliente recorrente","Inbound","Parceiro","Outro"],index=["Indicação","Prospecção","Cliente recorrente","Inbound","Parceiro","Outro"].index(S.request_origin))
    with c2:
        S.declared_problem=st.text_area("Dor / problema declarado",S.declared_problem,height=120)
        S.initial_data=st.text_area("Dados iniciais disponíveis",S.initial_data,height=120)
    st.markdown("### Triagem visual")
    qs=["A dor tem relação com matéria, resíduos, perdas ou valorização?","O escopo parece investigável?","Há possibilidade de medir resultado depois?","Há dados iniciais suficientes para construir uma hipótese?"]
    for q in qs:
        st.radio(q,["Sim","Parcial","Não","A investigar"],horizontal=True,key="tri_"+str(qs.index(q)))
    if st.button("Registrar demanda",type="primary"):
        try:
            save_service_request(get_client(),{"company_name":S.company,"origin":S.request_origin,"received_at":str(date.today()),"status":"Nova","summary":S.declared_problem[:180],"declared_problem":S.declared_problem,"initial_scope":S.scope_name,"initial_data":S.initial_data})
            st.success("Demanda registrada no Supabase.")
        except Exception as e: st.warning(f"Workspace local atualizado. Supabase: {e}")
    end_section()

elif S.page=="01 Proposta":
    section("01 · Proposta e qualificação","Nesta fase a VITENUS não inventa dados que o cliente ainda não possui. O objetivo é construir uma hipótese de retorno transparente e mostrar exatamente o que precisará ser validado no diagnóstico.")
    why("Regra econômica da proposta","O cliente nem sempre consegue informar CAPEX, economia anual, OPEX ou volume de perdas com precisão. Por isso, a proposta separa DADO CONHECIDO, ESTIMATIVA VITENUS e DADO A VALIDAR. Payback e ROI só aparecem como números quando existe uma base mínima explicitamente registrada. Caso contrário, o sistema entrega a estrutura de cálculo e a lista de dados necessários — sem fabricar uma projeção.")

    st.markdown("### 1 · Perímetro e hipótese de negócio")
    c1,c2,c3=st.columns(3)
    with c1:
        S.scope_type=st.selectbox("Perímetro preliminar",["Linha de produção","Mais de uma linha","Setor","Mais de um setor","Planta inteira","Outro"],key="p_scope_type")
        S.scope_name=st.text_input("Como o cliente descreve o escopo?",S.scope_name,key="p_scope_name")
    with c2:
        S.proposal_inputs["production_volume"]=st.number_input("Produção anual conhecida (opcional)",min_value=0.0,value=float(S.proposal_inputs.get("production_volume",0)),key="p_prod")
        S.proposal_inputs["production_unit"]=st.text_input("Unidade",value=S.proposal_inputs.get("production_unit","t/ano"),key="p_prod_unit")
    with c3:
        S.proposal_inputs["data_access"]=st.selectbox("Acesso preliminar aos dados",["Baixo","Parcial","Bom","Ainda não avaliado"],index=["Baixo","Parcial","Bom","Ainda não avaliado"].index(S.proposal_inputs.get("data_access","Ainda não avaliado")),key="p_access")
        S.proposal_inputs["main_hypothesis"]=st.text_area("Hipótese de geração de valor",value=S.proposal_inputs.get("main_hypothesis",""),height=90,key="p_hyp")

    st.markdown("### 2 · O que sabemos e o que ainda precisamos descobrir")
    st.caption("Todos os campos econômicos abaixo são opcionais. Use somente quando houver informação minimamente defensável.")
    st.markdown("**Investimento — detalhado para evitar a categoria vaga ‘outros investimentos’**")
    inv_fields=[
        ("capex","Equipamentos / CAPEX"),("engineering","Engenharia / projeto"),("installation","Instalação / adequação"),
        ("commissioning","Comissionamento / validação"),("training","Treinamento / mudança"),("consulting","Honorários VITENUS"),
        ("contingency","Contingência assumida"),("other_investment","Outros — obrigatoriamente descritos")]
    invc=st.columns(4)
    for i,(key,label) in enumerate(inv_fields):
        with invc[i%4]: S.proposal_inputs[key]=st.number_input(label,min_value=0.0,value=float(S.proposal_inputs.get(key,0)),key="p_inv_"+key)
    S.proposal_inputs["other_investment_note"]=st.text_input("Descrição de ‘Outros’",value=S.proposal_inputs.get("other_investment_note",""),key="p_other_note")
    econ_fields=[
        ("current_material_cost","Gasto anual conhecido com matéria-prima (R$)"),
        ("waste_management_cost","Custo anual conhecido de gestão/destinação de resíduos (R$)"),
        ("current_energy_cost","Custo anual de energia relacionado ao escopo (R$)"),
        ("current_water_cost","Custo anual de água relacionado ao escopo (R$)"),
        ("waste_revenue","Receita anual já obtida com resíduos/subprodutos (R$)"),
    ]
    cols=st.columns(3)
    for i,(key,label) in enumerate(econ_fields):
        with cols[i%3]:
            S.proposal_inputs[key]=st.number_input(label,min_value=0.0,value=float(S.proposal_inputs.get(key,0)),key="p_"+key)
    c1,c2,c3=st.columns(3)
    with c1: S.proposal_inputs["investment_confidence"]=st.selectbox("Confiança do investimento",["Não informado","Hipótese VITENUS","Orçamento/documento","Dado financeiro validado"],key="p_inv_conf")
    with c2: S.proposal_inputs["benefit_basis"]=st.selectbox("Base para estimar benefício",["Nenhuma ainda","Histórico do cliente","Medição disponível","Benchmark/estudo setorial","Hipótese técnica VITENUS"],key="p_benefit_basis")
    with c3: S.proposal_inputs["hurdle_months"]=st.number_input("Payback de referência desejado pelo cliente (opcional)",min_value=0.0,value=float(S.proposal_inputs.get("hurdle_months",0)),key="p_hurdle")

    known=[k for k,_ in econ_fields if S.proposal_inputs.get(k,0)>0]
    missing=[label for k,label in econ_fields if not S.proposal_inputs.get(k,0)]
    inv=proposal_investment_total()
    st.markdown("### 3 · Estrutura de retorno preliminar")
    if len(known)>=1 and inv>0 and S.proposal_inputs.get("benefit_basis")!="Nenhuma ainda":
        st.success("Há dados suficientes para uma simulação preliminar controlada. Os valores abaixo são hipóteses de proposta e não resultado do diagnóstico.")
        inv=float(inv)
        # Only known cost reductions/revenues are used; no invented benefit.
        benefit=sum(float(S.proposal_inputs.get(k,0)) for k in ["current_material_cost","waste_management_cost","current_energy_cost","current_water_cost","waste_revenue"])
        benefit=benefit*0.0 + float(S.proposal_inputs.get("waste_revenue",0))
        # The system intentionally does not equate total current cost with achievable savings.
        S.proposal_inputs["scenario_benefit"]=st.number_input("Benefício anual assumido para a simulação (R$)",min_value=0.0,value=float(S.proposal_inputs.get("scenario_benefit",0)),key="p_scenario_benefit",help="Somente uma hipótese explicitamente assumida pela VITENUS. Não representa automaticamente o custo atual.")
        S.proposal_inputs["scenario_opex"]=st.number_input("OPEX adicional anual assumido (R$)",min_value=0.0,value=float(S.proposal_inputs.get("scenario_opex",0)),key="p_scenario_opex")
        b=float(S.proposal_inputs["scenario_benefit"]); op=float(S.proposal_inputs["scenario_opex"]); net_p=b-op
        pb=simple_payback_months(inv,net_p); roi_p=project_roi_percent(b,op,inv) if inv>0 else 0
        metrics([("Investimento assumido",money(inv),"hipótese registrada"),("Benefício líquido assumido",money(net_p),"benefício − OPEX"),("Payback",("—" if math.isinf(pb) else f"{pb:.1f} meses"),"simulação, não garantia"),("ROI anual",pct(roi_p),"simulação, não garantia")])
        cf=[]; cum=-inv
        for m in range(1,37):
            cum += net_p/12
            cf.append({"Mês":m,"Fluxo acumulado":cum})
        st.plotly_chart(px.line(pd.DataFrame(cf),x="Mês",y="Fluxo acumulado",markers=True,title="Curva de retorno — somente com hipótese econômica explicitada"),use_container_width=True)
    else:
        st.info("Ainda não há base suficiente para um Payback/ROI numérico defensável. A plataforma mantém a estrutura pronta e mostra o que precisa ser coletado antes de calcular.")
        metrics([("Variáveis conhecidas",str(len(known)),"informações econômicas registradas"),("Variáveis faltantes",str(len(missing)),"dados a investigar"),("Payback","não calculado","evita falsa precisão"),("ROI","não calculado","evita falsa precisão")])
        st.markdown("**Dados prioritários para a próxima etapa:**")
        for item in missing: st.markdown(f"- {item}")

    with st.expander("Como a VITENUS estrutura o retorno antes do diagnóstico"):
        st.markdown("**Payback = investimento elegível ÷ benefício líquido periódico.**\n\n**ROI = (benefício − OPEX adicional − investimento) ÷ investimento × 100.**\n\nNa proposta, qualquer valor estimado precisa ter origem e natureza declaradas: dado do cliente, documento, benchmark ou hipótese VITENUS. O diagnóstico substitui hipóteses por medições e evidências.")
    S.proposal_justification=st.text_area("Justificativa técnica preliminar",S.proposal_justification if "proposal_justification" in S else "",height=140,help="Explique por que o serviço é pertinente com os dados limitados, quais hipóteses sustentam a proposta e quais pontos serão obrigatoriamente validados.")
    if st.button("Registrar proposta / qualificação",type="primary"):
        try:
            save_proposal(get_client(),{"company_name":S.company,"fit_conclusion":"A investigar","justification":S.proposal_justification,"limitations":"Resultado preliminar; sujeito a validação no diagnóstico.","scope":S.scope_name})
            st.success("Proposta registrada.")
        except Exception as e: st.warning(f"Proposta pronta no workspace. Supabase: {e}")
    end_section()

elif S.page=="02 Cadrage":
    section("02 · Cadrage","Transforme a contratação em um perímetro investigável.")
    c1,c2=st.columns(2)
    with c1:
        S.scope_type=st.selectbox("Tipo de perímetro",["Linha de produção","Mais de uma linha","Setor","Mais de um setor","Planta inteira","Outro"],key="cad_scope")
        st.text_area("Objetivo do projeto",height=100,key="cad_goal")
    with c2:
        st.number_input("Número estimado de visitas",min_value=1,value=max(1,len(S.visits)),key="cad_visits")
        st.multiselect("Áreas que precisarão participar",["Produção","Manutenção","Qualidade","Compras","Logística","Meio ambiente","Financeiro","Engenharia","Gestão"],default=[x.get("area") for x in S.visits if x.get("area")])
    st.markdown("### Estrutura física do projeto")
    a,b=st.columns(2)
    with a:
        st.text_input("Nova área / setor",key="new_area"); st.selectbox("Tipo",["Setor","Área administrativa","Utilidades","Produção","Armazenagem","Outro"],key="new_area_type"); st.text_input("Observação",key="new_area_notes")
        if st.button("+ Adicionar área"): append_form_item("area")
    with b:
        st.text_input("Nova linha / unidade",key="new_line"); st.selectbox("Área",["—"]+[a["name"] for a in S.areas],key="new_line_area"); st.text_input("Produto",key="new_line_product"); st.number_input("Volume mensal",min_value=0.0,key="new_line_volume"); st.text_input("Unidade",value="t/mês",key="new_line_unit")
        if st.button("+ Adicionar linha"): append_form_item("line")
    if S.areas: st.markdown("**Áreas:** " + " · ".join(a["name"] for a in S.areas))
    if S.lines: st.markdown("**Linhas:** " + " · ".join(l["name"] for l in S.lines))
    end_section()

elif S.page=="03 Diagnóstico":
    section("03 · Diagnóstico industrial","O coração do serviço: observar, perguntar, entrevistar e mapear o que acontece em cada processo.")
    why("Visita imersiva","O documento enfatiza uma visita ou visitas imersivas, não uma passagem por um único turno. A investigação deve envolver pelo menos 2–3 pessoas em diferentes áreas, fazendo perguntas, análises e entrevistas; os dados devem ser observados processo a processo. ")
    if not S.lines: st.warning("Cadastre ao menos uma linha/unidade em 02 Cadrage para começar a registrar o diagnóstico por processo.")
    c1,c2,c3=st.columns(3)
    with c1: st.selectbox("Linha / unidade",[l["name"] for l in S.lines] or ["Ainda não cadastrada"],key="d_line"); st.text_input("Processo",key="d_process"); st.text_input("Etapa",key="d_step")
    with c2: st.selectbox("Tipo de registro",["Observação","Entrevista","Medição","Documento","Foto/evidência"],key="d_type"); st.text_input("Pessoa / área entrevistada",key="d_person"); st.text_input("Data da visita",value=str(date.today()),key="d_date")
    with c3: st.text_area("O que foi observado?",key="d_note",height=120); st.selectbox("Confiança da informação",["5 · medição/ERP/documento verificado","4 · documento interno verificado","3 · declaração operacional","2 · estimativa técnica","1 · hipótese"],key="d_conf")
    if st.button("+ Registrar observação",type="primary"):
        if S.d_note.strip(): S.observations.append({"line":S.d_line,"process":S.d_process,"step":S.d_step,"type":S.d_type,"person":S.d_person,"date":S.d_date,"note":S.d_note,"confidence":S.d_conf}); st.rerun()
    if S.observations:
        st.markdown("### Diário de campo")
        for i,o in enumerate(reversed(S.observations)):
            with st.expander(f"{len(S.observations)-i:02d} · {o['line']} · {o['process'] or 'processo não informado'} · {o['type']}"):
                st.write(o["note"]); st.caption(f"Etapa: {o['step'] or '—'} · Entrevistado: {o['person'] or '—'} · {o['confidence']}")
    end_section()

elif S.page=="04 Dados":
    section("04 · Transformação de informações em dados","Converta o diário de campo em variáveis mensuráveis, com unidade, período, fonte e qualidade.")
    why("Por que separar observação de dado?","Durante a visita, a VITENUS registra fatos e observações. Depois, esses elementos são organizados em dados comparáveis, com unidades, períodos, fontes e classificação de qualidade.")
    c1,c2,c3=st.columns(3)
    with c1: st.text_input("Material / variável",key="m_name"); st.number_input("Quantidade",min_value=0.0,key="m_qty"); st.text_input("Unidade",value="kg/mês",key="m_unit")
    with c2: st.selectbox("Destino",["Processo","Produto","Estoque","Descarte","Reciclagem","Reutilização","Venda","Outro"],key="m_dest"); st.number_input("Custo atual (R$/período)",min_value=0.0,key="m_cost")
    with c3: st.selectbox("Fonte",["Medição","ERP","Documento","Entrevista","Observação","Estimativa"],key="m_source"); st.select_slider("Qualidade do dado",options=[1,2,3,4,5],value=3,key="m_quality"); st.text_area("Notas",key="m_notes",height=90)
    if st.button("+ Adicionar dado",type="primary"):
        S.materials.append({"name":S.m_name,"qty":S.m_qty,"unit":S.m_unit,"dest":S.m_dest,"cost":S.m_cost,"source":S.m_source,"quality":S.m_quality,"notes":S.m_notes}); st.rerun()
    if S.materials:
        df=pd.DataFrame(S.materials); c1,c2=st.columns(2)
        with c1: st.plotly_chart(px.bar(df,x="name",y="qty",color="dest",title="Quantidade por material"),use_container_width=True)
        with c2: st.plotly_chart(px.bar(df,x="name",y="cost",color="source",title="Custo atual por material"),use_container_width=True)
        st.dataframe(df,use_container_width=True,hide_index=True)
    end_section()

elif S.page=="05 Perdas":
    section("05 · Identificação de perdas","Uma ocorrência física/econômica é registrada uma única vez. Depois, suas dimensões são classificadas sem duplicar o valor.")
    why("Regra para não duplicar perdas","Uma mesma ocorrência pode ser simultaneamente uma perda material, uma perda econômica, uma oportunidade potencial e um risco estratégico. Essas categorias NÃO são quatro perdas independentes. A VITENUS cria um único EVENTO DE PERDA, com uma dimensão primária e dimensões secundárias. O valor econômico do evento entra uma única vez nos agregados. O potencial de valorização é tratado como potencial futuro, não somado à perda econômica. O risco é tratado como atributo/impacto, não como dinheiro adicional.")
    st.markdown("### 1 · Registrar o evento físico observado")
    c1,c2,c3=st.columns(3)
    with c1:
        st.selectbox("Processo relacionado",["—"]+[o.get("process") for o in S.observations if o.get("process")],key="l_process")
        st.text_input("Descrição do evento",key="l_desc")
        st.selectbox("Dimensão primária",["Perda material","Perda econômica","Potencial de valorização","Risco estratégico"],key="l_primary")
    with c2:
        st.number_input("Quantidade do evento",min_value=0.0,key="l_qty")
        st.text_input("Unidade",value="kg/ano",key="l_unit")
        st.number_input("Valor econômico anual do evento (R$)",min_value=0.0,key="l_value")
    with c3:
        st.text_input("Causa provável",key="l_cause")
        st.selectbox("Fonte principal",["Medição","ERP","Documento","Entrevista","Observação","Estimativa"],key="l_source")
        st.select_slider("Qualidade do dado",options=[1,2,3,4,5],value=3,key="l_quality")
    st.markdown("### 2 · Dimensões adicionais do mesmo evento")
    dims=st.multiselect("Marque somente as dimensões que realmente se aplicam",["Material","Econômica","Potencial","Risco estratégico"],key="l_dims")
    c1,c2=st.columns(2)
    with c1: st.number_input("Potencial anual de valorização estimado (R$)",min_value=0.0,key="l_potential",help="Não é somado ao valor da perda; representa valor futuro potencial de uma solução.")
    with c2: st.selectbox("Nível de risco associado",["Não avaliado","Baixo","Moderado","Alto","Crítico"],key="l_risk")
    if st.button("+ Registrar evento de perda",type="primary"):
        if not S.l_desc.strip(): st.warning("Descreva o evento antes de registrar.")
        else:
            S.losses.append({"id":f"L{len(S.losses)+1:03d}","process":S.l_process,"type":S.l_primary,"dimensions":dims,"description":S.l_desc,"qty":S.l_qty,"unit":S.l_unit,"value":S.l_value,"potential":S.l_potential,"risk":S.l_risk,"cause":S.l_cause,"source":S.l_source,"quality":S.l_quality})
            st.rerun()
    if S.losses:
        st.markdown("### Mapa dos eventos")
        for l in S.losses:
            with st.container(border=True):
                a,b,c=st.columns([1.1,2.2,1.2])
                with a: st.markdown(f"**{l['id']}**\n\n{l['type']}"); st.caption(f"Dimensões: {', '.join(l.get('dimensions',[])) or '—'}")
                with b: st.markdown(f"### {l['description']}"); st.caption(f"Processo: {l['process'] or '—'} · Fonte: {l['source']} · Qualidade: {l['quality']}/5"); st.write(f"Causa: {l['cause'] or 'não definida'}")
                with c: st.metric("Perda econômica",money(l['value'])); st.metric("Potencial",money(l.get('potential',0))); st.caption(f"Risco: {l.get('risk','—')}")
        total_loss=sum(float(x.get("value",0)) for x in S.losses)
        total_pot=sum(float(x.get("potential",0)) for x in S.losses)
        metrics([("Eventos únicos",len(S.losses),"base física do diagnóstico"),("Valor econômico",money(total_loss),"cada evento contado uma vez"),("Potencial de valorização",money(total_pot),"não somado à perda"),("Risco",str(sum(1 for x in S.losses if x.get('risk') in ['Alto','Crítico'])),"eventos de atenção")])
        df=pd.DataFrame(S.losses)
        st.plotly_chart(px.bar(df,x="id",y="value",color="type",title="Valor econômico por evento — sem duplicação por dimensão"),use_container_width=True)
    end_section()

elif S.page=="06 Oportunidades":
    section("06 · Oportunidades circulares","Uma oportunidade nasce de um evento de perda/fluxo e representa uma hipótese de transformação em valor.")
    why("Regra de ligação","Uma oportunidade não é uma nova perda. Ela aponta para um evento já diagnosticado e descreve uma possível intervenção: REDUÇÃO → REUTILIZAÇÃO → VALORIZAÇÃO. O potencial econômico da oportunidade deve ser calculado separadamente do valor histórico da perda.")
    c1,c2,c3=st.columns(3)
    with c1:
        st.selectbox("Evento de origem",["—"]+[f"{x['id']} · {x['description']}" for x in S.losses],key="o_loss")
        st.selectbox("Família",["Redução","Reutilização","Valorização"],key="o_family")
    with c2:
        st.text_input("Solução / hipótese",key="o_solution")
        st.text_input("Mercado / destino",key="o_market")
        st.text_input("Tecnologia / parceiro",key="o_tech")
    with c3:
        st.number_input("Benefício anual potencial (R$)",min_value=0.0,key="o_benefit")
        st.number_input("Investimento estimado (R$)",min_value=0.0,key="o_invest")
        st.number_input("OPEX adicional anual (R$)",min_value=0.0,key="o_opex")
    st.text_area("Hipótese causal: como a solução transforma a perda em valor?",key="o_rationale",height=90)
    if st.button("+ Criar oportunidade",type="primary"):
        b=float(S.o_benefit); inv=float(S.o_invest); op=float(S.o_opex); pb=simple_payback_months(inv,max(b-op,0)) if inv>0 else float('inf'); r=((b-op-inv)/inv*100) if inv>0 else 0
        S.opportunities.append({"id":f"O{len(S.opportunities)+1:03d}","loss":S.o_loss,"family":S.o_family,"solution":S.o_solution,"market":S.o_market,"tech":S.o_tech,"rationale":S.o_rationale,"benefit":b,"investment":inv,"opex":op,"payback":pb,"roi":r}); st.rerun()
    for o in S.opportunities:
        with st.container(border=True):
            a,b,c=st.columns([1,2,1])
            with a: st.markdown(f"**{o['id']} · {o['family']}**"); st.caption(o['loss'])
            with b: st.markdown(f"### {o['solution'] or 'Solução sem nome'}"); st.write(o.get('rationale') or 'Sem hipótese causal registrada.')
            with c: st.metric("Payback",("—" if math.isinf(o['payback']) else f"{o['payback']:.1f} meses")); st.metric("ROI",pct(o['roi']))
    end_section()

elif S.page=="07 Priorização":
    section("07 · Priorização","A priorização compara soluções, não perdas. Só deve ser aplicada depois de dados, eventos de perda e oportunidades modeladas.")
    why("Lógica do IPC","O IPC combina seis dimensões proprietárias: Impacto Econômico (IE), Viabilidade Técnica (FT), Impacto Ambiental (IA), Complexidade de Implementação (CI), Tempo Necessário (TN) e Grau de Risco (GR). As notas são normalizadas para 0–100 e combinadas pelos pesos V0.4. Os pesos são hipóteses metodológicas e devem ser calibrados com pilotos.")
    if S.opportunities:
        labels=[f"{o['id']} · {o['solution'] or 'Sem nome'}" for o in S.opportunities]
        sel=st.selectbox("Solução a priorizar",labels,key="prio_solution")
        selected=S.opportunities[labels.index(sel)]
        c1,c2,c3=st.columns(3)
        pt={"process_compatibility":"Compatibilidade com o processo","technology_maturity":"Maturidade tecnológica","equipment_availability":"Disponibilidade de equipamentos","modification_complexity":"Complexidade das modificações","third_party_dependency":"Dependência de terceiros","pilot_validation_need":"Necessidade de piloto/validação"}
        ci_labels={"departments":"Número de áreas envolvidas","process_changes":"Mudanças de processo","suppliers":"Dependência de fornecedores","partners":"Dependência de parceiros","capex_complexity":"Complexidade do CAPEX","production_downtime":"Parada de produção","organizational_change":"Mudança organizacional"}
        gr_labels={"technical":"Risco técnico","financial":"Risco financeiro","operational":"Risco operacional","regulatory":"Risco regulatório","market":"Risco de mercado","supplier":"Risco de fornecedor","quality":"Risco de qualidade"}
        with c1:
            st.markdown("**FT · Viabilidade técnica**")
            for k in S.ft: S.ft[k]=st.slider(pt[k],1,10,int(S.ft[k]),key="ft_"+k)
        with c2:
            st.markdown("**CI · Complexidade (1 = baixa; 10 = alta)**")
            for k in S.ci: S.ci[k]=st.slider(ci_labels[k],1,10,int(S.ci[k]),key="ci_"+k)
        with c3:
            st.markdown("**GR · Risco (1 = baixo; 10 = alto)**")
            for k in S.gr: S.gr[k]=st.slider(gr_labels[k],1,10,int(S.gr[k]),key="gr_"+k)
        st.markdown("### IA · Impacto ambiental")
        env_labels={"virgin_material_avoided":"Matéria-prima virgem evitada","waste_avoided_recovered":"Resíduo evitado/recuperado","energy_avoided":"Energia evitada","water_avoided":"Água evitada","emissions_avoided":"Emissões evitadas"}
        cols=st.columns(5)
        for i,k in enumerate(S.env):
            with cols[i]: S.env[k]=st.number_input(env_labels[k],min_value=0.0,max_value=100.0,value=float(S.env[k]),key="env_"+k)
        idx,ipc_v=scores(); metrics([("IPC",f"{ipc_v:.1f}/100",ipc_band(ipc_v).replace('_',' ')),("IE",f"{idx['IE']:.0f}","impacto econômico"),("FT",f"{idx['FT']:.0f}","viabilidade técnica"),("IA",f"{idx['IA']:.0f}","impacto ambiental")])
        st.plotly_chart(px.bar_polar(pd.DataFrame({"Índice":list(idx.keys()),"Valor":list(idx.values())}),r="Valor",theta="Índice",range_r=[0,100],title="Perfil da solução priorizada"),use_container_width=True)
        with st.expander("Fórmula e pesos"):
            st.latex(r"IPC=0,30IE+0,20FT+0,20IA+0,10CI+0,10TN+0,10GR")
            st.markdown("IE 30% · FT 20% · IA 20% · CI 10% · TN 10% · GR 10%. **São pesos VITENUS V0.4, não pesos prescritos por uma ISO.**")
    else:
        st.info("Crie pelo menos uma oportunidade em 06 Oportunidades antes de priorizar uma solução.")
    end_section()

elif S.page=="08 Plano + ROI":
    section("08 · Plano de ação + retorno","O plano transforma uma solução priorizada em implantação controlada, com gates, responsabilidades, investimento, benefícios e medição.")
    why("Fundamento metodológico","O plano não é uma lista genérica de tarefas. Cada ação deve estar ligada a uma solução, possuir responsável, prazo, critério de conclusão, custo/benefício esperado e um gate de decisão. O Business Case separa investimento, benefícios, OPEX adicional e fluxo de caixa. O Payback projetado é calculado antes da execução; o ROI realizado só existe depois da medição.")
    gross,net,inv,pb,roi=economic()
    metrics([("Investimento total",money(inv),"CAPEX + custos elegíveis"),("Benefício líquido anual",money(net),"benefícios − OPEX"),("Payback",("—" if math.isinf(pb) else f"{pb:.1f} meses"),"projetado"),("ROI",pct(roi),"projetado")])
    st.markdown("### Business Case")
    c1,c2=st.columns(2)
    with c1:
        S.capex=st.number_input("CAPEX",min_value=0.0,value=float(S.capex),key="bc_capex")
        S.initial_costs=st.number_input("Custos iniciais de implantação",min_value=0.0,value=float(S.initial_costs),key="bc_initial")
        S.consulting_fee=st.number_input("Honorários VITENUS",min_value=0.0,value=float(S.consulting_fee),key="bc_fee")
        S.other_investment=st.number_input("Outros custos elegíveis — descreva",min_value=0.0,value=float(S.other_investment),key="bc_other")
        st.text_input("Descrição dos outros custos",key="bc_other_note")
    with c2:
        S.savings_material=st.number_input("Economia de matéria-prima / ano",min_value=0.0,value=float(S.savings_material),key="bc_sm")
        S.savings_waste=st.number_input("Economia de resíduos / ano",min_value=0.0,value=float(S.savings_waste),key="bc_sw")
        S.savings_energy=st.number_input("Economia de energia / ano",min_value=0.0,value=float(S.savings_energy),key="bc_se")
        S.savings_water=st.number_input("Economia de água / ano",min_value=0.0,value=float(S.savings_water),key="bc_swa")
        S.revenue_additional=st.number_input("Receita adicional / ano",min_value=0.0,value=float(S.revenue_additional),key="bc_rev")
        S.other_savings=st.number_input("Outros benefícios / ano",min_value=0.0,value=float(S.other_savings),key="bc_os")
        S.opex=st.number_input("OPEX adicional / ano",min_value=0.0,value=float(S.opex),key="bc_opex")
    st.markdown("### Cenários")
    sc=st.columns(3)
    scenarios=[]
    for i,(name,factor) in enumerate([("Conservador",0.75),("Central",1.0),("Otimista",1.20)]):
        with sc[i]:
            b=st.number_input(f"Benefício {name} (R$/ano)",min_value=0.0,value=float(net*factor if net>0 else 0),key=f"sc_b_{i}")
            investment=st.number_input(f"Investimento {name} (R$)",min_value=0.0,value=float(inv*(1.15 if i==0 else 1.0 if i==1 else 0.9)),key=f"sc_i_{i}")
            op=st.number_input(f"OPEX {name} (R$/ano)",min_value=0.0,value=float(S.opex),key=f"sc_o_{i}")
            spb=simple_payback_months(investment,b-op); sroi=project_roi_percent(b,op,investment) if investment>0 else 0
            st.metric("Payback",("—" if math.isinf(spb) else f"{spb:.1f} meses")); st.metric("ROI",pct(sroi)); scenarios.append((name,spb,sroi))
    cf=[]
    for name,pb_s,roi_s in scenarios: cf.append({"Cenário":name,"Payback (meses)":None if math.isinf(pb_s) else pb_s,"ROI (%)":roi_s})
    st.plotly_chart(px.bar(pd.DataFrame(cf),x="Cenário",y="ROI (%)",title="Comparação de cenários — ROI projetado"),use_container_width=True)
    st.markdown("### Plano de implantação")
    c1,c2,c3=st.columns(3)
    with c1: st.text_input("Ação",key="a_action"); st.text_input("Responsável",key="a_owner")
    with c2: st.number_input("Prazo (meses)",min_value=0.0,key="a_time"); st.selectbox("Gate",["Validação de dados","Piloto","Decisão de investimento","Implementação","M&V / verificação"],key="a_gate")
    with c3: st.text_area("Critério objetivo de conclusão",key="a_done",height=80); st.text_input("Solução relacionada",key="a_solution")
    if st.button("+ Adicionar ação ao plano",type="primary"):
        if S.a_action.strip(): S.kpis.append({"kind":"action","action":S.a_action,"owner":S.a_owner,"time":S.a_time,"gate":S.a_gate,"done":S.a_done,"solution":S.a_solution}); st.rerun()
    for a in [x for x in S.kpis if x.get("kind")=="action"]:
        st.markdown(f"<div class='card'><b>{a['action']}</b><br><span class='small'>{a['owner']} · {a['time']} mês(es) · {a['gate']}</span><p>{a['done']}</p></div>",unsafe_allow_html=True)
    with st.expander("Como interpretar Payback e ROI"):
        st.markdown("**Payback** mede o tempo necessário para recuperar o investimento pelo fluxo líquido. **ROI** mede o retorno relativo ao investimento no horizonte definido. Nenhum dos dois substitui risco, viabilidade técnica, qualidade de dados ou medição posterior. O fluxo mensal é preferível ao cálculo simplificado quando existirem cronograma, ramp-up e investimentos distribuídos no tempo.")
    end_section()

elif S.page=="09 Monitoramento":
    section("09 · Monitoramento","A plataforma já conhece os KPIs que fazem sentido para o tipo de oportunidade; você alimenta baseline, meta e realizado.")
    why("O que acontece nesta fase?","Monitoramento não é criar uma lista livre de indicadores. A VITENUS parte de um catálogo metodológico de KPIs e associa automaticamente indicadores às soluções. O consultor valida quais são aplicáveis, registra a linha de base, define meta, informa o período de medição e depois registra o realizado. Assim o sistema pode calcular melhoria, benefício, ROI realizado e desvio em relação à projeção.")
    if S.opportunities:
        existing={(x.get("opportunity"),x.get("code")) for x in S.monitor_kpis}
        for o in S.opportunities:
            for k in auto_kpis_for_opportunity(o):
                if (k.get("opportunity"),k.get("code")) not in existing:
                    S.monitor_kpis.append(k)
    if not S.monitor_kpis:
        st.info("Crie uma oportunidade em 06 para o sistema sugerir automaticamente os KPIs de monitoramento.")
    for i,k in enumerate(S.monitor_kpis):
        with st.container(border=True):
            c1,c2,c3=st.columns([1.3,1.5,1.5])
            with c1:
                st.markdown(f"**{k['code']} · {k['name']}**"); st.caption(f"Família: {k['family']} · {k['unit']}")
                st.write(k['formula'])
            with c2:
                k["baseline"]=st.number_input("Baseline",value=float(k.get("baseline",0)),key=f"mk_b_{i}")
                k["target"]=st.number_input("Meta",value=float(k.get("target",0)),key=f"mk_t_{i}")
            with c3:
                k["actual"]=st.number_input("Realizado",value=float(k.get("actual",0)),key=f"mk_a_{i}")
                k["period"]=st.text_input("Período",value=k.get("period",str(date.today())),key=f"mk_p_{i}")
            if k.get("baseline",0)!=0:
                improvement=(k.get("baseline",0)-k.get("actual",0))/abs(k.get("baseline",0))*100
                st.progress(max(0,min(improvement/100,1)),text=f"Variação normalizada: {improvement:.1f}%")
            k["source"]=st.selectbox("Fonte da medição",["Medição instrumentada","ERP","Documento","Registro interno","Entrevista","Estimativa"],index=0,key=f"mk_s_{i}")
            k["evidence"]=st.text_input("Evidência / responsável",value=k.get("evidence",""),key=f"mk_e_{i}")
    if S.monitor_kpis:
        st.markdown("### O que o sistema poderá calcular")
        metrics([("KPIs ativos",len(S.monitor_kpis),"catálogo VITENUS"),("Com baseline",sum(1 for x in S.monitor_kpis if x.get('baseline',0)!=0),"prontos para comparação"),("Com realizado",sum(1 for x in S.monitor_kpis if x.get('actual',0)!=0),"medições informadas"),("ROI realizado","após M&V","depende de dados econômicos")])
    end_section()

elif S.page=="10 Relatórios":
    idx,ipc_v=scores(); gross,net,inv,pb,roi=economic()
    section("10 · Relatórios e pareceres","O sistema transforma os dados do workspace em narrativa executiva, sem perder as limitações e evidências.")
    report=f"""# VITENUS — Diagnóstico e Valorização Circular\n\n## {S.company or 'Cliente'}\nProjeto: {S.project or 'Projeto sem nome'}\n\n### Escopo\n{S.scope_type} — {S.scope_name}\n\n### Evidências\n- Observações: {len(S.observations)}\n- Dados estruturados: {len(S.materials)}\n- Eventos de perda únicos: {len(S.losses)}\n- Oportunidades: {len(S.opportunities)}\n\n### Economia\n- Investimento: {money(inv)}\n- Benefício líquido anual: {money(net)}\n- Payback: {'não calculado' if math.isinf(pb) else f'{pb:.1f} meses'}\n- ROI: {roi:.1f}%\n\n### Priorização\n- IPC: {ipc_v:.1f}/100\n\n### Limitações\nTodo resultado depende das fontes, qualidade dos dados, hipóteses, fatores ambientais e versão metodológica registrados no workspace. Projeções não constituem garantia de resultado.\n"""
    st.download_button("⬇ Baixar parecer executivo (.md)",report,file_name=f"VITENUS_{S.project or 'projeto'}_parecer.md",mime="text/markdown",type="primary")
    st.download_button("⬇ Exportar workspace (.json)",json.dumps(workspace_payload(),ensure_ascii=False,indent=2),file_name="vitenus_workspace.json",mime="application/json")
    st.markdown("### Prévia"); st.markdown(report); end_section()

elif S.page=="11 Dashboard":
    idx,ipc_v=scores(); gross,net,inv,pb,roi=economic()
    section("11 · Dashboard executivo","Uma leitura em camadas: saúde do projeto → evidências → perdas → oportunidades → economia → decisão → monitoramento.")
    why("Como ler o dashboard","O dashboard não é um placar. Ele responde seis perguntas: 1) onde estamos? 2) quão completo está o diagnóstico? 3) onde estão as perdas? 4) quais oportunidades existem? 5) qual é o retorno econômico projetado? 6) o resultado realizado está confirmado? Cada número pode voltar à origem na rastreabilidade.")
    metrics([("Observações",len(S.observations),"campo"),("Eventos de perda",len(S.losses),"sem duplicação"),("Oportunidades",len(S.opportunities),"soluções modeladas"),("IPC",f"{ipc_v:.1f}/100","priorização")])
    c1,c2=st.columns(2)
    with c1:
        if S.losses:
            df=pd.DataFrame(S.losses); st.plotly_chart(px.bar(df,x="id",y="value",color="type",title="Perda econômica por evento"),use_container_width=True)
        else: st.info("Ainda não existem eventos de perda.")
    with c2:
        if S.opportunities:
            odf=pd.DataFrame(S.opportunities); st.plotly_chart(px.bar(odf,x="id",y="benefit",color="family",title="Potencial anual por oportunidade"),use_container_width=True)
        else: st.info("Ainda não existem oportunidades.")
    c1,c2=st.columns(2)
    with c1: st.plotly_chart(px.bar(pd.DataFrame({"Índice":list(idx.keys()),"Valor":list(idx.values())}),x="Índice",y="Valor",range_y=[0,100],title="Perfil de decisão"),use_container_width=True)
    with c2:
        years=list(range(1,max(2,S.horizon_years)+1)); val=-inv; arr=[]
        for y in years: val+=net; arr.append({"Ano":y,"Fluxo acumulado":val})
        st.plotly_chart(px.line(pd.DataFrame(arr),x="Ano",y="Fluxo acumulado",markers=True,title="Retorno econômico projetado"),use_container_width=True)
    st.markdown("### Estado de monitoramento")
    if S.monitor_kpis:
        complete=sum(1 for x in S.monitor_kpis if x.get("baseline",0)!=0 and x.get("actual",0)!=0)
        st.progress(complete/max(len(S.monitor_kpis),1),text=f"{complete}/{len(S.monitor_kpis)} KPIs com baseline + realizado")
    else: st.info("Nenhum KPI foi gerado ainda. Ele aparece automaticamente após a criação das oportunidades.")
    end_section()

elif S.page=="12 Rastreabilidade":
    section("12 · Rastreabilidade","A rastreabilidade responde: de onde veio este número, como foi calculado, quem o informou e qual versão da metodologia estava ativa?")
    why("Objetivo","Rastreabilidade não é uma tabela burocrática. É a camada de prova do sistema. Ela permite reconstruir um resultado: KPI → fórmula → variável → unidade → período → observação/registro → fonte/evidência → responsável → versão metodológica. Isso protege a VITENUS contra números sem origem e permite atualizar um diagnóstico quando uma evidência muda.")
    chains=[]
    for i,o in enumerate(S.observations,1): chains.append((f"Observação O{i}",f"{o.get('note','')} → {o.get('type')} → {o.get('date')} → confiança {o.get('confidence')}"))
    for l in S.losses: chains.append((f"Perda {l['id']}",f"{l['description']} → valor {money(l.get('value',0))} → fonte {l.get('source')} → qualidade {l.get('quality')}/5"))
    for o in S.opportunities: chains.append((f"Oportunidade {o['id']}",f"{o['solution']} → benefício {money(o.get('benefit',0))} → investimento {money(o.get('investment',0))} → Payback {('—' if math.isinf(o.get('payback',float('inf'))) else f'{o.get('payback'):.1f} meses')}"))
    if not chains: st.info("Ainda não existem registros suficientes para reconstruir uma trilha.")
    for title,detail in chains:
        with st.expander(title):
            st.markdown(detail)
            st.caption("Versão metodológica: VITENUS-METHODOLOGY-0.4 · A origem deve permanecer ligada ao registro de campo/documento correspondente.")
    st.markdown("### Teste de rastreabilidade")
    if chains: st.success("A plataforma já consegue reconstruir a origem dos principais registros do workspace. A próxima evolução é persistir cada cadeia como evento versionado no banco.")
    end_section()

elif S.page=="Metodologia VITENUS":
    section("Metodologia VITENUS · V0.4","Um guia didático e interativo: o que fazemos, por que fazemos, quais dados entram, como as fórmulas funcionam e o que pode ser concluído em cada etapa.")
    st.markdown("### O método em uma linha")
    st.markdown("**Observação → Dado → Medição → Diagnóstico → Perda → Oportunidade → Solução → Priorização → Investimento → Resultado → Medição.**")
    tabs=st.tabs(["01 · Preparação","02 · Diagnóstico","03 · Perdas","04 · Oportunidades","05 · Priorização","06 · ROI + Payback","07 · Monitoramento","08 · Rastreabilidade"])
    with tabs[0]:
        st.markdown("#### Preparação")
        st.markdown("A demanda registra a dor declarada. A proposta usa apenas informação limitada e separa fatos de hipóteses. O cadrage define o perímetro real: linha, linhas, setor(es) ou planta.")
        st.info("Regra: antes de afirmar resultado, identificar o que é conhecido, o que é hipótese e o que precisa ser validado.")
    with tabs[1]:
        st.markdown("#### Diagnóstico imersivo")
        st.markdown("A visita deve observar processos, entrevistar pessoas e coletar evidências. O documento-base determina uma abordagem imersiva, com diferentes áreas e pessoas, e coleta processo a processo.")
        st.markdown("**Exemplo:** matéria-prima → processo 01 → processo 02 → produto + perda + resíduo + subproduto.")
    with tabs[2]:
        st.markdown("#### Perdas: uma ocorrência, várias dimensões")
        st.markdown("Uma mesma ocorrência física pode ter dimensão material, econômica, potencial e de risco. O método registra um único evento e evita somar suas dimensões como se fossem eventos diferentes.")
        st.info("Perda econômica = consequência monetária observada. Potencial = valor futuro possível. Risco = exposição associada. Eles não são somados entre si.")
    with tabs[3]:
        st.markdown("#### Oportunidades")
        st.markdown("A hierarquia é **REDUÇÃO → REUTILIZAÇÃO → VALORIZAÇÃO**. A plataforma liga cada oportunidade ao evento de origem e constrói seu próprio Business Case.")
    with tabs[4]:
        st.markdown("#### Índices e IPC")
        st.latex(r"IPC=0,30IE+0,20FT+0,20IA+0,10CI+0,10TN+0,10GR")
        st.markdown("**IE — Impacto Econômico:** nasce do retorno econômico anual relativo ao investimento; o score financeiro é convertido para 0–100.  ")
        st.markdown("**FT — Viabilidade Técnica:** média ponderada de compatibilidade do processo, maturidade tecnológica, equipamentos, modificações, terceiros e necessidade de piloto.  ")
        st.markdown("**IA — Impacto Ambiental:** combina categorias físicas documentadas (matéria-prima virgem evitada, resíduos, energia, água e emissões), redistribuindo pesos quando uma categoria não é aplicável.  ")
        st.markdown("**CI — Complexidade:** avalia áreas, mudanças de processo, fornecedores, parceiros, CAPEX, parada e mudança organizacional; como maior complexidade é desfavorável, o score é invertido.  ")
        st.markdown("**TN — Tempo Necessário:** transforma o prazo de implantação em score; menor duração recebe score maior.  ")
        st.markdown("**GR — Grau de Risco:** avalia risco técnico, financeiro, operacional, regulatório, mercado, fornecedor e qualidade; risco maior reduz o score.  ")
        st.warning("Pesos, escalas e faixas são hipóteses proprietárias V0.4. Não são limites universais nem exigências ISO.")
        with st.expander("Exemplo completo"):
            st.markdown("Uma solução com IE 80, FT 70, IA 90, CI 60, TN 80 e GR 75 terá: **IPC = 0,30×80 + 0,20×70 + 0,20×90 + 0,10×60 + 0,10×80 + 0,10×75 = 77,5/100**. O resultado não decide sozinho: bloqueios regulatórios, segurança, incompatibilidade técnica ou dados insuficientes podem impedir a recomendação.")
            st.markdown("**Referências metodológicas externas:** MFCA / ISO 14051 e ISO 14053 para estruturação de fluxos e custos; família ISO 59004/59010/59020 para princípios e medição de circularidade. A metodologia VITENUS não é uma norma ISO e os pesos do IPC são proprietários.")
    with tabs[5]:
        st.markdown("#### Payback e ROI")
        st.latex(r"Payback=Investimento\ total\/Benefício\ líquido\ periódico")
        st.latex(r"ROI=(Benefícios-OPEX-Investimento)\/Investimento\times100")
        st.markdown("Na proposta, o cálculo é opcional e só aparece quando há dados suficientes e hipóteses explicitadas. Após o diagnóstico, o Business Case deve usar valores mais robustos e, quando possível, fluxo de caixa mensal.")
    with tabs[6]:
        st.markdown("#### KPIs e M&V")
        for k in kpi_catalog(): st.markdown(f"**{k['code']} — {k['name']}** · `{k['unit']}`  \\  Fórmula: {k['formula']}")
        st.markdown("O baseline representa a referência; o período de desempenho fornece o realizado. O sistema calcula a variação e, quando os dados econômicos existem, conecta o KPI ao benefício realizado.")
    with tabs[7]:
        st.markdown("#### Rastreabilidade")
        st.markdown("Cada número importante precisa poder voltar à evidência que o originou. A trilha lógica é: **resultado → fórmula → variável → unidade → período → registro → fonte → responsável → versão metodológica**.")
    end_section()

# ----------------------------- footer -----------------------------
st.markdown("<div class='small' style='text-align:center;margin-top:40px'>VITENUS · Circular Engine V0.4 · Protótipo operacional para testes internos</div>",unsafe_allow_html=True)
