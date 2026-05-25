from pathlib import Path
import pandas as pd

from pipeline.utils import load_json


def charger_depuis_bronze(data_lake_root: str) -> pd.DataFrame:
    """
    Charge toutes les offres depuis la zone Bronze et les rassemble
    dans un seul tableau pandas.
    """

    bronze_path = Path(data_lake_root) / "bronze"
    all_offres = []

    for json_file in bronze_path.rglob("offres_raw.json"):
        data = load_json(json_file)
        offres = data.get("offres", [])
        all_offres.extend(offres)

    df = pd.DataFrame(all_offres)

    if "id_offre" in df.columns:
        nb_avant = len(df)
        df = df.drop_duplicates(subset=["id_offre"])
        nb_apres = len(df)
        nb_doublons = nb_avant - nb_apres
    else:
        nb_doublons = 0

    print(f"[SILVER] {len(df)} offres chargees depuis Bronze")
    print(f"[SILVER] {nb_doublons} doublons supprimes")

    return df