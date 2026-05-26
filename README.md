# Mexora RH Intelligence - Data Lake RH

## Objectif du projet

Ce projet consiste a construire un Data Lake pour analyser le marche de l'emploi IT au Maroc.

Le cas d'usage est celui de Mexora, une entreprise qui souhaite recruter de nouveaux profils data. Le but est d'aider la direction RH a comprendre :

- les competences IT les plus demandees ;
- les profils les plus recherches ;
- les salaires medians par profil et par ville ;
- les villes les plus dynamiques ;
- les entreprises concurrentes sur le marche du talent.

Le projet suit une architecture Data Lake en trois zones :

```text
Bronze -> Silver -> Gold
```

---

## Structure du projet

```text
mexora_rh_lake/
|-- pipeline/
|   |-- __init__.py
|   |-- bronze_ingestion.py
|   |-- silver_transform.py
|   |-- silver_nlp.py
|   `-- utils.py
|-- analysis/
|   `-- analyse_marche.py
|-- notebooks/
|   `-- analyse_marche_it_maroc.ipynb
|-- data/
|   |-- raw/
|   |   |-- offres_emploi_it_maroc.json
|   |   |-- referentiel_competences_it.json
|   |   `-- entreprises_it_maroc.csv
|   `-- generated/
|-- data_lake/
|   |-- bronze/
|   |-- silver/
|   `-- gold/
|-- docs/
|   |-- conception_architecture.md
|   |-- rapport_pipeline.md
|   `-- schema_architecture.png
|-- reports/
|   `-- rapport_final.md
|-- main.py
|-- requirements.txt
|-- README.md
`-- .gitignore
```

---

## Architecture du pipeline

```text
Raw data
   ↓
Bronze (JSON brut)
   ↓
Silver (nettoyage + NLP)
   ↓
Gold (agregations analytiques)
   ↓
DuckDB + Notebook + Dashboard
```
---

## Zones du Data Lake

### Zone Bronze

La zone Bronze contient les donnees brutes, sans modification.

Format utilise :

```text
JSON
```

Partitionnement :

```text
source / mois
```

Exemple :

```text
data_lake/bronze/rekrute/2024_01/offres_raw.json
```

### Zone Silver

La zone Silver contient les donnees nettoyees et standardisees.

Format utilise :

```text
Parquet
```

Fichiers generes :

```text
data_lake/silver/offres_clean/offres_clean.parquet
data_lake/silver/competences_extraites/competences.parquet
```

### Zone Gold

La zone Gold contient les tables analytiques finales utilisées pour les requêtes DuckDB, les visualisations, le notebook d’analyse ainsi que les recommandations du rapport final.

Format utilise :

```text
Parquet
```

Fichiers generes :

```text
data_lake/gold/top_competences.parquet
data_lake/gold/salaires_par_profil.parquet
data_lake/gold/offres_par_ville.parquet
data_lake/gold/entreprises_recruteurs.parquet
data_lake/gold/tendances_mensuelles.parquet
```

Objectif :

```text
Transformer les donnees Silver en indicateurs analytiques prets a etre exploites
```
---

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/USERNAME/mexora_rh_lake.git
cd mexora_rh_lake
```

Remplacer `USERNAME` par le nom d'utilisateur GitHub du binome.

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

---

## Lancer le pipeline complet (Bronze → Silver → Gold)

Avant de lancer le pipeline, verifier que les fichiers sources sont presents dans :

```text
data/raw/
```

Fichiers attendus :

```text
data/raw/offres_emploi_it_maroc.json
data/raw/referentiel_competences_it.json
data/raw/entreprises_it_maroc.csv
```

Commande de lancement :

```powershell
python main.py
```

Le pipeline execute :

```text
1. Ingestion des donnees brutes dans Bronze
2. Chargement des donnees depuis Bronze
3. Nettoyage et standardisation Silver
4. Extraction des competences IT (NLP basique)
5. Sauvegarde des fichiers Silver en Parquet
6. Construction des tables Gold
7. Preparation des donnees analytiques pour DuckDB et notebook
```

---

## Fichiers generes

Apres execution de :

```powershell
python main.py
```

les zones Bronze, Silver et Gold sont generees automatiquement.

### Zone Bronze

```text
data_lake/bronze/...
```

### Zone Silver

```text
data_lake/silver/offres_clean/offres_clean.parquet
data_lake/silver/competences_extraites/competences.parquet
```

### Zone Gold

```text
data_lake/gold/top_competences.parquet
data_lake/gold/salaires_par_profil.parquet
data_lake/gold/offres_par_ville.parquet
data_lake/gold/entreprises_recruteurs.parquet
data_lake/gold/tendances_mensuelles.parquet
```

Ces fichiers sont générés localement et peuvent être reconstruits à tout moment en relançant :

```powershell
python main.py
```

---

## Colonnes importantes dans Silver

### Table offres propres

Fichier :

```text
data_lake/silver/offres_clean/offres_clean.parquet
```

Colonnes importantes :

```text
id_offre
source
titre_poste
profil_normalise
ville
ville_std
region_admin
type_contrat
type_contrat_std
salaire_brut
salaire_min_mad
salaire_max_mad
salaire_median_mad
salaire_connu
experience_requise
experience_min_ans
experience_max_ans
date_publication
date_expiration
date_publication_clean
date_expiration_clean
annee
mois
date_valide
```

### Table competences extraites

Fichier :

```text
data_lake/silver/competences_extraites/competences.parquet
```

Colonnes importantes :

```text
id_offre
profil
ville
competence
famille
date_pub
annee
mois
```

---

## Documentation

Documents disponibles :

```text
docs/conception_architecture.md
docs/rapport_pipeline.md
```

Le fichier `docs/conception_architecture.md` explique l'architecture Bronze / Silver / Gold.

Le fichier `docs/rapport_pipeline.md` documente les traitements realises dans le pipeline.

---

## Analyse DuckDB et notebook

### Executer les analyses DuckDB

Commande :

```powershell
python analysis/analyse_marche.py
```

Cette analyse permet de répondre aux questions stratégiques suivantes :

- Quelles competences sont les plus demandees ?
- Tanger vs Casablanca vs Rabat : ou se trouvent les opportunites IT ?
- Quel est le salaire median par profil ?
- Existe-t-il une relation entre experience et salaire ?
- Quelles entreprises recrutent le plus ?

### Notebook analytique

Fichier :

```text
notebooks/analyse_marche_it_maroc.ipynb
```

Le notebook contient :

```text
- les requetes DuckDB
- les tableaux de resultats
- les visualisations matplotlib
- les interpretations textuelles
- un dashboard analytique de synthese
```

## Travail en binome

Repartition conseillee :

### Partie pipeline Bronze / Silver

Branche :

```text
feature/pipeline-silver
```

Fichiers principaux :

```text
pipeline/
main.py
docs/rapport_pipeline.md
README.md
```

### Partie Gold / Analyse / Rapport final

Branche :

```text
feature/gold-analysis-report
```

Fichiers principaux :

```text
analysis/
notebooks/
reports/
data_lake/gold/
```

Pour eviter les conflits Git, il est conseille de ne pas modifier en meme temps les fichiers communs comme :

```text
README.md
docs/rapport_pipeline.md
main.py
```

---

## Etat du projet

Fonctionnalites implementees :

```text
Ingestion Bronze des donnees JSON
Nettoyage et standardisation Silver
Extraction des competences IT (NLP basique)
Construction de la zone Gold
Analyses DuckDB du marche IT marocain
Notebook analytique avec visualisations
Dashboard de synthese integre au notebook
Documentation complete du pipeline
```

Le projet fournit une chaine complete de traitement permettant de transformer des offres d’emploi IT brutes en indicateurs analytiques exploitables pour accompagner la strategie RH de Mexora.
