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

La zone Gold contient les tables analytiques finales.

Cette partie sera completee avec les agregations DuckDB et les analyses.

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

## Lancer le pipeline Bronze et Silver

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
4. Extraction des competences IT
5. Sauvegarde des fichiers Silver en Parquet
```

---

## Fichiers generes

Apres execution de `python main.py`, les fichiers suivants sont generes :

```text
data_lake/bronze/...
data_lake/silver/offres_clean/offres_clean.parquet
data_lake/silver/competences_extraites/competences.parquet
```

Ces fichiers sont generes localement. Ils peuvent ne pas etre versionnes dans GitHub afin d'eviter d'alourdir le repository.

Ils peuvent etre reconstruits a tout moment avec :

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

## Prochaines etapes

Parties a completer :

```text
Construction de la zone Gold
Requetes DuckDB
Notebook d'analyse
Visualisations
Rapport final pour le DRH
Dashboard de synthese
```
