# VITENUS Circular Engine — MVP 0.1

Moteur de diagnostic, valorisation circulaire, priorisation, Payback, ROI et suivi de performance.

> **Statut : prototype de recherche appliquée.** Les seuils, pondérations et règles de décision sont des hypothèses V0.1 à calibrer sur des données pilotes. Ils ne constituent ni des seuils ISO ni des seuils universels de rentabilité.

## Architecture

- **Streamlit** : interface et dashboard.
- **Supabase/PostgreSQL** : entreprises, projets, observations, opportunités, business cases, scores et mesures réelles.
- **GitHub** : versionnement, migrations SQL et CI.
- **Python** : moteur déterministe de calcul.
- **pytest** : tests des formules et invariants.

## Correction des formules

Tous les indices finaux sont sur 0–100 avant l'IPC :

```text
IPC = 0.30 IE + 0.20 FT + 0.20 IA + 0.10 CI + 0.10 TN + 0.10 GR
```

Pour les critères 1–10 :

```text
score_pondéré = Σ(score_i × poids_i)
indice_final = score_pondéré × 10
```

Pour CI et GR, la note 1 signifie faible complexité/risque et 10 forte complexité/risque ; l'indice final inverse donc la note :

```text
indice = 10 × (11 - score_pondéré)
```

### IE

```text
BEA = économies matière + économies déchets + économies énergie + économies eau + revenus additionnels + autres bénéfices
BEN = BEA - OPEX additionnel
REA = BEN / investissement
IE = score_REA(1..10) × 10
```

### FT

Compatibilité procédé 25 %, maturité technologique 20 %, disponibilité équipements 15 %, complexité modifications 15 %, dépendance tiers 10 %, besoin pilote/validation 15 %.

### IA

Matière vierge évitée 30 %, déchets évités/récupérés 25 %, énergie 15 %, eau 10 %, émissions 20 %. Les catégories non applicables voient leur poids redistribué. Une catégorie sans donnée quantitative n'est pas automatiquement considérée comme un bénéfice.

### TN

≤1 mois=10, >1–2=9, >2–3=8, >3–4=7, >4–6=6, >6–9=5, >9–12=4, >12–18=3, >18–24=2, >24=1 ; puis ×10.

### ROI

Le ROI est un calcul, pas un seuil scientifique universel. V0.1 utilise des bandes de screening configurables :

| ROI | Bande V0.1 |
|---:|---|
| < 0 % | négatif |
| 0–<10 % | positif faible |
| 10–<20 % | positif |
| 20–<35 % | élevé |
| ≥35 % | très élevé |

Une opportunité doit en plus satisfaire le **hurdle rate** du projet. La valeur par défaut de 15 % dans l'interface est un paramètre de test, pas une recommandation universelle.

## Payback

Payback simple :

```text
Payback_mois = Investissement_total / (BEN_annuel / 12)
```

Payback projeté par flux :

```text
CF_t = BN_t - I_t
CFC_t = CFC_(t-1) + CF_t
Payback = t-1 + |CFC_(t-1)| / CF_t
```

La seconde méthode est celle à privilégier dès que les flux varient dans le temps.

## Qualité des données et traçabilité

Chaque variable matériellement importante doit avoir unité, période, source, méthode, qualité, propriétaire et date de vérification. Le `Data Confidence Score` est un indicateur de gouvernance documentaire, pas un intervalle de confiance statistique.

Chaîne de traçabilité : `KPI → formule → variable → observation → source/preuve → vérification → version méthodologique`.

## Référentiels scientifiques

Le design s'inspire des cadres ISO 14051:2011 (MFCA), ISO 14053:2021 (MFCA par phases), ISO 14031:2021 (évaluation de performance environnementale), ISO 50015:2014 (mesure/vérification énergétique), ISO 59010:2024 (modèles économiques/réseaux de valeur circulaires) et ISO 59020:2024 (mesure/évaluation de circularité). Le produit n'est pas une certification de conformité ISO.

Sources officielles :
- https://www.iso.org/standard/50986.html
- https://www.iso.org/standard/73338.html
- https://www.iso.org/standard/81453.html
- https://www.iso.org/standard/60043.html
- https://www.iso.org/standard/80649.html
- https://www.iso.org/standard/80650.html

## Installation

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Copier `.env.example` vers `.env` et renseigner Supabase.

## Supabase

1. Créer le projet.
2. Exécuter `sql/001_schema.sql`.
3. Exécuter `sql/002_seed.sql`.
4. Ajouter les secrets dans l'environnement de déploiement.
5. Ne jamais exposer une clé `service_role` dans le navigateur.

## Validation pilote

1. définir frontière système et baseline ;
2. collecter données brutes et preuves ;
3. calculer business case et six indices ;
4. tester sensibilité des poids ;
5. décider selon IPC + économie + bloqueurs ;
6. mesurer après implantation ;
7. calculer ROI/Payback réalisés ;
8. comparer prévision/réalité ;
9. calibrer seulement après plusieurs projets pilotes.
