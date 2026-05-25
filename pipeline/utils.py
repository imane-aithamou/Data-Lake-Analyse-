from pathlib import Path
import json
import re
import unicodedata


def ensure_dir(path):
    """
    Cree un dossier s'il n'existe pas encore.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def load_json(path):
    """
    Charge un fichier JSON avec l'encodage UTF-8.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    """
    Sauvegarde des donnees dans un fichier JSON.
    """
    ensure_dir(Path(path).parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_text(value):
    """
    Normalise un texte pour faciliter les comparaisons :
    - minuscules
    - suppression des accents
    - suppression des espaces inutiles
    """
    if value is None:
        return ""

    value = str(value).strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = re.sub(r"\s+", " ", value)

    return value


def safe_get_month(date_value):
    """
    Extrait une partition mois au format YYYY_MM depuis une date YYYY-MM-DD.
    Si la date est invalide, retourne date_inconnue.
    """
    if not date_value:
        return "date_inconnue"

    text = str(date_value).strip()

    if len(text) >= 7:
        year_month = text[:7]
        if re.match(r"^\d{4}-\d{2}$", year_month):
            return year_month.replace("-", "_")

    return "date_inconnue"


def normalize_source(value):
    """
    Normalise le nom de la source pour creer un nom de dossier propre.
    """
    text = normalize_text(value)

    if not text:
        return "inconnu"

    text = text.replace(" ", "_")
    text = re.sub(r"[^a-z0-9_]", "", text)

    return text or "inconnu"