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

import re
import pandas as pd

from pipeline.utils import normalize_text


def normaliser_villes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les villes et ajoute la region administrative.
    """

    mapping_villes = {
        "casablanca": "Casablanca",
        "casa": "Casablanca",
        "rabat": "Rabat",
        "tanger": "Tanger",
        "marrakech": "Marrakech",
        "fes": "Fes",
        "fès": "Fes"
    }

    mapping_regions = {
        "Casablanca": "Casablanca-Settat",
        "Rabat": "Rabat-Sale-Kenitra",
        "Tanger": "Tanger-Tetouan-Al Hoceima",
        "Marrakech": "Marrakech-Safi",
        "Fes": "Fes-Meknes"
    }

    df["ville_source"] = df["ville"]
    df["ville_std"] = df["ville"].apply(lambda x: mapping_villes.get(normalize_text(x), "Inconnue"))
    df["region_admin"] = df["ville_std"].apply(lambda x: mapping_regions.get(x, "Inconnue"))

    print("[SILVER] Villes normalisees")
    return df


def normaliser_types_contrat(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les types de contrat.
    """

    def parse_contrat(value):
        text = normalize_text(value)

        if text in ["cdi", "permanent", "contrat a duree indeterminee"]:
            return "CDI"
        if "freelance" in text or "independant" in text:
            return "Freelance"
        if text == "cdd" or "duree determinee" in text:
            return "CDD"
        if "stage" in text:
            return "Stage"

        return "Autre"

    df["type_contrat_std"] = df["type_contrat"].apply(parse_contrat)

    print("[SILVER] Types de contrat normalises")
    return df


def nettoyer_titres_postes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardise les titres de postes en profils IT.
    """

    mapping_profils = {
        r"data\s*eng|ingenieur\s+big\s+data|ingenieur\s+data|dev\s+data": "Data Engineer",
        r"data\s*analyst|analyste\s+data|bi\s+analyst|developpeur\s+bi|business\s+intelligence": "Data Analyst",
        r"data\s*scientist|machine\s*learning|ml\s*engineer|nlp": "Data Scientist",
        r"full\s*stack|fullstack": "Developpeur Full Stack",
        r"back[\s-]*end|backend": "Developpeur Backend",
        r"front[\s-]*end|frontend": "Developpeur Frontend",
        r"devops|sre": "DevOps / SRE",
        r"cloud": "Cloud Engineer",
        r"cyber|securite": "Cybersecurite",
        r"chef\s+de\s+projet|project\s+manager|scrum\s+master": "Chef de Projet IT"
    }

    df["profil_source"] = df["titre_poste"].apply(normalize_text)
    df["profil_normalise"] = "Autre IT"

    for pattern, profil in mapping_profils.items():
        masque = df["profil_source"].str.contains(pattern, regex=True, na=False)
        df.loc[masque, "profil_normalise"] = profil

    print("[SILVER] Titres de postes normalises")
    return df


def normaliser_salaires(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrait les salaires min, max et median en MAD.
    """

    taux_eur_mad = 10.8

    def parser_salaire(value):
        if pd.isna(value):
            return None, None, False

        text = normalize_text(value)

        if text in ["", "null", "confidentiel", "selon profil"]:
            return None, None, False

        est_eur = "eur" in text or "€" in text

        text = text.replace("mad", "")
        text = text.replace("dh", "")
        text = text.replace("eur", "")
        text = text.replace("€", "")
        text = text.replace(" ", "")

        text = re.sub(
            r"(\d+(?:\.\d+)?)k",
            lambda m: str(int(float(m.group(1)) * 1000)),
            text
        )

        nombres = re.findall(r"\d+(?:\.\d+)?", text)

        if not nombres:
            return None, None, False

        montants = [float(n) for n in nombres]

        if est_eur:
            montants = [m * taux_eur_mad for m in montants]

        if len(montants) >= 2:
            salaire_min = min(montants[:2])
            salaire_max = max(montants[:2])
        else:
            salaire_min = montants[0]
            salaire_max = montants[0]

        if salaire_min < 3000 or salaire_max > 100000:
            return None, None, False

        return salaire_min, salaire_max, True

    resultats = df["salaire_brut"].apply(
        lambda x: pd.Series(
            parser_salaire(x),
            index=["salaire_min_mad", "salaire_max_mad", "salaire_connu"]
        )
    )

    df = pd.concat([df, resultats], axis=1)
    df["salaire_median_mad"] = (df["salaire_min_mad"] + df["salaire_max_mad"]) / 2

    print("[SILVER] Salaires normalises")
    return df


def normaliser_experience(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme l'experience requise en annees min et max.
    """

    def parser_experience(value):
        if pd.isna(value):
            return None, None

        text = normalize_text(value)

        if "debutant" in text or "junior" in text or "sans experience" in text:
            return 0, 2

        if "senior" in text or "expert" in text or "lead" in text:
            nombres = re.findall(r"\d+", text)
            if nombres:
                return int(nombres[0]), None
            return 5, None

        fourchette = re.search(r"(\d+)\s*[-a]\s*(\d+)", text)
        if fourchette:
            return int(fourchette.group(1)), int(fourchette.group(2))

        nombre = re.search(r"(\d+)", text)
        if nombre:
            return int(nombre.group(1)), None

        return None, None

    resultats = df["experience_requise"].apply(
        lambda x: pd.Series(
            parser_experience(x),
            index=["experience_min_ans", "experience_max_ans"]
        )
    )

    df = pd.concat([df, resultats], axis=1)

    print("[SILVER] Experiences normalisees")
    return df


def normaliser_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convertit les dates et ajoute annee, mois et date_valide.
    """

    df["date_publication_clean"] = pd.to_datetime(df["date_publication"], errors="coerce")
    df["date_expiration_clean"] = pd.to_datetime(df["date_expiration"], errors="coerce")

    df["annee"] = df["date_publication_clean"].dt.year
    df["mois"] = df["date_publication_clean"].dt.month

    df["date_valide"] = (
        df["date_publication_clean"].notna()
        & df["date_expiration_clean"].notna()
        & (df["date_publication_clean"] <= df["date_expiration_clean"])
    )

    print("[SILVER] Dates normalisees")
    return df