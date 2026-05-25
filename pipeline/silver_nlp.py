import re
import pandas as pd

from pipeline.utils import load_json, normalize_text


def construire_dictionnaire_competences(referentiel_path: str) -> dict:
    """
    Transforme le referentiel en dictionnaire plat :
    alias -> competence normalisee + famille.
    """

    referentiel = load_json(referentiel_path)
    dictionnaire = {}

    for famille, competences in referentiel.get("familles", {}).items():
        for competence_normalisee, aliases in competences.items():
            for alias in aliases:
                alias_normalise = normalize_text(alias)
                dictionnaire[alias_normalise] = {
                    "competence": competence_normalisee,
                    "famille": famille
                }

    return dictionnaire


def extraire_competences(df: pd.DataFrame, referentiel_path: str) -> pd.DataFrame:
    """
    Extrait les competences depuis competences_brut et description.
    Une offre peut produire plusieurs lignes : une ligne par competence trouvee.
    """

    dictionnaire = construire_dictionnaire_competences(referentiel_path)
    aliases_tries = sorted(dictionnaire.keys(), key=len, reverse=True)

    resultats = []

    for _, offre in df.iterrows():
        texte_complet = " ".join([
            str(offre.get("competences_brut", "") or ""),
            str(offre.get("description", "") or "")
        ])

        texte_complet = normalize_text(texte_complet)
        competences_trouvees = set()

        for alias in aliases_tries:
            if len(alias) <= 1:
                continue

            pattern = r"\b" + re.escape(alias) + r"\b"

            if re.search(pattern, texte_complet):
                info = dictionnaire[alias]
                competence = info["competence"]

                if competence not in competences_trouvees:
                    competences_trouvees.add(competence)

                    resultats.append({
                        "id_offre": offre.get("id_offre"),
                        "profil": offre.get("profil_normalise"),
                        "ville": offre.get("ville_std"),
                        "competence": competence,
                        "famille": info["famille"],
                        "date_pub": offre.get("date_publication"),
                        "annee": offre.get("annee"),
                        "mois": offre.get("mois")
                    })

        if not competences_trouvees:
            resultats.append({
                "id_offre": offre.get("id_offre"),
                "profil": offre.get("profil_normalise"),
                "ville": offre.get("ville_std"),
                "competence": "non_detecte",
                "famille": "inconnu",
                "date_pub": offre.get("date_publication"),
                "annee": offre.get("annee"),
                "mois": offre.get("mois")
            })

    df_competences = pd.DataFrame(resultats)

    nb_lignes = len(df_competences)
    nb_offres_avec_competence = df_competences[
        df_competences["competence"] != "non_detecte"
    ]["id_offre"].nunique()

    print(f"[SILVER NLP] {nb_lignes} lignes competences extraites")
    print(f"[SILVER NLP] {nb_offres_avec_competence}/{len(df)} offres avec au moins une competence")

    return df_competences