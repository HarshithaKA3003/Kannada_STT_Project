import json
import os

# Path to your conjugations file
_CONJ_PATH = os.path.join("data", "verb_conjugations.json")

# Load verb conjugation table safely
try:
    with open(_CONJ_PATH, "r", encoding="utf-8") as fh:
        content = fh.read().strip()
        if not content:
            # Empty file
            verb_data = {}
            print(f"[agreement_checker] Warning: {_CONJ_PATH} is empty.")
        else:
            try:
                verb_data = json.loads(content)
            except json.JSONDecodeError as je:
                print(f"[agreement_checker] JSON decode error in {_CONJ_PATH}: {je}")
                verb_data = {}
except FileNotFoundError:
    print(f"[agreement_checker] Warning: {_CONJ_PATH} not found.")
    verb_data = {}
except Exception as e:
    print(f"[agreement_checker] Error loading {_CONJ_PATH}: {e}")
    verb_data = {}


def fix_agreement(subject, verb, pos_tags=None):
    """
    Fix simple subject-verb agreement for Kannada verbs using verb_data.

    Accepts either:
        fix_agreement(subject, verb)
    or:
        fix_agreement(subject, verb, pos_tags)

    pos_tags (optional) can be a dict mapping word -> feature dict, e.g.
        {"nanu": {"person": "1", "number": "sing", "gender": "none"}}

    Expected structure in verb_data (example):
    {
      "maadu": {
         "1": { "sing": { "male": "maadidene", "female": "maadidini", "none": "maadidini" }, "plur": {...} },
         "2": { ... },
         "3": { ... }
      },
      ...
    }

    If verb_data doesn't contain mapping, return original verb.
    """

    # Default defensive values
    person = None
    number = None
    gender = None

    # If pos_tags provided and contains features for subject, get them
    if pos_tags:
        try:
            # if pos_tags is list or list-of-tuples, try to map
            if isinstance(pos_tags, dict):
                features = pos_tags.get(subject, {})
            else:
                # try convert list of (word, POS/features) to dict if it's (word, {features})
                features = {}
                for item in pos_tags:
                    if isinstance(item, (list, tuple)) and len(item) == 2:
                        w, feat = item
                        if isinstance(feat, dict):
                            features[w] = feat
                features = features.get(subject, {})
            person = features.get("person")
            number = features.get("number")
            gender = features.get("gender")
        except Exception:
            # swallow any parsing issues and fallback to None
            person = number = gender = None

    # If pos_tags didn't provide features, try simple heuristics (optional)
    # For now, if verb_data is empty or missing keys, return original verb
    if not verb_data:
        return verb

    # Defensive lookups - ensure keys exist at each level
    try:
        verb_root = verb  # assume 'verb' is root form; adapt if your JSON keys differ
        if verb_root not in verb_data:
            # maybe verb is already inflected or spelled differently; return original
            return verb

        # If any feature missing, pick a reasonable default ordering
        # Try person -> number -> gender, with fallbacks
        for p in (person, "3", "1", "2"):
            if p is None:
                continue
            p_key = str(p)
            if p_key not in verb_data[verb_root]:
                continue
            # inside person
            person_block = verb_data[verb_root][p_key]

            for n in (number, "sing", "plur"):
                if n is None:
                    continue
                if n not in person_block:
                    continue
                number_block = person_block[n]

                for g in (gender, "none", "male", "female"):
                    if g is None:
                        continue
                    if g in number_block:
                        return number_block[g]
                # if exact gender not found, try any available value
                # return first available string
                for val in number_block.values():
                    return val

        # final fallback: try to return any nested form
        # navigate and return first string found
        def find_any_string(obj):
            if isinstance(obj, str):
                return obj
            if isinstance(obj, dict):
                for k in obj:
                    res = find_any_string(obj[k])
                    if res:
                        return res
            return None

        any_form = find_any_string(verb_data[verb_root])
        if any_form:
            return any_form

    except Exception as e:
        print(f"[agreement_checker] Error during agreement fix lookup: {e}")
        return verb

    # If everything fails, return original verb
    return verb
