from pathlib import Path
import pandas as pd


def construire_gold(data_lake_root: str):
    """
    Construit les tables Gold a partir des fichiers Silver.
    Les tables Gold sont des agregations pretes pour DuckDB,
    le notebook, les graphiques et le rapport final.
    """

    root = Path(data_lake_root)

    offres_path = root / "silver" / "offres_clean" / "offres_clean.parquet"
    competences_path = root / "silver" / "competences_extraites" / "competences.parquet"
    gold_path = root / "gold"
    gold_path.mkdir(parents=True, exist_ok=True)

    df_offres = pd.read_parquet(offres_path)
    df_competences = pd.read_parquet(competences_path)

    # 1. Top competences
    top_competences = (
        df_competences[df_competences["competence"] != "non_detecte"]
        .groupby(["competence", "famille"])
        .agg(
            nb_offres=("id_offre", "nunique")
        )
        .reset_index()
        .sort_values("nb_offres", ascending=False)
    )

    # 2. Salaires par profil
    salaires_par_profil = (
        df_offres[df_offres["salaire_connu"] == True]
        .groupby("profil_normalise")
        .agg(
            nb_offres=("id_offre", "nunique"),
            salaire_min=("salaire_median_mad", "min"),
            salaire_median=("salaire_median_mad", "median"),
            salaire_moyen=("salaire_median_mad", "mean"),
            salaire_max=("salaire_median_mad", "max")
        )
        .reset_index()
        .sort_values("salaire_median", ascending=False)
    )

    # 3. Offres par ville
    offres_par_ville = (
        df_offres
        .groupby(["ville_std", "region_admin"])
        .agg(
            nb_offres=("id_offre", "nunique"),
            nb_profils=("profil_normalise", "nunique")
        )
        .reset_index()
        .sort_values("nb_offres", ascending=False)
    )

    # 4. Entreprises recruteurs
    entreprises_recruteurs = (
        df_offres
        .groupby("entreprise")
        .agg(
            nb_offres=("id_offre", "nunique"),
            nb_villes=("ville_std", "nunique"),
            nb_profils=("profil_normalise", "nunique")
        )
        .reset_index()
        .sort_values("nb_offres", ascending=False)
    )

    # 5. Tendances mensuelles
    tendances_mensuelles = (
        df_offres
        .groupby(["annee", "mois", "profil_normalise"])
        .agg(
            nb_offres=("id_offre", "nunique")
        )
        .reset_index()
        .sort_values(["annee", "mois"])
    )

    top_competences.to_parquet(gold_path / "top_competences.parquet", index=False)
    salaires_par_profil.to_parquet(gold_path / "salaires_par_profil.parquet", index=False)
    offres_par_ville.to_parquet(gold_path / "offres_par_ville.parquet", index=False)
    entreprises_recruteurs.to_parquet(gold_path / "entreprises_recruteurs.parquet", index=False)
    tendances_mensuelles.to_parquet(gold_path / "tendances_mensuelles.parquet", index=False)

    print("[GOLD] Tables Gold generees avec succes")
    print(f"[GOLD] {len(top_competences)} competences agregees")
    print(f"[GOLD] {len(salaires_par_profil)} profils avec salaires")
    print(f"[GOLD] {len(offres_par_ville)} villes analysees")
    print(f"[GOLD] {len(entreprises_recruteurs)} entreprises analysees")
    print(f"[GOLD] {len(tendances_mensuelles)} lignes de tendances mensuelles")