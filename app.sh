#!/bin/bash

set -euo pipefail

FICHIER_ENV=".env"

# 1. Chargement des variables d'environnement si le fichier existe
if [ -f "$FICHIER_ENV" ]; then
    set -a
    source "$FICHIER_ENV"
    set +a
else
    echo "[ERREUR] Le fichier $FICHIER_ENV est introuvable. Veuillez d'abord initialiser vos identifiants."
    exit 1
fi

# 2. Utiliser l'environnement virtuel
if [ -d "venv" ]; then
    source venv/bin/activate
else 
    echo "[ERREUR] L'environnement virtuel est introuvable ou manquant."
    exit 1
fi

# 3. Vérification de la présence des variables requises
if [ -z "${DB_USER:-}" ] || [ -z "${DB_PASS:-}" ]; then
    echo "[ERREUR] Les variables DB_USER ou DB_PASS ne sont pas définies dans le fichier $FICHIER_ENV."
    exit 1
fi

echo "  Lancement de main.py..."
# Correction ici : utilisation constante de 'python3' pour éviter les conflits hors du venv
python3 ./src/app/main.py "$DB_USER" "$DB_PASS"