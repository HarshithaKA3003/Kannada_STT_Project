import whisper

model = whisper.load_model("base")

def transcribe_audio(path):
    result = model.transcribe(path, language="kn")
    return result["text"]
