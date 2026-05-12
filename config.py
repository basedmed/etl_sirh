# Les filiales de notre groupe fictif
SUBSIDIARIES = [
    {"id": "FR01", "name": "France Siège",   "country": "France",    "currency": "EUR", "locale": "fr_FR"},
    {"id": "DE02", "name": "Allemagne GmbH", "country": "Allemagne", "currency": "EUR", "locale": "de_DE"},
    {"id": "ES03", "name": "Espagne SL",     "country": "Espagne",   "currency": "EUR", "locale": "es_ES"},
    {"id": "MA04", "name": "Maroc SARL",     "country": "Maroc",     "currency": "MAD", "locale": "fr_FR"},
    {"id": "SN05", "name": "Sénégal SA",     "country": "Sénégal",   "currency": "XOF", "locale": "fr_FR"},
]

# Les départements possibles dans l'entreprise
DEPARTMENTS = ["RH", "Finance", "IT", "Commercial", "Production", "Marketing", "Logistique"]

# Les niveaux de poste
JOB_LEVELS = ["Stagiaire", "Junior", "Confirmé", "Senior", "Manager", "Directeur"]

# Les types de contrat
CONTRACT_TYPES = ["CDI", "CDD", "Alternance", "Stage", "Intérim"]

# Les types d'absence
ABSENCE_TYPES = ["Maladie", "Congés payés", "RTT", "Accident travail", "Autre"]

# Combien d'employés dans chaque filiale
EMPLOYEES_PER_SUBSIDIARY = {
    "FR01": 120,
    "DE02": 85,
    "ES03": 60,
    "MA04": 45,
    "SN05": 30,
}

# Salaire brut mensuel de base en EUR selon le niveau
BASE_SALARY_EUR = {
    "Stagiaire":  800,
    "Junior":     2200,
    "Confirmé":   3200,
    "Senior":     4500,
    "Manager":    6000,
    "Directeur":  9000,
}

# Taux de conversion vers EUR
CURRENCY_TO_EUR = {
    "EUR": 1.0,
    "MAD": 0.092,
    "XOF": 0.00153,
}

# Taux de turnover annuel par filiale (% d'employés qui partent)
TURNOVER_RATE = {
    "FR01": 0.08,   # 8%
    "DE02": 0.06,   # 6%
    "ES03": 0.12,   # 12%
    "MA04": 0.18,   # 18%
    "SN05": 0.22,   # 22%
}

# Base de données SQLite 
DATABASE_URL = "sqlite:///sirh_dw.db"