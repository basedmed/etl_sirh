import pandas as pd
import random
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_generator.hr_data_generator import generer_employes
from config import SUBSIDIARIES


def injecter_erreurs(df, seed=42):
    random.seed(seed)
    df = df.copy()

    # Erreur 1 : valeurs manquantes
    indices = random.sample(range(len(df)), 5)
    df.loc[indices, "prenom"] = None
    print(f"Erreur 1 : {df['prenom'].isna().sum()} prenoms manquants injectes")

    # Erreur 2 : doublons
    doublons = df.sample(3, random_state=seed)
    df = pd.concat([df, doublons], ignore_index=True)
    print(f"Erreur 2 : {df.duplicated().sum()} doublons injectes")

    # Erreur 3 : departements hors referentiel
    faux_departements = ["Ventes", "rh", "INFORMATIQUE", "Direction", "Compta"]
    indices = random.sample(range(len(df)), 8)
    df.loc[indices, "departement"] = random.choices(faux_departements, k=8)
    print(f"Erreur 3 : 8 departements hors referentiel injectes")

    # Erreur 4 : emails mal formates
    faux_emails = ["pasdeemail", "manque@", "@sansnom.com", "espaces @gmail.com"]
    indices = random.sample(range(len(df)), 6)
    df.loc[indices, "email"] = random.choices(faux_emails, k=6)
    print(f"Erreur 4 : 6 emails mal formates injectes")

    # Erreur 5 : niveaux hors referentiel
    faux_niveaux = ["Debutant", "SENIOR", "chef", "pro", "novice"]
    indices = random.sample(range(len(df)), 5)
    df.loc[indices, "niveau"] = random.choices(faux_niveaux, k=5)
    print(f"Erreur 5 : 5 niveaux hors referentiel injectes")

    return df


if __name__ == "__main__":
    df_propre = generer_employes(SUBSIDIARIES[0])
    df_sale = injecter_erreurs(df_propre)