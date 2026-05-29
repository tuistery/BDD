#!/bin/bash

# ==============================================================================
# CONFIGURATION & ROBUSTESSE
# ==============================================================================
# -e : Arrête le script immédiatement si une commande échoue
# -u : Provoque une erreur si une variable non définie est utilisée
# -o pipefail : Protège les erreurs masquées dans les pipelines
set -euo pipefail

# Fonction de nettoyage et de gestion des erreurs
declencher_erreur() {
    local ligne_erreur=$1
    local code_erreur=$2
    echo -e "\n[ERREUR] Le script a échoué à la ligne $ligne_erreur avec le code de retour $code_erreur."
    exit "$code_erreur"
}

trap 'declencher_erreur $LINENO $?' ERR

FICHIER_ENV=".env"

# 1. Si le fichier .env n'existe pas, on le crée vide pour pouvoir y écrire
if [ ! -f "$FICHIER_ENV" ]; then
    echo "Fichier $FICHIER_ENV introuvable. Création d'un nouveau fichier..."
    touch "$FICHIER_ENV"
else
    # S'il existe, on charge les variables existantes
    set -a
    source "$FICHIER_ENV"
    set +a
fi

# 2. Vérification / Saisie du nom d'utilisateur
if [ -z "${DB_USER:-}" ]; then
    read -p "Entrez le nom d'utilisateur MariaDB [root] : " username
    DB_USER=${username:-root}
    echo "DB_USER=\"$DB_USER\"" >> "$FICHIER_ENV"
fi

# 3. Vérification / Saisie du mot de passe
if [ -z "${DB_PASS:-}" ]; then
    read -s -p "Entrez le mot de passe MariaDB : " password
    echo "" # Saut de ligne après le mode masqué
    DB_PASS="$password"
    echo "DB_PASS=\"$DB_PASS\"" >> "$FICHIER_ENV"
fi

# Vérification de la présence des variables d'environnement requises
if [ -z "${DB_USER:-}" ] || [ -z "${DB_PASS:-}" ]; then
    echo -e "\n[ERREUR] Les variables d'environnement DB_USER et/ou DB_PASS ne sont pas définies."
    echo "Veuillez vérifier votre fichier .env ou votre environnement."
    exit 1
fi

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
# 2. BASE DE DONNÉES MARIADB
# ==============================================================================
echo -e "\nImportation du fichier SQL..."
if [ ! -f "./src/ddl.sql" ]; then
    echo "Erreur : Le fichier 'ddl.sql' est introuvable ou manquant"
    exit 1
fi

echo -e "\nConnexion à la base de données :"
# Exécution de l'import avec gestion spécifique de l'erreur d'authentification
if ! mariadb -u "$DB_USER" -p"$DB_PASS" < ./src/ddl.sql 2>/tmp/mariadb_err.log; then
    echo -e "\n[ERREUR] Impossible de se connecter à MariaDB."
    echo "Veuillez vérifier que le nom d'utilisateur '$DB_USER' et le mot de passe sont corrects."
    echo "Détail de l'erreur :"
    cat /tmp/mariadb_err.log
    rm -f /tmp/mariadb_err.log
    exit 1
fi
rm -f /tmp/mariadb_err.log
echo "Base de données initialisée avec succès."

# ==============================================================================
# 3. EXÉCUTION DES SCRIPTS PYTHON
# ==============================================================================
echo -e "\nExécution des scripts Python..."

# On s'assure que les fichiers Python existent avant de les lancer
if [ ! -f "./src/parsing.py" ] || [ ! -f "./src/app/main.py" ]; then
    echo "Erreur : 'parsing.py' ou 'main.py' manquant ou introuvable."
    exit 1
fi

echo "  Lancement de parsing.py..."
python3 ./src/parsing.py "$DB_USER" "$DB_PASS"

echo "  Lancement de main.py..."
python3 ./src/app/main.py "$DB_USER" "$DB_PASS"