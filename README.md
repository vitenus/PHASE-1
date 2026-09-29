# VITENUS Circular Engine — V0.4 réparée / opérationnelle

Prototype interne de la plateforme **Diagnóstico e Valorização Circular** de VITENUS.

## Ce que cette révision corrige

- Interface opérationnelle orientée workspace, et non formulaire.
- Proposition économique : aucun Payback/ROI inventé lorsque les données sont insuffisantes.
- Structure de retour préliminaire avec séparation entre données connues, hypothèses et données à valider.
- Investissements détaillés : CAPEX, ingénierie, installation, commissioning, formation, honoraires, contingence et autres coûts décrits.
- Identification des pertes : un événement unique peut avoir plusieurs dimensions sans être compté plusieurs fois.
- Opportunités liées à un événement de perte unique.
- Priorisation entièrement en portugais, avec explication des six indices et de l'IPC.
- Plan d'action avec Business Case, scénarios, gates et logique méthodologique.
- Monitoring avec catalogue prédéfini de KPIs et génération automatique selon la famille d'opportunité.
- Dashboard par couches : avancement, pertes, opportunités, économie, priorisation et suivi.
- Traçabilité expliquée comme une chaîne de preuve : résultat → formule → variable → unité → période → registre → source → responsable → version.
- Méthodologie interactive avec exemples, formules et références.
- Correction de `StreamlitWidgetAlreadyInstantiatedError` lors de l'ajout des secteurs/lignes : les valeurs des widgets ne sont plus mutées après leur instanciation.

## Déploiement

1. Garder `app.py`, `db.py`, les modules Python et les dossiers `.streamlit`, `sql`, `tests` à la racine du dépôt.
2. Installer les dépendances de `requirements.txt`.
3. Appliquer les migrations Supabase dans l'ordre : `001_schema.sql`, `002_seed.sql`, `003_workflow.sql`, `004_workspace.sql`.
4. Configurer `SUPABASE_URL` et `SUPABASE_KEY` dans les secrets de Streamlit Cloud.

## Validation locale effectuée

- `python -m py_compile app.py` : OK
- `pytest -q tests` : **9 passed**

Le test visuel complet doit être effectué dans Streamlit Cloud ou dans un environnement disposant de Streamlit.
