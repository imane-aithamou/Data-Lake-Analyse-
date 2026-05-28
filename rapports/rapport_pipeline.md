# Rapport pipeline - Mexora RH Intelligence

## 1. Objectif du pipeline

Ce document presente les traitements realises dans le pipeline Data Lake du projet Mexora RH Intelligence.

L'objectif du pipeline est de transformer des offres d'emploi IT marocaines brutes en donnees propres et exploitables pour l'analyse du marche de l'emploi IT au Maroc.

Le pipeline suit l'architecture suivante :

```text
Donnees sources
    -> Zone Bronze : donnees brutes conservees en JSON
    -> Zone Silver : donnees nettoyees et standardisees en Parquet
    -> Zone Gold : tables analytiques pour DuckDB et le rapport final
```

Ma partie concerne principalement :

- l'ingestion Bronze ;
- le chargement depuis Bronze ;
- le nettoyage Silver ;
- l'extraction des competences IT ;
- la sauvegarde des donnees Silver au format Parquet.

Les parties Gold, analyse DuckDB, visualisations et recommandations seront completees par la suite.

---

## 2. Donnees sources utilisees

Les fichiers sources sont places dans le dossier :

```text
data/raw/
```

Fichiers utilises :

```text
data/raw/offres_emploi_it_maroc.json
data/raw/referentiel_competences_it.json
data/raw/entreprises_it_maroc.csv
```

Le fichier principal `offres_emploi_it_maroc.json` contient les offres d'emploi IT avec des champs comme :

- `id_offre`
- `source`
- `titre_poste`
- `description`
- `competences_brut`
- `entreprise`
- `ville`
- `type_contrat`
- `experience_requise`
- `salaire_brut`
- `date_publication`
- `date_expiration`

Les donnees contiennent volontairement des imperfections afin de simuler des donnees issues du scraping :

- villes ecrites sous plusieurs formes : `casa`, `CASABLANCA`, `Casablanca` ;
- salaires sous plusieurs formats : `15000-20000 MAD`, `15K-20K`, `Selon profil`, `Confidentiel`, `2000 EUR` ;
- types de contrat non standardises : `CDI`, `cdi`, `Permanent`, `Contrat a duree indeterminee` ;
- experiences sous plusieurs formats : `3-5 ans`, `min 3 ans`, `Debutant accepte`, `Senior 7+ ans` ;
- competences melangees entre le champ `competences_brut` et la description.

---

## 3. Ingestion Bronze

### Fichier concerne

```text
pipeline/bronze_ingestion.py
```

### Fonction principale

```text
ingerer_bronze(filepath_source, data_lake_root)
```

### Objectif

L'objectif de cette etape est de charger les donnees brutes dans la zone Bronze sans les modifier.

La zone Bronze sert d'archive fidele des donnees recues. Aucune correction n'est appliquee a cette etape.

### Regles appliquees

Pour chaque offre :

1. lire la source de l'offre ;
2. lire la date de publication ;
3. extraire le mois au format `YYYY_MM` ;
4. creer une partition par `source/mois` ;
5. sauvegarder les offres dans un fichier `offres_raw.json`.

Exemple de structure generee :

```text
data_lake/bronze/rekrute/2024_01/offres_raw.json
data_lake/bronze/linkedin/2024_02/offres_raw.json
data_lake/bronze/marocannonce/2024_03/offres_raw.json
```

### Metadonnees ajoutees

Chaque fichier Bronze contient une section `metadata` avec :

- le fichier source ;
- la date d'ingestion ;
- la partition ;
- le nombre d'offres dans la partition.

### Resultat obtenu sur le jeu de test

```text
6 offres ingerees dans 6 partitions
```

Repartition observee :

```text
rekrute : 2 offres
linkedin : 2 offres
marocannonce : 2 offres
```

### Points d'attention

- Les donnees Bronze ne doivent pas etre modifiees.
- Si une date est invalide, la partition utilisee est `date_inconnue`.
- La zone Bronze n'est pas versionnee dans Git car elle peut etre regeneree.

---

## 4. Chargement depuis Bronze

### Fichier concerne

```text
pipeline/silver_transform.py
```

### Fonction principale

```text
charger_depuis_bronze(data_lake_root)
```

### Objectif

Cette etape lit tous les fichiers Bronze et les regroupe dans un seul tableau pandas afin de commencer les transformations Silver.

### Regles appliquees

Le pipeline parcourt tous les fichiers :

```text
data_lake/bronze/**/offres_raw.json
```

Puis il :

1. lit chaque fichier JSON ;
2. extrait la liste des offres ;
3. fusionne les offres dans un seul DataFrame ;
4. supprime les doublons avec la colonne `id_offre`.

### Resultat attendu

Sur le jeu de test :

```text
6 offres chargees depuis Bronze
0 doublons supprimes
```

### Points d'attention

- La colonne `id_offre` est essentielle pour detecter les doublons.
- Les donnees originales ne sont pas encore nettoyees a cette etape.

---

## 5. Transformations Silver

### Fichier concerne

```text
pipeline/silver_transform.py
```

### Objectif

La zone Silver contient des donnees nettoyees, standardisees et exploitables pour les analyses.

Les colonnes originales sont conservees quand elles sont utiles, et de nouvelles colonnes standardisees sont ajoutees.

---

### 5.1 Normalisation des villes

### Fonction

```text
normaliser_villes(df)
```

### Regles appliquees

Une nouvelle colonne `ville_std` est creee.

Exemples :

```text
casa -> Casablanca
CASABLANCA -> Casablanca
Casablanca -> Casablanca
rabat -> Rabat
RABAT -> Rabat
tanger -> Tanger
```

Une colonne `region_admin` est aussi ajoutee.

Exemples :

```text
Casablanca -> Casablanca-Settat
Rabat -> Rabat-Sale-Kenitra
Tanger -> Tanger-Tetouan-Al Hoceima
```

### Colonnes ajoutees

```text
ville_source
ville_std
region_admin
```

### Point d'attention

La colonne originale `ville` est conservee pour garder la trace de la donnee source.

---

### 5.2 Normalisation des types de contrat

### Fonction

```text
normaliser_types_contrat(df)
```

### Regles appliquees

Une nouvelle colonne `type_contrat_std` est creee.

Exemples :

```text
CDI -> CDI
cdi -> CDI
Permanent -> CDI
Contrat a duree indeterminee -> CDI
Freelance -> Freelance
CDD -> CDD
Stage -> Stage
```

### Colonne ajoutee

```text
type_contrat_std
```

### Point d'attention

Les valeurs non reconnues sont classees dans `Autre`.

---

### 5.3 Normalisation des titres de poste

### Fonction

```text
nettoyer_titres_postes(df)
```

### Objectif

Standardiser les intitules de poste en familles de profils IT.

### Regles appliquees

Une colonne `profil_normalise` est creee a partir du champ `titre_poste`.

Exemples :

```text
Data Engineer Junior -> Data Engineer
Ingenieur Big Data -> Data Engineer
Data Analyst Power BI -> Data Analyst
BI Analyst -> Data Analyst
Data Scientist NLP -> Data Scientist
Developpeur Full Stack React Node.js -> Developpeur Full Stack
```

### Colonnes ajoutees

```text
profil_source
profil_normalise
```

### Point d'attention

Les titres non reconnus sont classes dans `Autre IT`.

---

### 5.4 Normalisation des salaires

### Fonction

```text
normaliser_salaires(df)
```

### Objectif

Transformer les salaires textuels en valeurs numeriques en MAD mensuel brut.

### Regles appliquees

Exemples :

```text
12000-16000 MAD -> min 12000, max 16000, median 14000
15K-20K -> min 15000, max 20000, median 17500
2000 EUR -> conversion en MAD avec 1 EUR = 10.8 MAD
Selon profil -> salaire inconnu
Confidentiel -> salaire inconnu
```

### Colonnes ajoutees

```text
salaire_min_mad
salaire_max_mad
salaire_connu
salaire_median_mad
```

### Points d'attention

- Les salaires en EUR sont convertis avec un taux fixe de `1 EUR = 10.8 MAD`.
- Les valeurs non exploitables sont marquees avec `salaire_connu = False`.
- Les salaires incoherents sont ignores.

---

### 5.5 Normalisation de l'experience

### Fonction

```text
normaliser_experience(df)
```

### Objectif

Transformer l'experience demandee en annees minimum et maximum.

### Regles appliquees

Exemples :

```text
1-2 ans -> min 1, max 2
3-5 ans -> min 3, max 5
min 3 ans -> min 3, max vide
Debutant accepte -> min 0, max 2
Senior 7+ ans -> min 7, max vide
```

### Colonnes ajoutees

```text
experience_min_ans
experience_max_ans
```

### Point d'attention

Les valeurs impossibles a interpreter restent vides afin de ne pas fausser les analyses.

---

### 5.6 Normalisation des dates

### Fonction

```text
normaliser_dates(df)
```

### Objectif

Convertir les dates textuelles en dates exploitables et ajouter des colonnes temporelles.

### Regles appliquees

Le pipeline convertit :

```text
date_publication
date_expiration
```

en :

```text
date_publication_clean
date_expiration_clean
```

Puis il ajoute :

```text
annee
mois
date_valide
```

La colonne `date_valide` vaut `False` si :

- une date est absente ;
- une date est invalide ;
- la date de publication est apres la date d'expiration.

---

## 6. Extraction des competences IT

### Fichier concerne

```text
pipeline/silver_nlp.py
```

### Fonction principale

```text
extraire_competences(df, referentiel_path)
```

### Objectif

Extraire les competences IT presentes dans les offres afin de produire une table structuree exploitable pour les analyses.

### Source utilisee

Le pipeline utilise le referentiel :

```text
data/raw/referentiel_competences_it.json
```

Ce fichier contient des familles de competences et leurs alias.

Exemple :

```text
python : python, python3, py
power_bi : power bi, powerbi, pbi
spark : spark, apache spark, pyspark
```

### Regles appliquees

Pour chaque offre :

1. concatener `competences_brut` et `description` ;
2. normaliser le texte ;
3. chercher les alias presents dans le referentiel ;
4. produire une ligne par competence detectee ;
5. ajouter `non_detecte` si aucune competence n'est trouvee.

### Colonnes produites

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

### Points d'attention

- Les alias sont tries du plus long au plus court pour eviter des detections incorrectes.
- Les alias tres courts sont ignores pour limiter les faux positifs.
- Une meme competence n'est ajoutee qu'une seule fois par offre.

---

## 7. Sauvegarde Silver

### Fichier concerne

```text
pipeline/silver_transform.py
```

### Fonction principale

```text
sauvegarder_silver(df_offres, df_competences, data_lake_root)
```

### Objectif

Sauvegarder les donnees nettoyees au format Parquet.

### Fichiers generes

```text
data_lake/silver/offres_clean/offres_clean.parquet
data_lake/silver/competences_extraites/competences.parquet
```

### Pourquoi Parquet ?

Le format Parquet est utilise car il est :

- compresse ;
- rapide a lire ;
- adapte aux traitements analytiques ;
- compatible avec pandas, pyarrow et DuckDB.

### Point d'attention

Les fichiers Parquet sont generes localement et ne sont pas obligatoirement versionnes dans GitHub, car ils peuvent etre reconstruits avec :

```text
python main.py
```

---

## 8. Execution du pipeline

### Fichier concerne

```text
main.py
```

### Ordre d'execution

Le fichier `main.py` execute les etapes dans cet ordre :

```text
1. Ingestion Bronze
2. Chargement depuis Bronze
3. Normalisation des villes
4. Normalisation des types de contrat
5. Normalisation des titres de poste
6. Normalisation des salaires
7. Normalisation de l'experience
8. Normalisation des dates
9. Extraction des competences
10. Sauvegarde Silver
```

### Commande de lancement

```text
python main.py
```

---

## 9. Sorties disponibles pour la suite du projet

Les fichiers Silver suivants sont fournis a la partie Gold et analyse :

```text
data_lake/silver/offres_clean/offres_clean.parquet
data_lake/silver/competences_extraites/competences.parquet
```

Ces fichiers seront utilises pour :

- calculer les top competences ;
- analyser les salaires par profil ;
- comparer les villes ;
- identifier les entreprises qui recrutent le plus ;
- construire les tendances mensuelles.

---

## 10. Construction de la zone Gold

### Fichier concerne

```text
pipeline/gold_aggregation.py
```

### Fonction principale

```text
construire_gold(data_lake_root)
```

### Objectif

La zone Gold contient des donnees analytiques agregées prêtes pour les requêtes DuckDB, les visualisations, le notebook d’analyse ainsi que les recommandations finales du projet.

Contrairement à la zone Silver qui conserve les données nettoyées à un niveau détaillé, la zone Gold produit des indicateurs synthétiques facilitant l’analyse du marché IT marocain.

### Sources utilisees

Les tables Gold sont construites à partir des fichiers Silver suivants :

```text
data_lake/silver/offres_clean/offres_clean.parquet
data_lake/silver/competences_extraites/competences.parquet
```

### Regles appliquees

Le pipeline réalise plusieurs agrégations analytiques :

1. calcul des compétences IT les plus demandées ;
2. calcul des salaires médians par profil ;
3. calcul du nombre d’offres par ville ;
4. identification des entreprises recrutant le plus ;
5. calcul des tendances mensuelles des profils IT.

### Fichiers generes

```text
data_lake/gold/top_competences.parquet
data_lake/gold/salaires_par_profil.parquet
data_lake/gold/offres_par_ville.parquet
data_lake/gold/entreprises_recruteurs.parquet
data_lake/gold/tendances_mensuelles.parquet
```

### Pourquoi Parquet ?

Le format Parquet est utilisé dans la zone Gold car il permet :

- une lecture rapide avec DuckDB ;
- une meilleure compression des données ;
- une exécution efficace des agrégations ;
- une compatibilité avec pandas, matplotlib et les notebooks analytiques.

### Point d'attention

Les tables Gold ne remplacent pas les données Silver. Elles représentent une version analytique simplifiée construite à partir des données nettoyées afin de répondre aux besoins décisionnels de Mexora.

---

## 11. Analyse DuckDB

### Fichier concerne

```text
analysis/analyse_marche.py
```

### Objectif

DuckDB est utilisé afin d’exécuter des requêtes analytiques directement sur les fichiers Parquet sans utiliser une base de données relationnelle classique.

Cette approche permet d’analyser rapidement le marché de l’emploi IT marocain à partir des données produites dans le Data Lake.

### Questions analytiques traitees

Les analyses réalisées répondent aux cinq questions stratégiques définies dans le cahier des charges du projet.

---

### 11.1 Quelles competences sont les plus demandees ?

Cette analyse mesure les compétences apparaissant le plus fréquemment dans les offres IT.

Objectif :

```text
Identifier les technologies prioritaires du marche IT marocain
```

Exemples de compétences observées :

```text
Python
SQL
Spark
Power BI
Docker
```

Cette analyse permet d’identifier les compétences techniques devant être priorisées dans les futurs recrutements de Mexora.

---

### 11.2 Tanger vs Casablanca vs Rabat : ou se trouvent les opportunites IT ?

Cette analyse compare le volume d’offres d’emploi entre les principales villes IT marocaines.

Objectif :

```text
Comparer les bassins d'emploi technologique
```

Cette question est particulièrement stratégique pour Mexora basée à Tanger, car elle permet d’évaluer si certains profils devront être recrutés localement ou à distance depuis d’autres villes.

---

### 11.3 Quel est le salaire median par profil IT ?

Cette analyse mesure les niveaux de rémunération observés selon les profils IT.

Objectif :

```text
Positionner les futurs packages salariaux de Mexora
```

Les salaires médians observés permettent d’estimer des niveaux de rémunération cohérents avec le marché afin de rester compétitif dans le recrutement.

---

### 11.4 Existe-t-il une relation entre experience et salaire ?

Une corrélation de Pearson est calculée entre :

```text
experience_min_ans
salaire_median_mad
```

Objectif :

```text
Mesurer l'impact de l'experience sur les niveaux de remuneration
```

Cette analyse permet de vérifier si une augmentation du niveau d’expérience demandé tend à être associée à des salaires plus élevés.

---

### 11.5 Quelles entreprises recrutent le plus ?

Cette analyse identifie les entreprises publiant le plus d’offres IT.

Objectif :

```text
Identifier les concurrents de Mexora sur le marche du talent
```

Les entreprises les plus actives en recrutement représentent une concurrence potentielle sur les profils data et IT.

---

## 12. Visualisations et dashboard

### Fichier concerne

```text
notebooks/analyse_marche_it_maroc.ipynb
```

### Objectif

Le notebook contient un dashboard analytique synthétisant les principaux résultats du marché IT marocain.

### Visualisations realisees

#### 12.1 Top competences IT

Graphique horizontal présentant les compétences les plus demandées dans les offres IT.

Objectif :

```text
Identifier les technologies prioritaires du marche
```

#### 12.2 Comparaison Tanger / Casablanca / Rabat

Graphique comparatif du volume d’offres selon les villes.

Objectif :

```text
Comparer les opportunites IT selon les bassins d'emploi
```

#### 12.3 Salaires mediens par profil

Graphique montrant les rémunérations médianes selon les profils IT.

Objectif :

```text
Comparer les niveaux de salaire du marche
```

#### 12.4 Evolution mensuelle des profils data

Courbe temporelle représentant les profils :

```text
Data Engineer
Data Analyst
Data Scientist
```

Objectif :

```text
Identifier les tendances de recrutement dans le temps
```

### Point d'attention

Le dashboard est intégré directement au notebook d’analyse via matplotlib, conformément aux consignes du projet.

---

## 13. Limites du projet

Certaines limites doivent être prises en compte dans l’interprétation des résultats :

- le dataset reste issu du scraping et peut contenir du bruit ;
- certaines offres ne renseignent pas le salaire ;
- certaines compétences peuvent ne pas être détectées si elles ne figurent pas dans le référentiel ;
- le nombre d’offres peut varier selon les plateformes utilisées ;
- certaines informations manquantes peuvent limiter certaines analyses statistiques.

Malgré ces limites, les analyses produites permettent d’obtenir une vision cohérente du marché IT marocain.

---

## 14. Recommandations pour Mexora

À partir des résultats obtenus, plusieurs recommandations peuvent être formulées :

- cibler les compétences les plus demandées dans les futurs recrutements ;
- proposer des rémunérations cohérentes avec les médianes observées sur le marché ;
- renforcer le recrutement sur Casablanca et Rabat si certains profils sont rares localement ;
- anticiper les périodes de forte demande sur les profils data ;
- développer une stratégie attractive afin de concurrencer les entreprises les plus actives du marché du talent IT.