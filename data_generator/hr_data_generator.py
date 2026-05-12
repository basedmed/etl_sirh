import random
import pandas as pd
from faker import Faker

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import (
    SUBSIDIARIES,
    DEPARTMENTS,
    JOB_LEVELS,
    CONTRACT_TYPES,
    EMPLOYEES_PER_SUBSIDIARY,
    BASE_SALARY_EUR,
    CURRENCY_TO_EUR,
    ABSENCE_TYPES,
    TURNOVER_RATE,
)


def generer_employes(filiale, seed=42):
    Faker.seed(seed)
    fake = Faker(filiale["locale"])
    random.seed(seed)

    n = EMPLOYEES_PER_SUBSIDIARY[filiale["id"]]
    employes = []

    for i in range(n):
        # Est-ce que cet employe a quitte l entreprise ?
        est_parti = random.random() < TURNOVER_RATE[filiale["id"]]
        date_depart = fake.date_between(start_date="-1y", end_date="today") if est_parti else None

        employe = {
            "employee_id":   f"{filiale['id']}-EMP-{str(i+1).zfill(4)}",
            "subsidiary_id": filiale["id"],
            "country":       filiale["country"],
            "prenom":        fake.first_name(),
            "nom":           fake.last_name(),
            "email":         fake.email(),
            "departement":   random.choice(DEPARTMENTS),
            "niveau":        random.choice(JOB_LEVELS),
            "contrat":       random.choice(CONTRACT_TYPES),
            "date_embauche": fake.date_between(start_date="-8y", end_date="today"),
            "est_parti":     est_parti,
            "date_depart":   date_depart,
        }
        employes.append(employe)

    return pd.DataFrame(employes)


def generer_salaires(df_employes, filiale, seed=42):
    random.seed(seed + 1)
    currency = filiale["currency"]
    fx = CURRENCY_TO_EUR[currency]

    salaires = []

    for _, emp in df_employes.iterrows():
        base_eur = BASE_SALARY_EUR[emp["niveau"]]
        variation = random.uniform(0.80, 1.20)

        coeff_pays = {
            "France": 1.0,
            "Allemagne": 1.05,
            "Espagne": 0.90,
            "Maroc": 0.35,
            "Senegal": 0.28
        }.get(filiale["country"], 1.0)

        salaire_eur = round(base_eur * variation * coeff_pays, 2)
        salaire_local = round(salaire_eur / fx, 2)

        salaires.append({
            "employee_id":   emp["employee_id"],
            "subsidiary_id": filiale["id"],
            "salaire_local": salaire_local,
            "devise":        currency,
            "salaire_eur":   salaire_eur,
            "niveau":        emp["niveau"],
        })

    return pd.DataFrame(salaires)


def generer_absences(df_employes, filiale, seed=42):
    random.seed(seed + 2)
    absences = []

    for _, emp in df_employes.iterrows():
        n_absences = random.randint(0, 5)

        for _ in range(n_absences):
            duree = random.randint(1, 30)
            absences.append({
                "employee_id":   emp["employee_id"],
                "subsidiary_id": filiale["id"],
                "type_absence":  random.choice(ABSENCE_TYPES),
                "duree_jours":   duree,
                "annee":         random.randint(2022, 2024),
            })

    return pd.DataFrame(absences)


if __name__ == "__main__":
    tous_les_employes = []
    tous_les_salaires = []
    tous_les_absences = []

    for i, filiale in enumerate(SUBSIDIARIES):
        seed = i * 100
        df_emp = generer_employes(filiale, seed=seed)
        df_sal = generer_salaires(df_emp, filiale, seed=seed)
        df_abs = generer_absences(df_emp, filiale, seed=seed)

        tous_les_employes.append(df_emp)
        tous_les_salaires.append(df_sal)
        tous_les_absences.append(df_abs)

        # Calcul turnover reel
        nb_partis = df_emp["est_parti"].sum()
        taux = round(nb_partis / len(df_emp) * 100, 1)
        print(f"{filiale['name']} -> {len(df_emp)} employes | {nb_partis} departs | turnover {taux}%")

    df_emp_final = pd.concat(tous_les_employes, ignore_index=True)
    df_sal_final = pd.concat(tous_les_salaires, ignore_index=True)
    df_abs_final = pd.concat(tous_les_absences, ignore_index=True)

    os.makedirs("output", exist_ok=True)
    df_emp_final.to_csv("output/employes.csv", index=False, encoding="utf-8-sig")
    df_sal_final.to_csv("output/salaires.csv",  index=False, encoding="utf-8-sig")
    df_abs_final.to_csv("output/absences.csv",  index=False, encoding="utf-8-sig")

    print(f"\nTotal employes : {len(df_emp_final)}")
    print(f"Total salaires : {len(df_sal_final)}")
    print(f"Total absences : {len(df_abs_final)}")