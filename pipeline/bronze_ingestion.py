from datetime import datetime
from pathlib import Path

from pipeline.utils import load_json, save_json, safe_get_month, normalize_source


def ingerer_bronze(filepath_source: str, data_lake_root: str) -> dict:
    """
    Charge les donnees brutes dans la zone Bronze sans modification.
    Les offres sont partitionnees par source et par mois de publication.

    Exemple de sortie :
    data_lake/bronze/rekrute/2024_01/offres_raw.json
    """

    data = load_json(filepath_source)
    offres = data.get("offres", [])

    stats = {
        "total": len(offres),
        "par_source": {},
        "par_mois": {},
        "nb_partitions": 0
    }

    partitions = {}

    for offre in offres:
        source = normalize_source(offre.get("source", "inconnu"))
        mois_partition = safe_get_month(offre.get("date_publication"))

        cle_partition = f"{source}/{mois_partition}"

        if cle_partition not in partitions:
            partitions[cle_partition] = []

        partitions[cle_partition].append(offre)

        stats["par_source"][source] = stats["par_source"].get(source, 0) + 1
        stats["par_mois"][mois_partition] = stats["par_mois"].get(mois_partition, 0) + 1

    for partition, offres_partition in partitions.items():
        chemin_fichier = (
            Path(data_lake_root)
            / "bronze"
            / partition
            / "offres_raw.json"
        )

        contenu = {
            "metadata": {
                "source_fichier": filepath_source,
                "date_ingestion": datetime.now().isoformat(timespec="seconds"),
                "partition": partition,
                "nb_offres": len(offres_partition)
            },
            "offres": offres_partition
        }

        save_json(contenu, chemin_fichier)

    stats["nb_partitions"] = len(partitions)

    print(
        f"[BRONZE] {stats['total']} offres ingerees "
        f"dans {stats['nb_partitions']} partitions"
    )

    return stats