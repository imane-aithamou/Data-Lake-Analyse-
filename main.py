from pipeline.bronze_ingestion import ingerer_bronze


DATA_LAKE_ROOT = "data_lake"
SOURCE_OFFRES = "data/raw/offres_emploi_it_maroc.json"


def main():
    stats = ingerer_bronze(SOURCE_OFFRES, DATA_LAKE_ROOT)
    print(stats)


if __name__ == "__main__":
    main()