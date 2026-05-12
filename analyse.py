import sys
import os
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import DATABASE_URL

# Connexion a la base
engine = create_engine(DATABASE_URL)

def run_query(titre, sql):
    """Execute une requete SQL et affiche le resultat."""
    print(f"\n--- {titre} ---")
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        for row in result:
            print(row)


if __name__ == "__main__":

    # 1. Effectifs par filiale
    run_query(
        "Effectifs par filiale",
        """
        SELECT subsidiary_id, COUNT(*) as nb_employes
        FROM employes
        GROUP BY subsidiary_id
        ORDER BY nb_employes DESC
        """
    )

    # 2. Salaire moyen par filiale
    run_query(
        "Salaire moyen par filiale (EUR)",
        """
        SELECT subsidiary_id, ROUND(AVG(salaire_eur), 2) as salaire_moyen
        FROM salaires
        GROUP BY subsidiary_id
        ORDER BY salaire_moyen DESC
        """
    )

    # 3. Salaire moyen par niveau
    run_query(
        "Salaire moyen par niveau (EUR)",
        """
        SELECT niveau, ROUND(AVG(salaire_eur), 2) as salaire_moyen
        FROM salaires
        GROUP BY niveau
        ORDER BY salaire_moyen DESC
        """
    )

    # 4. Absences par filiale
    run_query(
        "Total jours d absence par filiale",
        """
        SELECT subsidiary_id, 
               COUNT(*) as nb_absences,
               SUM(duree_jours) as total_jours
        FROM absences
        GROUP BY subsidiary_id
        ORDER BY total_jours DESC
        """
    )

    # 5. Type d absence le plus frequent
    run_query(
        "Types d absence les plus frequents",
        """
        SELECT type_absence, COUNT(*) as nb
        FROM absences
        GROUP BY type_absence
        ORDER BY nb DESC
        """
    )

    # 6. Effectifs par departement
    run_query(
        "Effectifs par departement",
        """
        SELECT departement, COUNT(*) as nb_employes
        FROM employes
        GROUP BY departement
        ORDER BY nb_employes DESC
        """
    )
    # 7. Turnover par filiale
    run_query(
        "Turnover par filiale",
        """
        SELECT 
            subsidiary_id,
            COUNT(*) as effectif_total,
            SUM(CASE WHEN est_parti = 1 THEN 1 ELSE 0 END) as nb_departs,
            ROUND(SUM(CASE WHEN est_parti = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as taux_turnover
        FROM employes
        GROUP BY subsidiary_id
        ORDER BY taux_turnover DESC
        """
    )