from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def home():
    return send_from_directory(".", "index.html")  # serve from front_end folder

if __name__ == '__main__':
    app.run(debug=True)
