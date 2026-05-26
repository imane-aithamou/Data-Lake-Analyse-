import duckdb

con = duckdb.connect()

OFFRES = "data_lake/silver/offres_clean/offres_clean.parquet"
COMPETENCES = "data_lake/silver/competences_extraites/competences.parquet"

print("\n1. Top compétences IT")
print(con.execute(f"""
SELECT competence, famille, COUNT(DISTINCT id_offre) AS nb_offres
FROM read_parquet('{COMPETENCES}')
WHERE competence <> 'non_detecte'
GROUP BY competence, famille
ORDER BY nb_offres DESC
LIMIT 15
""").df())

print("\n2. Tanger vs Casablanca vs Rabat")
print(con.execute(f"""
SELECT ville_std, profil_normalise, COUNT(DISTINCT id_offre) AS nb_offres
FROM read_parquet('{OFFRES}')
WHERE ville_std IN ('Tanger', 'Casablanca', 'Rabat')
GROUP BY ville_std, profil_normalise
ORDER BY ville_std, nb_offres DESC
""").df())

print("\n3. Salaire médian par profil")
print(con.execute(f"""
SELECT profil_normalise,
       COUNT(*) AS nb_offres_salaire,
       MEDIAN(salaire_median_mad) AS salaire_median_mad
FROM read_parquet('{OFFRES}')
WHERE salaire_connu = true
GROUP BY profil_normalise
ORDER BY salaire_median_mad DESC
""").df())

print("\n4. Corrélation expérience / salaire")
print(con.execute(f"""
SELECT CORR(experience_min_ans, salaire_median_mad) AS correlation_experience_salaire
FROM read_parquet('{OFFRES}')
WHERE salaire_connu = true
  AND experience_min_ans IS NOT NULL
  AND salaire_median_mad IS NOT NULL
""").df())

print("\n5. Entreprises qui recrutent le plus")
print(con.execute(f"""
SELECT entreprise,
       COUNT(DISTINCT id_offre) AS nb_offres,
       COUNT(DISTINCT ville_std) AS nb_villes,
       COUNT(DISTINCT profil_normalise) AS nb_profils
FROM read_parquet('{OFFRES}')
GROUP BY entreprise
ORDER BY nb_offres DESC
LIMIT 10
""").df())