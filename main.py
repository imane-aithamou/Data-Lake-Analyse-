from pipeline.gold_aggregation import construire_gold
from pipeline.bronze_ingestion import ingerer_bronze
from pipeline.silver_transform import (
    charger_depuis_bronze,
    normaliser_villes,
    normaliser_types_contrat,
    nettoyer_titres_postes,
    normaliser_salaires,
    normaliser_experience,
    normaliser_dates,
    sauvegarder_silver,
)
from pipeline.silver_nlp import extraire_competences


DATA_LAKE_ROOT = "data_lake"
SOURCE_OFFRES = "data/raw/offres_emploi_it_maroc.json"
REFERENTIEL_COMPETENCES = "data/raw/referentiel_competences_it.json"


def main():
    ingerer_bronze(SOURCE_OFFRES, DATA_LAKE_ROOT)

    df = charger_depuis_bronze(DATA_LAKE_ROOT)

    df = normaliser_villes(df)
    df = normaliser_types_contrat(df)
    df = nettoyer_titres_postes(df)
    df = normaliser_salaires(df)
    df = normaliser_experience(df)
    df = normaliser_dates(df)

    df_competences = extraire_competences(df, REFERENTIEL_COMPETENCES)

    sauvegarder_silver(df, df_competences, DATA_LAKE_ROOT)


if __name__ == "__main__":
    main()

construire_gold(DATA_LAKE_ROOT)