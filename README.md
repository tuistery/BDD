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

```bash
pip install mysql-connector-python bcrypt
```

### Configuration de la base de données

Créez une base de données MySQL nommée `ProjetBdd` avec les tables suivantes :

#### Tables principales
- `User` : Utilisateurs (UID, UName, Pass, Email, RegistrationDate, Points, Xp, Title)
- `Course` : Cours (Mnemonic, Name, Faculty)
- `Summary` : Résumés (SID, AuthorID, Course, PublicationDate, Title, Description, Version, Visibility)
- `Note` : Évaluations (NID, UID, SID, Note, Comment)
- `Object` : Objets de la boutique (OID, Name, Price)
- `Title` : Titres cosmétiques (OID, Label)
- `Badge` : Badges (OID, Symbol)
- `Inventory` : Inventaires utilisateurs (OID, OwnerID, Quantity, isActive)
- `Action` : Actions récompensées (Description, CoinGain, XpGain)
- `Transaction` : Historique (TID, Description, UID, Amount, Date)

## 🚀 Installation

1. **Cloner le projet**
```bash
git clone [votre-repo]
cd studyshare
```

2. **Configurer la connexion MySQL**
```python
connection = mysql.connector.connect(
    host='localhost',
    database='ProjetBdd',
    user='votre_utilisateur',
    password='votre_mot_de_passe'
)
```

3. **Lancer l'application**
```bash
python main.py
```

## 📖 Guide d'utilisation

### Menu principal (non connecté)
```
- connect : Se connecter ou s'inscrire
- exit    : Quitter l'application
```

### Menu utilisateur (connecté)

#### Utilisateur
- `profil` : Voir votre profil (points, XP, titre, badge actif)
- `historique` : Consulter vos transactions
- `classement` : Voir le leaderboard

#### Cours & Résumés
- `list` : Lister tous les cours
- `ajouter` : Ajouter un nouveau cours
- `publier` : Publier un résumé
- `get` : Voir les résumés publics d'un cours
- `get mine` : Voir vos résumés d'un cours
- `note` : Noter un résumé
- `modifier_resume` : Modifier un de vos résumés
- `supprimer_resume` : Supprimer un de vos résumés

#### Boutique
- `boutique` : Voir et acheter des objets
- `inventaire` : Voir vos objets possédés
- `activer_titre` : Activer un titre possédé
- `activer_badge` : Activer un badge possédé

### Exemple d'utilisation

```
1. Inscription
   > connect
   > register
   Email: etudiant@universite.be
   Username: EtudiantPro
   Password: ********

2. Ajouter un cours
   > ajouter
   Mnemonic: INFO-F101
   Name: Programmation
   Faculty: Sciences
   Credits: 5

3. Publier un résumé
   > publier
   Mnemonic: INFO-F101
   Title: Résumé Chapitre 1-3
   Desc: Introduction à la programmation Python
   Visibility: public

4. Consulter et noter
   > get
   Quel cours: INFO-F101
   > note
   SID: 1
   Note: 5
   Comment: Très utile!
```

## 🔒 Sécurité

- **Mots de passe** : Hashage avec bcrypt (salage automatique)
- **Requêtes SQL** : Paramètres préparés pour éviter les injections SQL
- **Transactions atomiques** : Prévention des achats simultanés au-delà du solde

## 📊 Architecture du code

### Classes principales
- **`DataUser`** : Modèle utilisateur avec méthodes d'affichage et de rechargement

### Fonctions principales
- **Authentification** : `register()`, `login()`
- **Cours** : `ajoutCours()`, `getListCours()`, `getCourseByMnemonic()`
- **Résumés** : `publierResumer()`, `consulterResumé()`, `modifierResumer()`, `supprimerResumer()`
- **Évaluations** : `publierNote()`
- **Boutique** : `consulterBoutique()`, `acheterObjet()`
- **Inventaire** : `consulterInventaire()`, `activerTitle()`, `activerBadge()`
- **Social** : `consulterClassement()`, `consulterHistorique()`
- **Récompenses** : `ajoutPoints()`, `ajoutTransaction()`, `getAmount()`

### Utilitaires
- `print_structured_list()` : Affichage tabulaire élégant
- `get_table_length()` : Comptage d'entrées pour ID auto-incrémentés

## 🎨 Affichage

L'application utilise un système d'affichage tabulaire automatique qui s'adapte à la largeur du contenu :

```
=== Liste des cours ===
Mnemonic | Name           | Faculty  
---------+----------------+----------
INFO-F101| Programmation  | Sciences 
MATH-F101| Analyse        | Sciences 
```

## 🐛 Gestion des erreurs

- Validation des entrées utilisateur
- Gestion des exceptions MySQL
- Rollback automatique en cas d'échec de transaction
- Messages d'erreur explicites

## 🔮 Améliorations futures

- [ ] Interface graphique (GUI)
- [ ] Recherche avancée de résumés
- [ ] Système de tags pour les résumés
- [ ] Notifications de nouveaux résumés
- [ ] Export PDF des résumés
- [ ] Statistiques détaillées par utilisateur
- [ ] Système de badges automatiques (achievements)

## 👥 Contributeurs

Projet développé dans le cadre d'un cours de bases de données.

## 📄 Licence

[À spécifier]

---

💡 **Astuce** : Contribuez régulièrement en publiant des résumés de qualité et en évaluant ceux des autres pour grimper dans le classement !

