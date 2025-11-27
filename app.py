from flask import Flask, request, jsonify, send_from_directory
import os, sys, tempfile, json

# Get project root (one level up from app.py folder)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Add project root to Python path
sys.path.append(PROJECT_ROOT)

from main import process_audio as process_audio_function

# Point Flask to front_end folder
FRONTEND_FOLDER = os.path.join(PROJECT_ROOT, "front_end")

app = Flask(__name__, static_folder=FRONTEND_FOLDER)

@app.route("/")
def index():
    return send_from_directory(FRONTEND_FOLDER, "index.html")


@app.route("/process_audio", methods=["POST"])
def process_route():
    file = request.files.get("audio")
    if not file:
        return jsonify({"error": "No audio file uploaded"}), 400

    # Save uploaded audio temporarily
    ext = os.path.splitext(file.filename)[1]
    temp_audio = tempfile.mktemp(suffix=ext)
    file.save(temp_audio)

    # Run processing
    process_audio_function(temp_audio)

    # Read output JSON
    output_file = os.path.join(PROJECT_ROOT, "data", "output.json")
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
