# Mexora RH Intelligence - Data Lake RH

## Objectif du projet

Ce projet construit un Data Lake pour analyser le marche de l'emploi IT au Maroc.

Le cas d'usage est celui de Mexora, une entreprise qui souhaite recruter des profils data et IT. Le projet aide la direction RH a comprendre :

- les competences IT les plus demandees ;
- les profils les plus recherches ;
- les salaires medians par profil ;
- les villes les plus dynamiques ;
- les entreprises concurrentes sur le marche du talent.

Le pipeline suit une architecture Data Lake en trois zones :

```text
Bronze -> Silver -> Gold
```

## Structure du projet

```text
Data-Lake-Analyse-/
|-- pipeline/
|   |-- __init__.py
|   |-- bronze_ingestion.py
|   |-- silver_transform.py
|   |-- silver_nlp.py
|   |-- gold_aggregation.py
|   `-- utils.py
|-- analysis/
|   `-- analyse_marche.py
|-- notebooks/
|   `-- analyse_marche_it_maroc.ipynb
|-- data/
|   `-- raw/
|       |-- offres_emploi_it_maroc.json
|       |-- referentiel_competences_it.json
|       `-- entreprises_it_maroc.csv
|-- data_lake/
|   |-- bronze/
|   |-- silver/
|   `-- gold/
|-- docs/
|   |-- conception_architecture.md
|   |-- conception_architecture.pdf
|   |-- rapport_pipeline.md
|   `-- schema_architecture.png
|-- rapports/
|   |-- rapport_pipeline.md
|   |-- rapport_pipeline.pdf
|   |-- dashboard_synthese.md
|   |-- dashboard_synthese.pdf
|   |-- dashboard_top_competences.png
|   |-- dashboard_villes.png
|   |-- dashboard_salaires.png
|   `-- dashboard_tendances.png
|-- main.py
|-- requirements.txt
|-- README.md
`-- .gitignore
```

Note : le dossier `data_lake/` est genere localement par le pipeline et n'est pas versionne dans Git.

## Architecture du pipeline

```text
Donnees sources
    -> Bronze : donnees brutes conservees en JSON
    -> Silver : donnees nettoyees et standardisees en Parquet
    -> Gold : tables analytiques agregees en Parquet
    -> DuckDB, notebook, dashboard et rapports
```

## Zones du Data Lake

### Bronze

La zone Bronze conserve les donnees brutes sans modification.

- Format : JSON
- Partitionnement : `source / mois`
- Exemple : `data_lake/bronze/rekrute/2024_01/offres_raw.json`

### Silver

La zone Silver contient les donnees nettoyees et standardisees.

Fichiers generes :

```text
data_lake/silver/offres_clean/offres_clean.parquet
data_lake/silver/competences_extraites/competences.parquet
```

Transformations principales :

- normalisation des villes ;
- normalisation des contrats ;
- standardisation des profils IT ;
- conversion des salaires en MAD ;
- preparation des dates ;
- extraction des competences IT.

### Gold

La zone Gold contient les tables analytiques finales utilisees par DuckDB, le notebook et le dashboard.

Fichiers generes :

```text
data_lake/gold/top_competences.parquet
data_lake/gold/salaires_par_profil.parquet
data_lake/gold/offres_par_ville.parquet
data_lake/gold/entreprises_recruteurs.parquet
data_lake/gold/tendances_mensuelles.parquet
```

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/imane-aithamou/Data-Lake-Analyse-.git
cd Data-Lake-Analyse-
```

### 2. Creer un environnement virtuel

Sous Windows PowerShell :

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Installer les dependances

```powershell
pip install -r requirements.txt
```

## Lancer le pipeline complet

Verifier que les trois fichiers sources sont presents dans `data/raw/` :

```text
data/raw/offres_emploi_it_maroc.json
data/raw/referentiel_competences_it.json
data/raw/entreprises_it_maroc.csv
```

Commande :

```powershell
python main.py
```

Le pipeline execute :

```text
1. Ingestion Bronze
2. Chargement depuis Bronze
3. Transformations Silver
4. Extraction des competences IT
5. Sauvegarde Silver en Parquet
6. Construction des tables Gold
```

## Analyse DuckDB

Commande :

```powershell
python analysis/analyse_marche.py
```

Cette analyse repond aux questions suivantes :

- Quelles competences sont les plus demandees ?
- Tanger, Casablanca et Rabat : ou se trouvent les opportunites IT ?
- Quel est le salaire median par profil ?
- Existe-t-il une relation entre experience et salaire ?
- Quelles entreprises recrutent le plus ?

## Notebook analytique

Fichier :

```text
notebooks/analyse_marche_it_maroc.ipynb
```

Le notebook contient les requetes DuckDB, les resultats, les visualisations et les interpretations.

## Livrables principaux

```text
docs/conception_architecture.md
docs/conception_architecture.pdf
docs/schema_architecture.png
rapports/rapport_pipeline.md
rapports/rapport_pipeline.pdf
notebooks/analyse_marche_it_maroc.ipynb
rapports/dashboard_synthese.pdf
```

## Etat du projet

Fonctionnalites implementees :

- ingestion Bronze des donnees JSON ;
- nettoyage et standardisation Silver ;
- extraction des competences IT ;
- construction de la zone Gold ;
- analyses DuckDB du marche IT marocain ;
- notebook analytique avec visualisations ;
- dashboard de synthese exporte en PDF ;
- documentation du pipeline et de l'architecture.

Le projet fournit une chaine complete de traitement pour transformer des offres d'emploi IT brutes en indicateurs RH exploitables pour Mexora.
