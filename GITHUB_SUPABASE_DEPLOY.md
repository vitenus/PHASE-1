# Déploiement GitHub + Supabase

## GitHub

```bash
git init
git add .
git commit -m "feat: VITENUS Circular Engine V0.1"
git branch -M main
git remote add origin <VOTRE_REPO_GITHUB>
git push -u origin main
```

## Supabase

1. Créer un projet Supabase.
2. SQL Editor → exécuter `sql/001_schema.sql`.
3. Exécuter `sql/002_seed.sql`.
4. Définir `SUPABASE_URL` et `SUPABASE_KEY` dans l'environnement Streamlit.
5. Pour une application multi-client, mettre en place Auth + Row Level Security avant d'autoriser plusieurs organisations.

La V0.1 sauvegarde chaque calcul avec sa version méthodologique et une trace JSON des pondérations. Cela permet de reproduire le résultat après évolution du moteur.

## Streamlit Community Cloud / autre hébergeur

Ajouter les secrets :

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_KEY"
```

Ne jamais mettre `service_role` dans GitHub, dans le code source ou dans le navigateur.
