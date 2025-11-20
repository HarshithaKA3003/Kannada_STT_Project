import speech_recognition as sr

def speech_to_text(audio_file):
    r = sr.Recognizer()
    
    try:
        with sr.AudioFile(audio_file) as source:
            r.adjust_for_ambient_noise(source, duration=0.4)  # Noise reduction
            audio = r.record(source)

        # Google Kannada Speech-to-Text
        text = r.recognize_google(audio, language="kn-IN")

        # Ensure UTF-8 safe output
        return text.encode("utf-8").decode("utf-8")

    except sr.UnknownValueError:
        return "ERROR: Could not understand the audio."
    
    except sr.RequestError:
        return "ERROR: Speech recognition service failed. Check internet."
    
    except Exception as e:
        return "ERROR: " + str(e)
