import json
import os

# Use project-level data folder (one level up from modules/)
PROJECT_DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_CONJ_PATH = os.path.join(PROJECT_DATA, "verb_conjugations.json")
_GENDER_PATH = os.path.join(PROJECT_DATA, "gender_names.json")

# Load conjugations (safe)
try:
    with open(_CONJ_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
        verb_data = json.loads(content) if content else {}
except Exception:
    verb_data = {}

# Load optional gender dictionary (may not exist)
try:
    with open(_GENDER_PATH, "r", encoding="utf-8") as f:
        gender_dict = json.load(f)
except Exception:
    gender_dict = {"female": [], "male": []}


def detect_gender(words):
    """
    Auto-detect gender using multiple signals:
     1) gender_dict (if present)
     2) small built-in special-name lists
     3) heuristic suffix rules for Kannada names
    Returns: "female", "male", or None
    """
    # small built-in lists (extend as needed)
    female_special = {"ಹರ್ಷಿತ", "ಹರ್ಷಿತಾ", "ಪ್ರಿಯಾ", "ರೇವತಿ", "ಪ್ರಿಯాంకಾ"}
    male_special = {"ಹರ್ಷಿತ್", "ಪ್ರಸಾದ್", "ಸುದೀಪ್", "ರಾಘವ"}

    female_suffixes = ["ಾ", "ತಾ", "ೀಕಾ", "ಿತಾ", "ಾಳ"]
    male_suffixes = ["್ರಾಜ", "್ಶ್", "ಕುಮಾರ್", "್ನ್", "ೇಶ್"]

    for w in words:
        if not isinstance(w, str):
            continue

        # 1) dictionary lookup
        if w in gender_dict.get("female", []):
            return "female"
        if w in gender_dict.get("male", []):
            return "male"

        # 2) small special lists
        if w in female_special:
            return "female"
        if w in male_special:
            return "male"

        # 3) suffix heuristics
        for suf in female_suffixes:
            if w.endswith(suf):
                return "female"
        for suf in male_suffixes:
            if w.endswith(suf):
                return "male"

    return None


def _normalize_person(person_in):
    if person_in is None:
        return "3"
    s = str(person_in).lower()
    if s.startswith("1"):
        return "1"
    if s.startswith("2"):
        return "2"
    return "3"


def _normalize_number(number_in):
    if number_in is None:
        return "sing"
    s = str(number_in).lower()
    if s.startswith("pl"):
        return "plur"
    return "sing"


def _heuristic_feminize_verb(verb):
    """
    Conservative feminize heuristic:
      - Handles typical finite masculine endings: 'ನು' -> 'ಳು'
      - Handles 'ದನು' -> 'ದಳು'
    Avoids aggressive rewrites.
    """
    if not isinstance(verb, str) or len(verb) < 2:
        return verb

    # common: 'ದನು' -> 'ದಳು' (e.g., 'ಹೋದನು' -> 'ಹೋದಳು')
    if verb.endswith("ದನು"):
        # replace last two characters 'ನು' with 'ಳು' but keep preceding char 'ದ'
        return verb[:-2] + "ಳು"

    # generic 'ನು' -> 'ಳು' (safe for many verbs)
    if verb.endswith("ನು"):
        return verb[:-1] + "ಳು"

    # if already feminine form or unknown, return as-is
    return verb


def fix_agreement(subject, verb, pos_tags=None, words=None):
    """
    Main public function.
    - Tries to use verb_conjugations.json first (exact key match).
    - Falls back to translit map if provided (small mapping).
    - If not found and subject is female, applies conservative heuristic.
    - Returns a string (corrected verb) — never a non-string.
    """
    person = "3"
    number = "sing"
    gender = "none"

    # extract person/number/gender from pos_tags if available
    if pos_tags:
        try:
            for w, feats in pos_tags:
                if w == subject and isinstance(feats, dict):
                    person = _normalize_person(feats.get("person", person))
                    number = _normalize_number(feats.get("number", number))
                    g = feats.get("gender")
                    if g:
                        gender = g
        except Exception:
            pass

    # detect gender from words if still none
    if gender in (None, "none") and words:
        g = detect_gender(words)
        if g:
            gender = g

    # 1) Try direct lookup in verb_data using verb as key
    try:
        entry = verb_data.get(verb)
        if entry:
            p_entry = entry.get(str(person))
            if p_entry:
                num_entry = p_entry.get(number)
                if num_entry:
                    # prefer gendered entry, then 'none'
                    if gender in num_entry and num_entry.get(gender):
                        return num_entry.get(gender)
                    if "none" in num_entry and num_entry.get("none"):
                        return num_entry.get("none")
    except Exception:
        pass

    # 2) Try a tiny mapping for common Kannada verbs to romanized keys in verb_data
    # (you can extend this map to include more verbs)
    translit_map = {
        "ಮಾಡು": "maadu",
        "ಮಾಡಿದನು": "maaduttiddane",
        "ಮಾಡಿದ್ದರು": "maaduttiddare",
    }
    try:
        mapped = translit_map.get(verb)
        if mapped and mapped in verb_data:
            entry = verb_data[mapped]
            p_entry = entry.get(str(person))
            if p_entry:
                num_entry = p_entry.get(number)
                if num_entry:
                    if gender in num_entry and num_entry.get(gender):
                        return num_entry.get(gender)
                    if "none" in num_entry and num_entry.get("none"):
                        return num_entry.get("none")
    except Exception:
        pass

    # 3) If subject is female, apply conservative heuristic
    if gender == "female":
        heur = _heuristic_feminize_verb(verb)
        if heur != verb:
            return heur

    # final fallback: return verb unchanged
    return verb
