from modules.speech_to_text import speech_to_text
from modules.pos_tagger import pos_tag
from modules.agreement_checker import fix_agreement
from modules.word_order_corrector import reorder_to_sov


def process_audio(audio_file):
    # 1️⃣ Step: Speech to Text
    text = speech_to_text(audio_file)
    
    if text.startswith("ERROR"):
        print(text)
        return text

    print("\n🗣 Transcribed Text:", text)

    # 2️⃣ Step: Split words
    words = text.split()

    # 3️⃣ Step: POS Tagging
    pos_tags = pos_tag(words)
    print("\n🔠 POS Tags:", pos_tags)

    # 4️⃣ Step: Fix Agreement (Subject–Verb)
    if len(words) >= 2:
        subject = words[0]
        verb = words[-1]
        corrected_verb = fix_agreement(subject, verb)
        words[-1] = corrected_verb

    print("\n✔ Corrected Verb (Agreement Fix):", words[-1])

    # 5️⃣ Step: Reorder to SOV
    final_sentence = reorder_to_sov(words, pos_tags)

    print("\n🔀 Final SOV Corrected Sentence:", final_sentence)

    return final_sentence


if __name__ == "__main__":
    output = process_audio(r"C:\Users\win10\Desktop\Kannada_stt_project\sample.wav")
    print("\n✅ Output:", output)
