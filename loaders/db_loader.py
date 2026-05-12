import pandas as pd
import sys
import os
from sqlalchemy import create_engine

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import DATABASE_URL


def charger_en_base(df, nom_table):
    """
    Charge un DataFrame dans la base SQLite.
    df        : le DataFrame propre
    nom_table : le nom de la table dans la base
    """
    # On se connecte a la base
    engine = create_engine(DATABASE_URL)

    # On charge le DataFrame dans la table
    df.to_sql(nom_table, engine, if_exists="replace", index=False)

    print(f"Table '{nom_table}' chargee : {len(df)} lignes")


if __name__ == "__main__":

    from data_generator.hr_data_generator import generer_employes
    from data_generator.injector import injecter_erreurs
    from transformers.cleaner import nettoyer
    from config import SUBSIDIARIES

    # On genere, on sale, on nettoie
    df_propre = generer_employes(SUBSIDIARIES[0])
    df_sale = injecter_erreurs(df_propre)
    df_final = nettoyer(df_sale)

    # On charge en base
    charger_en_base(df_final, "employes")