# Marche a suivre

## Prérequis

- Python 3.x
- MySQL en cours d'exécution en local

## Installation

1. Créer et activer l'environnement virtuel :

```bash
python -m venv venv
source venv/bin/activate
```

2. Installer les dépendances :

```bash
pip install mysql-connector-python bcrypt
```

## Initier la base de données

Lancer le parsing des données de départ :

```bash
python Parsing.py
```

## Lancer l'application

```bash
python Projet.py
```

Une fois lancé, tapez `connect` pour vous inscrire (`register`) ou vous connecter (`login`). Entrez `help` ou laissez la commande vide pour afficher le menu des commandes disponibles.
