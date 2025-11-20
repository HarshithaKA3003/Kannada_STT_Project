import json

pos_data = json.load(open("data/pos_tags.json", "r", encoding="utf-8"))

def pos_tag(words_list):
    output = []
    for w in words_list:
        tag = pos_data.get(w, "UNK")
        output.append((w, tag))
    return output
