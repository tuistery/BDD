# Marche a suivre

## Prérequis

- Python 3.x
- MySQL en cours d'exécution en local

## Initier la base de données

Lancer toutes les commandes depuis la racine du projet.

Pour (ré)initialiser l'application :
```bash
./init.sh
```
Le script lancera l'application automatiquement

## Lancer l'application

```bash
python Projet.py mariadb_username mariadb_password
```

Une fois lancé, tapez `connect` pour vous inscrire (`register`) ou vous connecter (`login`). Entrez `help` ou laissez la commande vide pour afficher le menu des commandes disponibles.

## 🎯 Vue d'ensemble

StudyShare est une plateforme communautaire qui permet aux étudiants de :
- 📝 Publier et partager des résumés de cours
- ⭐ Évaluer et commenter les résumés des autres
- 🏆 Gagner des points et de l'expérience via des actions
- 🛍️ Acheter des titres et badges cosmétiques
- 📊 Consulter un classement global des contributeurs

## ✨ Fonctionnalités principales

### 👤 Gestion des utilisateurs
- **Inscription sécurisée** : Mots de passe hashés avec bcrypt
- **Système de connexion** : Authentification par username/password
- **Profil personnalisable** : Titres et badges activables
- **Progression** : Points et expérience (XP)

### 📖 Gestion des cours et résumés
- Ajout de nouveaux cours (mnémonique, nom, faculté, crédits)
- Publication de résumés (publics ou privés)
- Consultation des résumés par cours
- Modification et suppression de vos propres résumés
- Système de notation avec commentaires

### 🎮 Système de récompenses

#### Actions récompensées
| Action | Points | XP |
|--------|--------|-----|
| Inscription | Variables selon configuration BDD |
| Publication de résumé | " |
| Évaluation de résumé | " |
| Achat de titre | " |

#### Boutique virtuelle
- Titres cosmétiques (affichés à côté du pseudo)
- Badges avec symboles (visibles sur le profil)
- Achat avec les points gagnés
- Activation/désactivation des objets possédés

### 📊 Fonctionnalités sociales
- **Classement global** : Tri par points, puis XP, puis nom
- **Historique des transactions** : Suivi de toutes vos actions récompensées
- **Inventaire personnel** : Gestion de vos objets cosmétiques

## 🛠️ Technologies utilisées

- **Python 3.x**
- **MySQL** : Base de données relationnelle
- **mysql-connector-python** : Interface Python-MySQL
- **bcrypt** : Hashage sécurisé des mots de passe

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