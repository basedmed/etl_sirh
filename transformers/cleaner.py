print("fichier lance")

import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import DEPARTMENTS, JOB_LEVELS, CONTRACT_TYPES


def nettoyer(df):
    print("--- DEBUT NETTOYAGE ---")
    print(f"Lignes avant nettoyage : {len(df)}")

    # 1. Supprimer les doublons
    avant = len(df)
    df = df.drop_duplicates()
    print(f"Doublons supprimes : {avant - len(df)}")

    # 2. Prenoms manquants
    manquants = df["prenom"].isna().sum()
    df["prenom"] = df["prenom"].fillna("Inconnu")
    print(f"Prenoms manquants corriges : {manquants}")

    # 3. Departements hors referentiel
    hors_ref = ~df["departement"].isin(DEPARTMENTS)
    df.loc[hors_ref, "departement"] = "Autre"
    print(f"Departements corriges : {hors_ref.sum()}")

    # 4. Emails mal formates
    masque = df["email"].str.match(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$", na=False)
    invalides = ~masque
    df.loc[invalides, "email"] = "inconnu@entreprise.com"
    print(f"Emails corriges : {invalides.sum()}")

    # 5. Niveaux hors referentiel
    hors_ref_niv = ~df["niveau"].isin(JOB_LEVELS)
    df.loc[hors_ref_niv, "niveau"] = "Junior"
    print(f"Niveaux corriges : {hors_ref_niv.sum()}")

    print(f"Lignes apres nettoyage : {len(df)}")
    print("--- NETTOYAGE TERMINE ---")

    return df


if __name__ == "__main__":

    from data_generator.hr_data_generator import generer_employes
    from data_generator.injector import injecter_erreurs
    from config import SUBSIDIARIES

    df_propre = generer_employes(SUBSIDIARIES[0])
    print(f"Donnees propres : {len(df_propre)} lignes")

    print("\n--- INJECTION ERREURS ---")
    df_sale = injecter_erreurs(df_propre)
    print(f"Donnees sales : {len(df_sale)} lignes")

    print()
    df_final = nettoyer(df_sale)