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
:root{--ink:#17231f;--muted:#68756f;--line:#dfe7e2;--soft:#f5f8f6;--deep:#12352c;--mint:#dff3e9;--lime:#bde56d;--accent:#2f8f6b;--gold:#e7b84b;--danger:#c95858;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink)}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif;letter-spacing:-.03em}
.block-container{padding-top:1.1rem;padding-bottom:4rem;max-width:1500px}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#102f28 0%,#0b241f 100%)}
[data-testid="stSidebar"] *{color:#eaf4ef!important}
[data-testid="stSidebar"] .stButton button{border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.05);text-align:left;border-radius:12px}
[data-testid="stSidebar"] .stButton button:hover{background:rgba(189,229,109,.14);border-color:rgba(189,229,109,.4)}
.hero{background:radial-gradient(circle at 85% 10%,rgba(189,229,109,.24),transparent 28%),linear-gradient(135deg,#12352c,#1b5a47);border-radius:28px;padding:34px 38px;color:#fff;box-shadow:0 18px 50px rgba(18,53,44,.16);margin-bottom:22px}
.hero h1{font-size:42px;margin:8px 0}.hero p{max-width:850px;color:#d8e8e1;font-size:16px}.eyebrow{font-size:12px;letter-spacing:.15em;text-transform:uppercase;color:#cceaa8;font-weight:700}
.section{border:1px solid var(--line);border-radius:22px;padding:22px;background:#fff;box-shadow:0 7px 25px rgba(20,40,32,.05);margin-bottom:18px}
.card{border:1px solid var(--line);border-radius:18px;padding:18px;background:#fff;box-shadow:0 6px 20px rgba(20,40,32,.045);height:100%}
.card .label{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}.card .value{font-family:'Space Grotesk';font-size:30px;font-weight:700;margin-top:5px}.card .hint{font-size:12px;color:var(--muted);margin-top:4px}
.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:12px 0 22px}.metric{background:var(--soft);border-radius:18px;padding:18px;border:1px solid var(--line)}
.metric strong{font-family:'Space Grotesk';font-size:27px}.metric span{display:block;color:var(--muted);font-size:12px;margin-top:3px}
.pill{display:inline-block;padding:6px 10px;border-radius:999px;background:var(--mint);color:var(--deep);font-size:12px;font-weight:700}.pill.gold{background:#fff3cf}.pill.red{background:#fde5e5;color:#8e3333}
.callout{border-left:4px solid var(--accent);background:#f2f8f5;padding:14px 17px;border-radius:0 14px 14px 0;margin:12px 0}.warn{border-left-color:var(--gold);background:#fff9e9}.danger{border-left-color:var(--danger);background:#fff2f2}
.flow{display:flex;gap:8px;align-items:center;overflow-x:auto;padding:8px 0 14px}.flow .node{min-width:120px;padding:13px;border:1px solid var(--line);border-radius:16px;background:#fff;text-align:center;font-size:12px}.flow .arrow{color:#8b9892;font-size:18px}
.stButton button{border-radius:12px;font-weight:600}.stTextInput input,.stNumberInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]>div{border-radius:12px!important;border-color:#d6e0da!important}
[data-testid="stExpander"]{border-radius:16px!important;border:1px solid var(--line)!important}
.small{font-size:12px;color:var(--muted)}
@media(max-width:900px){.metric-grid{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:32px}}
</style>
""", unsafe_allow_html=True)

# ----------------------------- State -----------------------------
DEFAULT = {
    "page":"Central do projeto","company":"","project":"","sector":"","scope_type":"Linha de produção","scope_name":"",
    "request_status":"Nova", "request_origin":"Indicação", "declared_problem":"", "initial_data":"", "proposal_justification":"",
    "capex":0.0,"initial_costs":0.0,"consulting_fee":0.0,"other_investment":0.0,"savings_material":0.0,"savings_waste":0.0,"savings_energy":0.0,"savings_water":0.0,"revenue_additional":0.0,"other_savings":0.0,"opex":0.0,
    "implementation_months":12.0,"horizon_years":5,"consulting_benefit":0.0,
    "areas":[],"lines":[],"processes":[],"observations":[],"materials":[],"losses":[],"opportunities":[],"visits":[],"kpis":[],
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
        if name: add_item("areas",{"name":name,"type":st.session_state.new_area_type,"notes":st.session_state.new_area_notes}); st.session_state.new_area=""; st.rerun()
    if kind=="line":
        name=st.session_state.get("new_line","").strip();
        if name: add_item("lines",{"name":name,"area":st.session_state.new_line_area,"product":st.session_state.new_line_product,"volume":st.session_state.new_line_volume,"unit":st.session_state.new_line_unit}); st.session_state.new_line=""; st.rerun()

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
    gross,net,inv,pb,roi=economic()
    section("01 · Proposta e qualificação","Aqui a VITENUS trabalha com informação limitada. O objetivo é construir uma hipótese econômica e operacional, não um diagnóstico final.")
    why("Limite metodológico","Nesta etapa não devemos afirmar causa definitiva, economia garantida, ROI garantido, Payback garantido, impacto ambiental definitivo ou viabilidade técnica comprovada. Esses pontos dependem da investigação posterior.")
    c1,c2,c3=st.columns(3)
    with c1: S.scope_type=st.selectbox("Perímetro preliminar",["Linha de produção","Mais de uma linha","Setor","Mais de um setor","Planta inteira","Outro"]); S.scope_name=st.text_input("Escopo descrito",S.scope_name)
    with c2: st.number_input("Investimento / CAPEX preliminar",min_value=0.0,value=S.capex,key="p_capex",on_change=lambda:None); S.capex=st.session_state.p_capex; st.number_input("Custos iniciais",min_value=0.0,value=S.initial_costs,key="p_initial"); S.initial_costs=st.session_state.p_initial
    with c3: st.number_input("Honorários VITENUS",min_value=0.0,value=S.consulting_fee,key="p_fee"); S.consulting_fee=st.session_state.p_fee; st.number_input("Outros investimentos",min_value=0.0,value=S.other_investment,key="p_other"); S.other_investment=st.session_state.p_other
    st.markdown("### Benefícios preliminares")
    cols=st.columns(3)
    fields=[("savings_material","Economia de matéria-prima"),("savings_waste","Economia na gestão de resíduos"),("savings_energy","Economia de energia"),("savings_water","Economia de água"),("revenue_additional","Receita adicional"),("other_savings","Outras economias")]
    for i,(key,label) in enumerate(fields):
        with cols[i%3]: S[key]=st.number_input(label,min_value=0.0,value=float(S[key]),key="p_"+key)
    S.opex=st.number_input("OPEX adicional anual",min_value=0.0,value=float(S.opex),key="p_opex")
    metrics([("Investimento total",money(inv),"CAPEX + custos + honorários"),("Benefício líquido anual",money(net),"benefícios − OPEX adicional"),("Payback preliminar",("—" if math.isinf(pb) else f"{pb:.1f} meses"),"projeção"),("ROI anual projetado",pct(roi),"não é garantia")])
    fig=pd.DataFrame({"Categoria":["Matéria","Resíduos","Energia","Água","Receita","Outros"],"Valor":[S.savings_material,S.savings_waste,S.savings_energy,S.savings_water,S.revenue_additional,S.other_savings]})
    st.plotly_chart(px.bar(fig,x="Categoria",y="Valor",title="Composição do benefício anual preliminar"),use_container_width=True)
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
    section("05 · Identificação de perdas","Aqui o sistema começa a transformar observações em diagnóstico.")
    why("Quatro lentes de perda","A arquitetura do serviço separa perda material, perda econômica, potencial de valorização e perda/risco estratégico. A classificação pode evoluir durante os testes do método.")
    c1,c2=st.columns(2)
    with c1: st.selectbox("Processo relacionado",["—"]+[o.get("process") for o in S.observations if o.get("process")],key="l_process"); st.selectbox("Tipo de perda",["Material","Econômica","Potencial","Estratégica"],key="l_type"); st.text_input("Descrição",key="l_desc")
    with c2: st.number_input("Quantidade anual",min_value=0.0,key="l_qty"); st.text_input("Unidade",value="kg/ano",key="l_unit"); st.number_input("Custo / valor anual",min_value=0.0,key="l_value"); st.text_input("Causa provável",key="l_cause")
    if st.button("+ Registrar perda",type="primary"):
        S.losses.append({"process":S.l_process,"type":S.l_type,"description":S.l_desc,"qty":S.l_qty,"unit":S.l_unit,"value":S.l_value,"cause":S.l_cause}); st.rerun()
    if S.losses:
        df=pd.DataFrame(S.losses); metrics([("Perdas registradas",len(df),"diagnóstico"),("Valor anual mapeado",money(df.value.sum()),"soma dos valores informados"),("Quantidade material",f"{df.qty.sum():,.0f}","unidades informadas"),("Tipos",df.type.nunique(),"classes")])
        st.plotly_chart(px.bar(df,x="description",y="value",color="type",title="Mapa econômico das perdas"),use_container_width=True)
    end_section()

elif S.page=="06 Oportunidades":
    section("06 · Oportunidades circulares","Transforme uma perda ou fluxo em uma hipótese de solução.")
    if not S.losses: st.info("Primeiro registre perdas em 05 Perdas. As oportunidades serão ligadas a elas.")
    c1,c2,c3=st.columns(3)
    with c1: st.selectbox("Perda de origem",["—"]+[x["description"] for x in S.losses],key="o_loss"); st.selectbox("Família",["Redução","Reutilização","Valorização"],key="o_family")
    with c2: st.text_input("Solução proposta",key="o_solution"); st.text_input("Mercado / destino",key="o_market"); st.text_input("Tecnologia / parceiro",key="o_tech")
    with c3: st.number_input("Benefício anual estimado",min_value=0.0,key="o_benefit"); st.number_input("Investimento estimado",min_value=0.0,key="o_invest"); st.number_input("OPEX adicional anual",min_value=0.0,key="o_opex")
    if st.button("+ Criar oportunidade",type="primary"):
        b=float(S.o_benefit); inv=float(S.o_invest); op=float(S.o_opex); pb=simple_payback_months(inv,max(b-op,0)) if inv>0 else float('inf'); r=((b-op-inv)/inv*100) if inv>0 else 0
        S.opportunities.append({"loss":S.o_loss,"family":S.o_family,"solution":S.o_solution,"market":S.o_market,"tech":S.o_tech,"benefit":b,"investment":inv,"opex":op,"payback":pb,"roi":r}); st.rerun()
    for i,o in enumerate(S.opportunities):
        with st.container(border=True):
            a,b,c=st.columns([1,2,1]); a.markdown(f"**{o['family']}**"); b.markdown(f"### {o['solution'] or 'Solução sem nome'}\n{o['loss']}"); c.metric("Payback",("—" if math.isinf(o['payback']) else f"{o['payback']:.1f} m")); st.progress(min(max(o['roi'],0)/200,1),text=f"ROI projetado · {o['roi']:.1f}%")
    end_section()

elif S.page=="07 Priorização":
    section("07 · Priorização","Só pontue depois de ter dados, perdas e oportunidades modeladas.")
    idx,ipc_v=scores(); metrics([("IPC",f"{ipc_v:.1f}/100",ipc_band(ipc_v).replace('_',' ')),("IE",f"{idx['IE']:.0f}","impacto econômico"),("IA",f"{idx['IA']:.0f}","impacto ambiental"),("FT",f"{idx['FT']:.0f}","viabilidade técnica")])
    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown("**Viabilidade técnica · 1–10**")
        for k in S.ft: S.ft[k]=st.slider(k.replace('_',' ').title(),1,10,int(S.ft[k]),key="ft_"+k)
    with c2:
        st.markdown("**Complexidade · 1–10 (menor é melhor)**")
        for k in S.ci: S.ci[k]=st.slider(k.replace('_',' ').title(),1,10,int(S.ci[k]),key="ci_"+k)
    with c3:
        st.markdown("**Risco · 1–10 (menor é melhor)**")
        for k in S.gr: S.gr[k]=st.slider(k.title(),1,10,int(S.gr[k]),key="gr_"+k)
    st.markdown("### Impactos ambientais estimados (%)")
    cols=st.columns(5); labels=list(S.env.keys())
    for i,k in enumerate(labels):
        with cols[i]: S.env[k]=st.number_input(k.replace('_',' ').title(),min_value=0.0,max_value=1000.0,value=float(S.env[k]),key="env_"+k)
    df=pd.DataFrame({"Índice":list(idx.keys()),"Valor":[idx[k] for k in idx]}); st.plotly_chart(px.bar_polar(df,r="Valor",theta="Índice",range_r=[0,100],title="Perfil de priorização"),use_container_width=True)
    end_section()

elif S.page=="08 Plano + ROI":
    gross,net,inv,pb,roi=economic(); section("08 · Plano de ação + ROI","A solução deixa de ser apenas uma ideia e vira uma implantação mensurável.")
    metrics([("Investimento",money(inv),"base econômica"),("Benefício líquido anual",money(net),"após OPEX adicional"),("Payback",("—" if math.isinf(pb) else f"{pb:.1f} meses"),"projetado"),("ROI",pct(roi),"projetado")])
    st.markdown("### Curva de retorno")
    years=list(range(1,max(2,S.horizon_years)+1)); cum=[]; val=-inv
    for y in years: val+=net; cum.append(val)
    st.plotly_chart(px.line(pd.DataFrame({"Ano":years,"Fluxo acumulado":cum}),x="Ano",y="Fluxo acumulado",markers=True,title="Fluxo de caixa acumulado projetado"),use_container_width=True)
    st.markdown("### Plano de implementação")
    c1,c2,c3=st.columns(3)
    with c1: st.text_input("Ação",key="a_action"); st.text_input("Responsável",key="a_owner")
    with c2: st.number_input("Prazo (meses)",min_value=0.0,key="a_time"); st.selectbox("Gate",["Validar dados","Piloto","Investimento","Implementação","M&V"],key="a_gate")
    with c3: st.text_area("Critério de conclusão",key="a_done",height=80)
    if st.button("+ Adicionar ação"): S.kpis.append({"action":S.a_action,"owner":S.a_owner,"time":S.a_time,"gate":S.a_gate,"done":S.a_done}); st.rerun()
    for a in S.kpis: st.markdown(f"**{a['action']}** · {a['owner']} · {a['time']} mês(es) · `{a['gate']}` — {a['done']}")
    end_section()

elif S.page=="09 Monitoramento":
    section("09 · Monitoramento","Depois da implementação, a pergunta muda: o resultado projetado aconteceu de verdade?")
    why("Medição","O desempenho realizado deve ser comparado com uma linha de base adequada e com o período de desempenho. Para evitar dupla contagem, cada benefício precisa ter origem, fórmula, unidade, período, responsável e evidência.")
    c1,c2,c3=st.columns(3)
    with c1: st.text_input("KPI",key="k_name"); st.number_input("Baseline",key="k_base"); st.number_input("Realizado",key="k_actual")
    with c2: st.text_input("Unidade",value="R$/ano",key="k_unit"); st.selectbox("Fonte",["Medição","ERP","Documento","Entrevista","Estimativa"],key="k_source")
    with c3: st.text_input("Período",value=str(date.today()),key="k_period"); st.text_area("Evidência / observação",key="k_note",height=80)
    if st.button("+ Adicionar KPI",type="primary"): S.kpis.append({"action":S.k_name,"owner":"Monitoramento","time":0,"gate":"M&V","done":f"Baseline {S.k_base} → Real {S.k_actual} {S.k_unit} · {S.k_source} · {S.k_period} · {S.k_note}"}); st.rerun()
    if S.kpis:
        st.markdown("### Indicadores registrados")
        for k in S.kpis: st.markdown(f"<div class='card'><b>{k['action']}</b><div class='small'>{k['done']}</div></div><br>",unsafe_allow_html=True)
    end_section()

elif S.page=="10 Relatórios":
    idx,ipc_v=scores(); gross,net,inv,pb,roi=economic()
    section("10 · Relatórios e pareceres","Gere uma síntese executiva a partir do que já existe no workspace.")
    report=f"""# VITENUS — Diagnóstico e Valorização Circular\n\n## {S.company or 'Cliente'}\nProjeto: {S.project or 'Projeto sem nome'}\n\n### Escopo\n{S.scope_type} — {S.scope_name}\n\n### Síntese econômica\n- Investimento estimado: {money(inv)}\n- Benefício líquido anual: {money(net)}\n- Payback projetado: {'não alcançado na simulação' if math.isinf(pb) else f'{pb:.1f} meses'}\n- ROI projetado: {roi:.1f}%\n\n### Diagnóstico\n- Observações de campo: {len(S.observations)}\n- Materiais/dados estruturados: {len(S.materials)}\n- Perdas identificadas: {len(S.losses)}\n- Oportunidades modeladas: {len(S.opportunities)}\n\n### Priorização\n- IE: {idx['IE']:.1f}\n- FT: {idx['FT']:.1f}\n- IA: {idx['IA']:.1f}\n- CI: {idx['CI']:.1f}\n- TN: {idx['TN']:.1f}\n- GR: {idx['GR']:.1f}\n- IPC: {ipc_v:.1f}/100\n\n### Limitações\nOs resultados devem ser interpretados segundo as fontes, qualidade dos dados, hipóteses e versão metodológica registradas no workspace. Projeções econômicas não constituem garantia de resultado.\n"""
    st.download_button("⬇ Baixar parecer executivo (.md)",report,file_name=f"VITENUS_{S.project or 'projeto'}_parecer.md",mime="text/markdown",type="primary")
    st.download_button("⬇ Exportar workspace (.json)",json.dumps(workspace_payload(),ensure_ascii=False,indent=2),file_name="vitenus_workspace.json",mime="application/json")
    st.markdown("### Prévia")
    st.markdown(report)
    end_section()

elif S.page=="11 Dashboard":
    idx,ipc_v=scores(); gross,net,inv,pb,roi=economic(); section("11 · Dashboard executivo","A visão para gestão: onde estamos, quanto existe de potencial e o que precisa acontecer agora.")
    metrics([("Potencial líquido anual",money(max(net,0)),"projetado"),("Payback",("—" if math.isinf(pb) else f"{pb:.1f} m"),"projetado"),("ROI",pct(roi),"projetado"),("IPC",f"{ipc_v:.1f}",ipc_band(ipc_v).replace('_',' '))])
    c1,c2=st.columns(2)
    with c1:
        st.plotly_chart(px.bar(pd.DataFrame({"Índice":list(idx.keys()),"Valor":list(idx.values())}),x="Índice",y="Valor",range_y=[0,100],title="Perfil de decisão"),use_container_width=True)
    with c2:
        if S.losses: st.plotly_chart(px.pie(pd.DataFrame(S.losses),names="type",values="value",title="Distribuição do valor das perdas"),use_container_width=True)
        else: st.info("Registre perdas para gerar a distribuição.")
    end_section()

elif S.page=="12 Rastreabilidade":
    section("12 · Rastreabilidade","Nenhum número importante deve existir sem saber de onde veio.")
    rows=[]
    for i,o in enumerate(S.observations,1): rows.append({"KPI / dado":f"Observação {i}","Fonte":o.get("type"),"Processo":o.get("process"),"Período":o.get("date"),"Qualidade":o.get("confidence"),"Versão":"VITENUS-METHODOLOGY-0.4"})
    for i,m in enumerate(S.materials,1): rows.append({"KPI / dado":m.get("name"),"Fonte":m.get("source"),"Processo":"—","Período":"—","Qualidade":m.get("quality"),"Versão":"VITENUS-METHODOLOGY-0.4"})
    if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    else: st.info("Ainda não há dados suficientes para montar a trilha de rastreabilidade.")
    st.markdown("**Estrutura:** KPI → fórmula → variável → unidade → período → observação → fonte/evidência → responsável → versão metodológica.")
    end_section()

elif S.page=="Metodologia VITENUS":
    section("Metodologia VITENUS · V0.4","A metodologia continua explicada dentro do sistema, mas agora está subordinada ao fluxo operacional.")
    cards=[("M00","Entrada e qualificação","Entender empresa, produto, dor declarada e dados iniciais."),("M01","Cadrage","Definir perímetro: linha, linhas, setor(es) ou planta."),("M02","Diagnóstico imersivo","Observar processos, entrevistar pessoas e registrar evidências."),("M03","Transformação","Converter observações em variáveis, unidades, períodos, fontes e qualidade."),("M04","Perdas","Classificar e mensurar perdas materiais, econômicas, potenciais e estratégicas."),("M05","Oportunidades","Conceber redução, reutilização e valorização."),("M06","Priorização","Aplicar IE, FT, IA, CI, TN, GR e IPC."),("M07","Business Case","Calcular investimento, benefícios, OPEX, Payback e ROI."),("M08","Plano","Definir ações, responsáveis, prazos e gates."),("M09","Monitoramento","Comparar baseline, meta e realizado; calcular retorno realizado."),("M10","Rastreabilidade","Conectar resultado, fórmula, dado, fonte e versão.")]
    for i in range(0,len(cards),3):
        cols=st.columns(3)
        for c,(code,title,desc) in zip(cols,cards[i:i+3]):
            with c: st.markdown(f"<div class='card'><span class='pill'>{code}</span><h3>{title}</h3><div class='small'>{desc}</div></div>",unsafe_allow_html=True)
    st.markdown("### Premissas importantes")
    st.markdown("- Os pesos e faixas do IPC são hipóteses proprietárias V0.4 e devem ser testados e calibrados com pilotos.\n- O DCS é um mecanismo de governança da qualidade dos dados, não um intervalo estatístico.\n- Payback e ROI projetados são cenários; o resultado realizado depende da implementação e da medição.\n- A plataforma deve guardar evidências e versões para permitir auditoria interna.")
    end_section()

# ----------------------------- footer -----------------------------
st.markdown("<div class='small' style='text-align:center;margin-top:40px'>VITENUS · Circular Engine V0.4 · Protótipo operacional para testes internos</div>",unsafe_allow_html=True)
