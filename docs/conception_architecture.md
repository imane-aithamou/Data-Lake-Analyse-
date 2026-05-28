# Conception de l'architecture Data Lake - Mexora RH Intelligence

## 1. Objectif du Data Lake

Mexora RH Intelligence utilise un Data Lake pour analyser le marche de l'emploi IT au Maroc. Les donnees proviennent d'offres d'emploi, d'un referentiel de competences IT et d'un fichier d'entreprises marocaines.

L'objectif est de transformer des donnees brutes en indicateurs utiles pour la decision RH : competences les plus demandees, profils recherches, salaires medians, villes dynamiques et entreprises concurrentes.

## 2. Architecture generale

```text
Sources brutes
    -> Bronze
    -> Silver
    -> Gold
    -> DuckDB, notebook, dashboard et rapports
```

### Sources brutes

Les fichiers d'entree sont places dans `data/raw/` :

- `offres_emploi_it_maroc.json`
- `referentiel_competences_it.json`
- `entreprises_it_maroc.csv`

### Zone Bronze

La zone Bronze conserve les donnees brutes sans correction. Elle sert d'archive fidele des donnees recues.

- Format : JSON
- Partitionnement : source et mois
- Exemple : `data_lake/bronze/rekrute/2024_01/offres_raw.json`

### Zone Silver

La zone Silver contient les donnees nettoyees et standardisees. Les traitements portent sur les villes, les contrats, les profils, les salaires, les dates et les competences IT.

- Format : Parquet
- Sorties principales :
  - `data_lake/silver/offres_clean/offres_clean.parquet`
  - `data_lake/silver/competences_extraites/competences.parquet`

### Zone Gold

La zone Gold regroupe les tables analytiques pretes pour DuckDB, le notebook et le dashboard.

- Format : Parquet
- Sorties principales :
  - `top_competences.parquet`
  - `salaires_par_profil.parquet`
  - `offres_par_ville.parquet`
  - `entreprises_recruteurs.parquet`
  - `tendances_mensuelles.parquet`

## 3. Choix des formats

| Zone | Format | Justification |
|---|---|---|
| Bronze | JSON | Adapte aux donnees brutes et semi-structurees issues des offres d'emploi. |
| Silver | Parquet | Efficace pour stocker des donnees nettoyees, typees et relues par pandas. |
| Gold | Parquet | Rapide pour les requetes DuckDB, les aggregations et les visualisations. |

## 4. Exploitation analytique

Les tables Gold sont interrogees avec DuckDB afin de produire les analyses du marche IT marocain :

- top competences IT ;
- comparaison des opportunites par ville ;
- salaires medians par profil ;
- relation entre experience et salaire ;
- entreprises qui recrutent le plus.

Les resultats sont presentes dans le notebook analytique et dans le dashboard de synthese.
