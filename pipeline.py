import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import SUBSIDIARIES
from data_generator.hr_data_generator import generer_employes, generer_salaires, generer_absences
from data_generator.injector import injecter_erreurs
from transformers.cleaner import nettoyer
from loaders.db_loader import charger_en_base


def run_pipeline():
    print("=== PIPELINE ETL SIRH ===\n")

    tous_employes = []
    tous_salaires = []
    tous_absences = []

    for i, filiale in enumerate(SUBSIDIARIES):
        print(f"--- Filiale : {filiale['name']} ---")
        seed = i * 100

        # EXTRACT
        df_emp = generer_employes(filiale, seed=seed)
        df_sal = generer_salaires(df_emp, filiale, seed=seed)
        df_abs = generer_absences(df_emp, filiale, seed=seed)

        # TRANSFORM
        df_emp = injecter_erreurs(df_emp, seed=seed)
        df_emp = nettoyer(df_emp)

        tous_employes.append(df_emp)
        tous_salaires.append(df_sal)
        tous_absences.append(df_abs)

    # Consolidation
    df_emp_final = pd.concat(tous_employes, ignore_index=True)
    df_sal_final = pd.concat(tous_salaires, ignore_index=True)
    df_abs_final = pd.concat(tous_absences, ignore_index=True)

    # LOAD
    charger_en_base(df_emp_final, "employes")
    charger_en_base(df_sal_final, "salaires")
    charger_en_base(df_abs_final, "absences")

    print("\n=== PIPELINE TERMINE ===")
    print(f"Employes : {len(df_emp_final)}")
    print(f"Salaires : {len(df_sal_final)}")
    print(f"Absences : {len(df_abs_final)}")

    # EXPORT CSV pour Power BI
    os.makedirs("output", exist_ok=True)
    df_emp_final.to_csv("output/employes.csv", index=False, encoding="utf-8-sig")
    df_sal_final.to_csv("output/salaires.csv",  index=False, encoding="utf-8-sig")
    df_abs_final.to_csv("output/absences.csv",  index=False, encoding="utf-8-sig")
    print("CSV exportes -> output/")


if __name__ == "__main__":
    run_pipeline()