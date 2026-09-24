import streamlit as st
from datetime import date
from vitenus.scoring import economic_index, technical_feasibility_index, environmental_index, implementation_complexity_index, time_index, risk_index, ipc, ipc_band
from vitenus.economics import annual_gross_benefit, net_annual_benefit, simple_payback_months, project_roi_percent
from vitenus.recommendation import recommend
from dotenv import load_dotenv
from vitenus.db import get_client, save_assessment
load_dotenv()

st.set_page_config(page_title='VITENUS Circular Engine', layout='wide')
st.title('VITENUS Circular Engine — V0.1')
st.caption('Prototype de recherche appliquée — résultats à valider avec données pilotes.')
with st.sidebar:
    st.header('Paramètres')
    investment=st.number_input('Investissement total (R$)',min_value=0.0,value=100000.0)
    opex=st.number_input('OPEX additionnel annuel (R$)',min_value=0.0,value=5000.0)
    hurdle=st.number_input('Hurdle rate / taux minimal (%)',min_value=-100.0,value=15.0)
    months=st.number_input("Temps d'implantation (mois)",min_value=0.0,value=6.0)
    dcs=st.slider('Data Confidence Score',0,100,80)

st.header('1. Business case')
c=st.columns(5)
sm=c[0].number_input('Économies matière/an',min_value=0.0,value=30000.0)
sw=c[1].number_input('Économies déchets/an',min_value=0.0,value=10000.0)
se=c[2].number_input('Économies énergie/an',min_value=0.0,value=5000.0)
swa=c[3].number_input('Économies eau/an',min_value=0.0,value=2000.0)
rev=c[4].number_input('Revenus additionnels/an',min_value=0.0,value=20000.0)
gross=annual_gross_benefit(sm,sw,se,swa,rev)
net=net_annual_benefit(gross,opex)
roi=project_roi_percent(gross,opex,investment) if investment else 0
payback=simple_payback_months(investment,net)
for col,label,value in zip(st.columns(4),['BEA annuel','BEN annuel','ROI projeté','Payback simple'],[f'R$ {gross:,.0f}',f'R$ {net:,.0f}',f'{roi:.1f}%',('∞' if payback==float('inf') else f'{payback:.1f} mois')]): col.metric(label,value)

st.header('2. Six indices')
left,right=st.columns(2)
with left:
    st.subheader('IE — Impact économique'); ie=economic_index((net/investment*100) if investment else 0); st.write(f'IE = **{ie:.1f}/100**')
    st.subheader('FT — Faisabilité technique'); ft_inputs={k:st.slider(label,1,10,7) for label,k in [('Compatibilité du procédé','process_compatibility'),('Maturité technologique','technology_maturity'),('Disponibilité des équipements','equipment_availability'),('Complexité des modifications','modification_complexity'),('Dépendance à des tiers','third_party_dependency'),('Besoin de pilote/validation','pilot_validation_need')]}; ft=technical_feasibility_index(ft_inputs); st.write(f'FT = **{ft:.1f}/100**')
    st.subheader('IA — Impact environnemental'); imp={k:st.number_input(label,min_value=0.0,value=val) for label,k,val in [('Matière vierge évitée (%)','virgin_material_avoided',20.0),('Déchets évités/récupérés (%)','waste_avoided_recovered',30.0),('Énergie évitée (%)','energy_avoided',10.0),('Eau évitée (%)','water_avoided',5.0),('Émissions évitées (%)','emissions_avoided',15.0)]}; ia,_=environmental_index(imp); st.write(f'IA = **{ia:.1f}/100**')
with right:
    st.subheader("CI — Complexité d'implantation"); ci_inputs={k:st.slider(label,1,10,4) for label,k in [('Départements impliqués','departments'),('Changements de procédé','process_changes'),('Complexité fournisseurs','suppliers'),('Complexité partenaires','partners'),('Complexité CAPEX','capex_complexity'),('Arrêt de production','production_downtime'),('Changement organisationnel','organizational_change')]}; ci=implementation_complexity_index(ci_inputs); st.write(f'CI = **{ci:.1f}/100**')
    st.subheader('TN — Temps nécessaire'); tn=time_index(months); st.write(f'TN = **{tn:.1f}/100**')
    st.subheader('GR — Degré de risque'); gr_inputs={k:st.slider(label,1,10,3) for label,k in [('Technique','technical'),('Financier','financial'),('Opérationnel','operational'),('Réglementaire','regulatory'),('Marché','market'),('Fournisseur','supplier'),('Qualité','quality')]}; gr=risk_index(gr_inputs); st.write(f'GR = **{gr:.1f}/100**')

indices={'IE':ie,'FT':ft,'IA':ia,'CI':ci,'TN':tn,'GR':gr}; ipc_value=ipc(indices)
st.header('3. IPC'); st.metric('Indice de Priorisation Circulaire',f'{ipc_value:.1f}/100'); st.write(f'Classe V0.1 : **{ipc_band(ipc_value)}**')
st.header('4. Gouvernance')
reg=st.checkbox('Bloqueur réglementaire'); safety=st.checkbox('Bloqueur sécurité'); tech=st.checkbox('Incompatibilité technique'); risk=st.checkbox('Risque critique'); market=st.checkbox('Marché disponible',True); supplier=st.checkbox('Fournisseur disponible',True)
st.json(recommend(ipc_value,roi,payback,dcs,hurdle,reg,safety,tech,risk,market,supplier))
st.header('5. Sauvegarde Supabase')
company_name=st.text_input('Entreprise pilote', 'Entreprise pilote')
project_name=st.text_input('Projet', 'Diagnostic circularité V0.1')
opportunity_name=st.text_input('Opportunité', 'Opportunité test')
if st.button('Enregistrer le calcul dans Supabase'):
    try:
        client=get_client()
        trace={'indices':indices,'weights':{'IE':.30,'FT':.20,'IA':.20,'CI':.10,'TN':.10,'GR':.10},'formula_version':'VITENUS-METHODOLOGY-0.1'}
        payload={**indices,'IPC':ipc_value,'recommendation':decision['decision'],'trace':trace}
        result=save_assessment(client,company_name,project_name,opportunity_name,payload,roi,payback,dcs)
        st.success(f"Calcul enregistré. Score ID: {result[3]['id']}")
    except Exception as exc:
        st.error(f'Enregistrement impossible : {exc}')

st.header('6. Traçabilité')
st.info('En production : KPI → formule → variable → unité → période → observation → source/preuve → responsable → version méthodologique.')
st.caption(f'VITENUS-METHODOLOGY-0.1 • {date.today().isoformat()}')
