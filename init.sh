#!/bin/bash

# ==============================================================================
# CONFIGURATION & ROBUSTESSE
# ==============================================================================
# -e : Arrête le script immédiatement si une commande échoue
# -u : Provoque une erreur si une variable non définie est utilisée
# -o pipefail : Protège les erreurs masquées dans les pipelines
set -euo pipefail

set -a
source .env
set +a
# Fonction de nettoyage et de gestion des erreurs
declencher_erreur() {
    local ligne_erreur=$1
    local code_erreur=$2
    echo -e "\n[ERREUR] Le script a échoué à la ligne $ligne_erreur avec le code de retour $code_erreur."
    exit "$code_erreur"
}

# Associer le signal ERR à notre fonction
trap 'declencher_erreur $LINENO $?' ERR

# ==============================================================================
# 1. ENVIRONNEMENT VIRTUEL PYTHON
# ==============================================================================
echo "Configuration de l'environnement Python..."

# Créer le venv s'il n'existe pas déjà
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Mettre à jour pip et installer les dépendances proprement
pip install --upgrade pip --quiet
pip install mysql-connector-python bcrypt --quiet

# ==============================================================================
# 2. SAISIE DES IDENTIFIANTS (SÉCURISÉE)
# ==============================================================================
echo -e "\nConnexion à la base de données :"

# Saisie du nom d'utilisateur (avec une valeur par défaut 'root' pour aller vite)
#read -p "  Nom d'utilisateur MariaDB [root] : " username
#username=${username:-root}

# Saisie du mot de passe masquée (-s)
#read -s -p "  Mot de passe : " password
#echo "" # Saut de ligne requis après un read -s

# ==============================================================================
# 3. BASE DE DONNÉES MARIADB
# ==============================================================================
echo -e "\nImportation du fichier SQL..."

if [ ! -f "ProjetBdd.sql" ]; then
    echo "Erreur : Le fichier 'ProjetBdd.sql' est introuvable dans le dossier courant."
    exit 1
fi

# Utilisation de MYSQL_PWD pour éviter de passer le mot de passe en clair dans les processus
#export MYSQL_PWD="$password"

# Exécution de l'import (on ajoute -v pour un retour visuel si besoin, ou on laisse tel quel)
mariadb -u "$DB_USER" < ProjetBdd.sql

# Nettoyage de la variable d'environnement par sécurité
#unset MYSQL_PWD

echo "Base de données initialisée avec succès."

# ==============================================================================
# 4. EXÉCUTION DES SCRIPTS PYTHON
# ==============================================================================
echo -e "\nExécution des scripts Python..."

# On s'assure que les fichiers Python existent avant de les lancer
if [ ! -f "parsing.py" ] || [ ! -f "main.py" ]; then
    echo "Erreur : 'parsing.py' ou 'main.py' manquant."
    exit 1
fi

echo "  Lancement de parsing.py..."
python3 parsing.py "$DB_USER" "$DB_PASS"

echo "  Lancement de main.py..."
# Correction ici : utilisation constante de 'python3' pour éviter les conflits hors du venv
python3 main.py "$DB_USER" "$DB_PASS"