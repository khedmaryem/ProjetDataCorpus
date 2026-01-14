# Projet d'Analyse de Corpus et Dashboard

Ce projet porte sur le développement d'un tableau de bord de visualisation de données conçu avec Python et Dash. Il permet d'analyser un corpus de documents, d'explorer les thématiques, l'évolution temporelle et la répartition géographique des données.

## Prérequis

- Python 3.8 ou supérieur installé sur votre machine.
- Pip (gestionnaire de paquets Python).

## Installation

1.  Clonez ce dépôt ou téléchargez les fichiers.
2.  Ouvrez un terminal dans le dossier du projet.
3.  Installez les dépendances nécessaires en utilisant `requirements.txt` :

    ```bash
    pip install -r requirements.txt
    ```

    Ou installez manuellement les librairies principales :

    ```bash
    pip install dash pandas plotly
    ```

## Démarrage

Pour lancer l'application, exécutez la commande suivante dans votre terminal :

```bash
python app.py
```

## Utilisation

Une fois l'application lancée, ouvrez votre navigateur web et accédez à l'adresse suivante :

**http://127.0.0.1:8050/**

Le dashboard est composé de trois onglets principaux :
1.  **Analyse Annuelle Détaillée** : Pour explorer les données année par année.
2.  **Comparaison 2024 vs 2025** : Pour comparer les tendances entre les années.
3.  **Aperçu Global du Corpus** : Pour une vue d'ensemble, incluant la carte géographique interactive et les nuages de mots.
