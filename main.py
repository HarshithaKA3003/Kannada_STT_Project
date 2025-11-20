import json
from modules.speech_to_text import speech_to_text
from modules.pos_tagger import pos_tag
from modules.agreement_checker import fix_agreement
from modules.word_order_corrector import reorder_to_sov


def process_audio(audio_file):

    # 1️⃣ Speech to Text
    text = speech_to_text(audio_file)
    if text.startswith("ERROR"):
        print(text)
        return text

    print("\n🗣 Transcribed Text:", text)

    # 2️⃣ Split words
    words = text.split()

    # 3️⃣ POS Tagging
    pos_tags = pos_tag(words)
    print("\n🔠 POS Tags:", pos_tags)

    # 4️⃣ Fix Subject–Verb Agreement
    if len(words) >= 2:
        subject = words[0]
        verb = words[-1]
        corrected_verb = fix_agreement(subject, verb)
        words[-1] = corrected_verb

    print("\n✔ Corrected Verb:", words[-1])

    # 5️⃣ Reorder to SOV
    final_sentence = reorder_to_sov(words, pos_tags)
    print("\n🔀 Final SOV Sentence:", final_sentence)

    # 6️⃣ Save output to JSON
    output_data = {
        "transcribed_text": text,
        "pos_tags": pos_tags,
        "corrected_verb": words[-1],
        "final_sentence": final_sentence
    }

    with open("data/output.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print("\n📁 Saved to data/output.json")

    return final_sentence


if __name__ == "__main__":
    output = process_audio(r"D:\M K CONSTRUCTIONS\01-01-04.wav")
    print("\n✅ Output:", output)
