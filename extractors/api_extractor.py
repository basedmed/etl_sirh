import requests
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import SUBSIDIARIES

BASE_URL = "http://127.0.0.1:5000"


def extraire_employes(subsidiary_id):
    """Appelle l API et recupere les employes d une filiale."""
    print(f"Appel API -> /api/employes/{subsidiary_id}")
    response = requests.get(f"{BASE_URL}/api/employes/{subsidiary_id}")

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        print(f"Recu : {len(df)} employes")
        return df
    else:
        print(f"Erreur API : {response.status_code}")
        return None


def extraire_salaires(subsidiary_id):
    """Appelle l API et recupere les salaires d une filiale."""
    print(f"Appel API -> /api/salaires/{subsidiary_id}")
    response = requests.get(f"{BASE_URL}/api/salaires/{subsidiary_id}")

    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data)
    else:
        print(f"Erreur API : {response.status_code}")
        return None


def extraire_absences(subsidiary_id):
    """Appelle l API et recupere les absences d une filiale."""
    print(f"Appel API -> /api/absences/{subsidiary_id}")
    response = requests.get(f"{BASE_URL}/api/absences/{subsidiary_id}")

    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data)
    else:
        print(f"Erreur API : {response.status_code}")
        return None


def extraire_toutes_filiales():
    """Extrait les donnees de toutes les filiales via l API."""
    tous_employes = []
    tous_salaires = []
    tous_absences = []

    for filiale in SUBSIDIARIES:
        print(f"\n--- Extraction {filiale['name']} ---")
        df_emp = extraire_employes(filiale["id"])
        df_sal = extraire_salaires(filiale["id"])
        df_abs = extraire_absences(filiale["id"])

        if df_emp is not None:
            tous_employes.append(df_emp)
        if df_sal is not None:
            tous_salaires.append(df_sal)
        if df_abs is not None:
            tous_absences.append(df_abs)

    return (
        pd.concat(tous_employes, ignore_index=True),
        pd.concat(tous_salaires, ignore_index=True),
        pd.concat(tous_absences, ignore_index=True),
    )


if __name__ == "__main__":
    df_emp, df_sal, df_abs = extraire_toutes_filiales()
    print(f"\nTotal employes : {len(df_emp)}")
    print(f"Total salaires : {len(df_sal)}")
    print(f"Total absences : {len(df_abs)}")