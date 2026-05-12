# Pipeline ETL SIRH — Consolidation Données RH Multi-filiales

Projet personnel · Data Engineering · 2026

## Objectif

Pipeline ETL complet simulant la consolidation de données RH issues de 5 filiales internationales (France, Allemagne, Espagne, Maroc, Sénégal).

## Données traitées

- Effectifs : 340 employés sur 5 filiales
- Rémunération : salaires en devise locale + conversion EUR
- Absentéisme : 877 événements d'absence
- Turnover : taux de départ par filiale

## Ce que fait le pipeline

### Extract
- API REST Flask exposant les données de chaque filiale
- Appels HTTP via requests pour chaque endpoint

### Transform
- Détection et correction de 5 types d anomalies :
  - Valeurs manquantes
  - Doublons
  - Departements hors referentiel
  - Emails mal formates
  - Niveaux hors referentiel

### Load
- Chargement en base SQLite via SQLAlchemy
- 3 tables : employes, salaires, absences

## KPIs calculés

- Effectifs par filiale
- Salaire moyen par filiale et par niveau
- Taux de turnover par filiale
- Jours d absence par filiale
- Types d absence les plus frequents

## Stack technique

Python · Pandas · SQL · API REST · Flask · SQLAlchemy · SQLite · Git

## Lancement

Installer les dependances :
pip install faker pandas sqlalchemy flask requests

Lancer l API :
python3 api_server.py

Lancer le pipeline :
python3 pipeline.py

Lancer les analyses SQL :
python3 analyse.py