from flask import Flask, render_template, request, jsonify
from matcher import matcher_grants
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/matching", methods=["POST"])
def matching():
    profil = request.json
    resultats = matcher_grants(profil)
    return jsonify(resultats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)