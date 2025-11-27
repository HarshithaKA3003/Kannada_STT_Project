import json
import os

# Use project-level data folder
PROJECT_DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_POS_PATH = os.path.join(PROJECT_DATA, "pos_tags.json")

try:
    with open(_POS_PATH, "r", encoding="utf-8") as f:
        pos_data = json.load(f)
except Exception:
    pos_data = {}


def smart_pos_guess(word):
    """Fallback POS guess when tagger gives UNK."""
    w = (word or "").strip()
    if not w:
        return "UNK"

    # Very small set of verb cues in Kannada finite forms
    if w.endswith("ನು") or w.endswith("ಳು") or w.endswith("ದನು") or w.endswith("ದಳು") or w.endswith("ಯಿತು"):
        return "VERB"

    # object markers
    if w.endswith("ನ್ನು") or w.endswith("ಗೆ") or w.endswith("ಕ್ಕೆ") or w.endswith("ನಿಗೆ"):
        return "OBJ"

    # location markers
    if w.endswith("ಲ್ಲಿ") or w.endswith("ನಲ್ಲ") or w.endswith("ಕ್ಕೆ"):
        return "LOC"

    # pronouns
    if w in {"ನಾನು", "ನೀನು", "ಅವನು", "ಅವಳು", "ಅವರು", "ನಾವು"}:
        return "PRON"

    return "NOUN"


def looks_like_object(word):
    markers = ["ಗೆ", "ಅನ್ನು", "ಯನ್ನು", "ಕ್ಕೆ", "ನಿಗೆ"]
    return any(word.endswith(m) for m in markers)


def reorder_to_sov(words, pos_tags):
    """
    Build S O (location/other) V order.
    pos_tags: list of (word, features) tuples.
    This function trusts pos_tags; if tag == UNK, uses smart_pos_guess.
    """

    subject = None
    verb = None
    objects = []
    locations = []
    others = []

    for (w, feats) in pos_tags:
        tag = "UNK"
        if isinstance(feats, dict):
            tag = feats.get("pos", "UNK")
        tag = str(tag).upper()

        if tag == "UNK":
            tag = smart_pos_guess(w)

        if tag == "VERB":
            # Keep the last verb seen (main verb)
            verb = w

        elif tag in ("PRON", "NOUN"):
            # prefer to treat marked objects as objects
            if looks_like_object(w):
                objects.append(w)
            else:
                if not subject:
                    subject = w
                else:
                    others.append(w)

        elif tag == "OBJ":
            objects.append(w)

        elif tag == "LOC":
            locations.append(w)

        else:
            others.append(w)

    # If no verb found, return original ordering (join words)
    if not verb:
        return " ".join(words)

    final_order = []
    if subject:
        final_order.append(subject)

    final_order.extend(objects)
    final_order.extend(locations)
    final_order.extend(others)

    final_order.append(verb)
    return " ".join(final_order)
