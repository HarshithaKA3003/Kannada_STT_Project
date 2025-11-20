import json

# Load POS tags (UTF-8 FIX)
pos_data = json.load(open("data/pos_tags.json", "r", encoding="utf-8"))


def reorder_to_sov(words, pos_tags):
    """
    Reorder words into SOV format (Subject–Object–Verb)
    words    = list of words
    pos_tags = list of (word, POS)
    """

    verb = None
    subjects = []
    objects = []
    others = []

    # Classify words by POS
    for w, tag in pos_tags:

        tag = tag.upper()

        if tag == "VERB":
            verb = w

        elif tag in ("PRON", "NOUN", "SUBJECT"):
            subjects.append(w)

        elif tag in ("OBJ", "OBJECT"):
            objects.append(w)

        else:
            others.append(w)

    # SOV = Subject + Object + Verb
    final_order = []

    if subjects:
        final_order.extend(subjects)

    if objects:
        final_order.extend(objects)

    final_order.extend(others)

    if verb:
        final_order.append(verb)

    # If verb missing → return original
    if not verb:
        return " ".join(words)

    return " ".join(final_order)
