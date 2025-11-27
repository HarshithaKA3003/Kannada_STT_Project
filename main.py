import json
import os
from modules.speech_to_text import speech_to_text
from modules.pos_tagger import pos_tag
from modules.agreement_checker import fix_agreement
from modules.word_order_corrector import reorder_to_sov


def process_audio(audio_file):

    # 1. Speech → Text
    text = speech_to_text(audio_file)
    if text.startswith("ERROR"):
        return text

    words = text.split()

    # 2. POS Tagging (ensure tuple format)
    pos_tags = pos_tag(words)               # returns list of (word, feats)
    pos_tags = [(w, t) for (w, t) in pos_tags]

    # 3. Agreement Fix
    corrected_verb = ""
    if len(words) >= 2:
        subject = words[0]
        verb = words[-1]

        corrected_verb = fix_agreement(
            subject=subject,
            verb=verb,
            pos_tags=pos_tags,
            words=words
        )

        # update words list with corrected verb
        words[-1] = corrected_verb

        # update pos_tags to reflect corrected verb token
        if pos_tags:
            new_pos_tags = []
            verb_replaced = False
            for w, feats in pos_tags:
                pos_upper = ""
                if isinstance(feats, dict):
                    pos_upper = feats.get("pos", "").upper()
                if (not verb_replaced) and pos_upper == "VERB":
                    # replace token but keep features the same
                    new_pos_tags.append((corrected_verb, feats))
                    verb_replaced = True
                else:
                    new_pos_tags.append((w, feats))
            # if no VERB found in pos_tags, append one
            if not verb_replaced:
                new_pos_tags.append((corrected_verb, {"pos": "VERB"}))
            pos_tags = new_pos_tags
    else:
        corrected_verb = ""

    # 4. Reorder SOV using updated pos_tags
    final_sentence = reorder_to_sov(words, pos_tags)

    # 5. Save Output to JSON
    data_folder = os.path.join(os.path.dirname(__file__), "data")
    output_path = os.path.join(data_folder, "output.json")

    output_data = {
        "transcribed_text": text,
        "words": words,
        "pos_tags": pos_tags,        # tuples → JSON converts to lists
        "corrected_verb": corrected_verb,
        "final_sentence": final_sentence
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    return final_sentence
