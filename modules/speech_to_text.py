import speech_recognition as sr
from pydub import AudioSegment
import os
import tempfile

def speech_to_text(audio_path):
    r = sr.Recognizer()

    try:
        # Convert ANY file to WAV
        wav_path = convert_to_wav(audio_path)

        with sr.AudioFile(wav_path) as source:
            r.adjust_for_ambient_noise(source)
            audio = r.record(source)

        text = r.recognize_google(audio, language="kn-IN")
        return text

    except sr.UnknownValueError:
        return "ERROR: Could not understand the audio."

    except sr.RequestError:
        return "ERROR: Speech recognition service failed."

    except Exception as e:
        return "ERROR: " + str(e)


def convert_to_wav(audio_path):
    ext = os.path.splitext(audio_path)[1].lower()

    # If already WAV, no need to convert
    if ext == ".wav":
        return audio_path

    sound = AudioSegment.from_file(audio_path)
    temp_wav = tempfile.mktemp(suffix=".wav")
    sound.export(temp_wav, format="wav")
    return temp_wav
