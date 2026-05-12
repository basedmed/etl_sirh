from flask import Flask, jsonify
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import SUBSIDIARIES
from data_generator.hr_data_generator import generer_employes, generer_salaires, generer_absences

app = Flask(__name__)


@app.route("/api/filiales", methods=["GET"])
def get_filiales():
    """Retourne la liste des filiales."""
    return jsonify(SUBSIDIARIES)


@app.route("/api/employes/<subsidiary_id>", methods=["GET"])
def get_employes(subsidiary_id):
    """Retourne les employes d une filiale."""
    filiale = next((f for f in SUBSIDIARIES if f["id"] == subsidiary_id), None)
    if not filiale:
        return jsonify({"erreur": "Filiale introuvable"}), 404

    i = SUBSIDIARIES.index(filiale)
    df = generer_employes(filiale, seed=i*100)
    return jsonify(df.astype(str).to_dict(orient="records"))


@app.route("/api/salaires/<subsidiary_id>", methods=["GET"])
def get_salaires(subsidiary_id):
    """Retourne les salaires d une filiale."""
    filiale = next((f for f in SUBSIDIARIES if f["id"] == subsidiary_id), None)
    if not filiale:
        return jsonify({"erreur": "Filiale introuvable"}), 404

    i = SUBSIDIARIES.index(filiale)
    df_emp = generer_employes(filiale, seed=i*100)
    df_sal = generer_salaires(df_emp, filiale, seed=i*100)
    return jsonify(df_sal.astype(str).to_dict(orient="records"))


@app.route("/api/absences/<subsidiary_id>", methods=["GET"])
def get_absences(subsidiary_id):
    """Retourne les absences d une filiale."""
    filiale = next((f for f in SUBSIDIARIES if f["id"] == subsidiary_id), None)
    if not filiale:
        return jsonify({"erreur": "Filiale introuvable"}), 404

    i = SUBSIDIARIES.index(filiale)
    df_emp = generer_employes(filiale, seed=i*100)
    df_abs = generer_absences(df_emp, filiale, seed=i*100)
    return jsonify(df_abs.astype(str).to_dict(orient="records"))


if __name__ == "__main__":
    print("API SIRH demarree sur http://localhost:5000")
    app.run(debug=True, port=5000)