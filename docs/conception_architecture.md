# Conception de l’architecture Data Lake - Mexora RH Intelligence

## 1. Objectif du Data Lake

Le projet Mexora RH Intelligence a pour objectif de construire un Data Lake permettant d’analyser le marché de l’emploi IT au Maroc. Les données utilisées proviennent d’offres d’emploi collectées depuis plusieurs sources comme Rekrute, MarocAnnonce et LinkedIn Maroc.

Le Data Lake est organisé en trois zones principales :

- Bronze : conservation des données brutes.
- Silver : nettoyage, standardisation et structuration des données.
- Gold : création de tables analytiques prêtes pour les requêtes DuckDB, le dashboard et le rapport final.

Cette architecture permet de garder une trace fidèle des données originales tout en produisant progressivement des données fiables pour l’analyse RH.

---

## 2. Justification des formats de stockage

| Zone | Format choisi | Pourquoi ce format ? | Pourquoi pas les autres ? |
|---|---|---|---|
| Bronze | JSON | Le JSON permet de conserver les données brutes telles qu’elles ont été collectées par scraping. Il accepte les données semi-structurées et garde la structure originale des offres. | Le CSV est moins adapté aux champs complexes comme les listes de langues ou les longues descriptions. Le Parquet impose une structure plus claire, ce qui n’est pas idéal pour une zone brute. |
| Silver | Parquet | Le Parquet est adapté aux données nettoyées et typées. Il est compressé, rapide à lire et efficace avec pandas, pyarrow et DuckDB. | Le JSON devient moins performant pour les traitements analytiques. Le CSV ne conserve pas bien les types de données et devient moins fiable pour les colonnes numériques ou dates. |
| Gold | Parquet | Les tables Gold sont utilisées pour l’analyse. Le Parquet permet des requêtes rapides avec DuckDB et réduit la taille des fichiers. | Le JSON et le CSV sont moins performants pour les agrégations, les filtres et les analyses répétées. |

---

## 3. Rôle de chaque zone

### Zone Bronze

La zone Bronze contient les données brutes, sans modification. Elle sert d’archive fidèle de ce qui a été reçu depuis les sources d’emploi.

Exemple de contenu :

```text
data_lake/bronze/rekrute/2024_01/offres_raw.json
data_lake/bronze/linkedin/2024_02/offres_raw.json
data_lake/bronze/marocannonce/2024_03/offres_raw.json