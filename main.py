from pipeline.bronze_ingestion import ingerer_bronze
from pipeline.silver_transform import charger_depuis_bronze


DATA_LAKE_ROOT = "data_lake"
SOURCE_OFFRES = "data/raw/offres_emploi_it_maroc.json"


def main():
    ingerer_bronze(SOURCE_OFFRES, DATA_LAKE_ROOT)

    df = charger_depuis_bronze(DATA_LAKE_ROOT)

    print(df.head())
    print(df.columns.tolist())


if __name__ == "__main__":
    main()