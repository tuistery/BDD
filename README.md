## 📋 Prérequis

- Python 3.x
- MySQL en cours d'exécution en local

## 🚀 Utilisation

## Initialiser l'application

Lancer toutes les commandes depuis la racine du projet.

Pour (ré)initialiser les données de l'application :
```bash
./init.sh
```
Le script lancera l'application automatiquement.

## Configurer la connexion MariaDB

Pour choisir un nouveau nom d'utilisateur et mot de passe :
```bash
./setenv.sh
```

## Lancer l'application

Pour lancer l'application déjà initialisée :
```bash
./app.sh
```

Une fois lancé, tapez `inscription` pour vous inscrire ou `connexion` pour vous connecter. Une fois connecté, vous pouvez vous déconnecter avec la commande `deconnexion`. Vous pouvez quitter l'application à tout moment avec `quitter`.

## Reset l'application

Pour supprimer la base de données ainsi que toutes les données liées à l'application, dont la connexion MariaDB et l'environnement virtuel, tapez la commande suivante :
```bash
./reset.sh
 ```