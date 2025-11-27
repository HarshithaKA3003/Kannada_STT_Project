import json
import os

# Use project-level data folder
PROJECT_DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
POS_PATH = os.path.join(PROJECT_DATA, "pos_tags.json")
GENDER_PATH = os.path.join(PROJECT_DATA, "gender_names.json")

# Load optional dictionaries
try:
    with open(POS_PATH, "r", encoding="utf-8") as f:
        pos_data = json.load(f)
except Exception:
    pos_data = {}

try:
    with open(GENDER_PATH, "r", encoding="utf-8") as f:
        gender_data = json.load(f)
except Exception:
    gender_data = {"female": [], "male": []}


def get_gender(word):
    if word in gender_data.get("female", []):
        return "female"
    if word in gender_data.get("male", []):
        return "male"
    return None


def smart_pos_guess(word):
    w = (word or "").strip()
    if not w:
        return "UNK"

    # verb heuristics
    if w.endswith("ನು") or w.endswith("ಳು") or w.endswith("ದನು") or w.endswith("ಯಿತು") or w.endswith("ದಳು"):
        return "VERB"

    # object markers
    if w.endswith("ನ್ನು") or w.endswith("ಗೆ") or w.endswith("ಕ್ಕೆ") or w.endswith("ನಿಗೆ"):
        return "OBJ"

    # location markers
    if w.endswith("ಲ್ಲಿ") or w.endswith("ನಲ್ಲ") or w.endswith("ಕೆ"):
        return "LOC"

    # pronouns
    if w in {"ನಾನು", "ನೀನು", "ಅವನು", "ಅವಳು", "ಅವರು", "ನಾವು"}:
        return "PRON"

    return "NOUN"


def pos_tag(words_list):
    """
    Return list of (word, features) where features is a dict:
      { "pos": "NOUN"/"VERB"/..., "person": "...", "number": "...", "gender": "female" }
    """

    output = []
    for w in words_list:
        entry = pos_data.get(w)
        if isinstance(entry, dict):
            features = entry.copy()
            if "tag" in features:
                features["pos"] = features.pop("tag").upper()
            else:
                features["pos"] = features.get("pos", "UNK").upper()
        elif isinstance(entry, str):
            features = {"pos": entry.upper()}
        else:
            guessed = smart_pos_guess(w)
            features = {"pos": guessed}

        # default person/number for nouns/pronouns
        if features["pos"] in ("NOUN", "PRON", "UNK"):
            features.setdefault("person", "third")
            features.setdefault("number", "singular")

        # attach gender if known from gender_data
        gender = get_gender(w)
        if gender:
            features["gender"] = gender

        output.append((w, features))

    return output
