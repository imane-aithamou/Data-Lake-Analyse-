from pipeline.bronze_ingestion import ingerer_bronze
from pipeline.silver_transform import (
    charger_depuis_bronze,
    normaliser_villes,
    normaliser_types_contrat,
    nettoyer_titres_postes,
    normaliser_salaires,
    normaliser_experience,
    normaliser_dates,
)


DATA_LAKE_ROOT = "data_lake"
SOURCE_OFFRES = "data/raw/offres_emploi_it_maroc.json"


def main():
    ingerer_bronze(SOURCE_OFFRES, DATA_LAKE_ROOT)

    df = charger_depuis_bronze(DATA_LAKE_ROOT)

    df = normaliser_villes(df)
    df = normaliser_types_contrat(df)
    df = nettoyer_titres_postes(df)
    df = normaliser_salaires(df)
    df = normaliser_experience(df)
    df = normaliser_dates(df)

    print(df[[
        "id_offre",
        "ville",
        "ville_std",
        "type_contrat",
        "type_contrat_std",
        "titre_poste",
        "profil_normalise",
        "salaire_brut",
        "salaire_median_mad",
        "experience_requise",
        "experience_min_ans",
        "annee",
        "mois",
        "date_valide"
    ]])


if __name__ == "__main__":
    main()