#!/bin/bash

# ==============================================================================
# CONFIGURATION & ROBUSTESSE
# ==============================================================================
set -euo pipefail

# Fonction de gestion des erreurs
declencher_erreur() {
    local ligne_erreur=$1
    local code_erreur=$2
    echo -e "\n[ERREUR] Le script de réinitialisation a échoué à la ligne $ligne_erreur."
    exit "$code_erreur"
}

trap 'declencher_erreur $LINENO $?' ERR

FICHIER_ENV=".env"
DOSSIER_VENV="venv"
NOM_BDD="AppDb"

echo "======================================================================"
echo "/!\\ Cette action va supprimer définitivement : /!\\"
echo "  - Le fichier de configuration ($FICHIER_ENV)"
echo "  - L'environnement virtuel Python ($DOSSIER_VENV)"
echo "  - La base de données MariaDB ($NOM_BDD)"
echo "======================================================================"

while true; do
    read -p "Êtes-vous sûr de vouloir tout réinitialiser ? (y/n) : " confirmation
    
    case "$confirmation" in
        [yYoO])
            # L'utilisateur a dit oui, on sort de la boucle et on continue le script
            break
            ;;
        [nN])
            # L'utilisateur a dit non, on affiche un message et on quitte le script immédiatement
            echo "Réinitialisation annulée."
            exit 0
            ;;
        *)
            ;;
    esac
done

# ==============================================================================
# 1. SUPPRESSION DE LA BASE DE DONNÉES
# ==============================================================================
echo -e "\nSuppression de la base de données MariaDB..."

# On tente de charger les identifiants actuels pour supprimer la BDD proprement
if [ -f "$FICHIER_ENV" ]; then
    set -a
    source "$FICHIER_ENV"
    set +a
fi

# Si les variables ne sont pas trouvées dans le .env, on les demande à la volée
if [ -z "${DB_USER:-}" ] || [ -z "${DB_PASS:-}" ]; then
    echo "Identifiants non trouvés dans le fichier .env."
    read -p "Entrez le nom d'utilisateur MariaDB [root] : " username
    DB_USER=${username:-root}
    read -s -p "Entrez le mot de passe MariaDB : " password
    echo ""
    DB_PASS="$password"
fi

# Exécution de la commande DROP DATABASE
if ! mariadb -u "$DB_USER" -p"$DB_PASS" -e "DROP DATABASE IF EXISTS \`$NOM_BDD\`;" 2>/tmp/mariadb_reset_err.log; then
    echo -e "\n[ATTENTION] Impossible de supprimer la base de données via l'outil en ligne."
    echo "Détail de l'erreur :"
    cat /tmp/mariadb_reset_err.log
    echo "Vous devrez probablement supprimer la base '$NOM_BDD' manuellement."
else
    echo "La base de données '$NOM_BDD' a été supprimée (si elle existait)."
fi
rm -f /tmp/mariadb_reset_err.log

# ==============================================================================
# 2. NETTOYAGE DES FICHIERS ET DOSSIERS
# ==============================================================================
echo -e "\nNettoyage des fichiers locaux..."

# Suppression du fichier .env
if [ -f "$FICHIER_ENV" ]; then
    rm -f "$FICHIER_ENV"
    echo "  - Fichier $FICHIER_ENV supprimé."
else
    echo "  - Fichier $FICHIER_ENV déjà absent."
fi

# Suppression du dossier venv
if [ -d "$DOSSIER_VENV" ]; then
    # Sécurité : on désactive le venv si le script est lancé depuis un venv actif
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        deactivate 2>/dev/null || true
    fi
    rm -rf "$DOSSIER_VENV"
    echo "  - Dossier $DOSSIER_VENV supprimé."
else
    echo "  - Dossier $DOSSIER_VENV déjà absent."
fi

echo -e "\n[SUCCÈS] L'application a été entièrement réinitialisée."
echo "Vous pouvez relancer './init.sh' pour tout reconfigurer à blanc."