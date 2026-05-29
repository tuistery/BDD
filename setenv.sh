#!/bin/bash

# Configuration stricte pour intercepter les erreurs
set -euo pipefail

FICHIER_ENV=".env"

# 1. On crée le fichier vide
if [ ! -f "$FICHIER_ENV" ]; then
    echo "Fichier $FICHIER_ENV introuvable. Création d'un nouveau fichier..."
fi
> "$FICHIER_ENV"

# 2. Saisie du nom d'utilisateur
read -p "Entrez le nom d'utilisateur MariaDB [root] : " username
DB_USER=${username:-root}
echo "DB_USER=\"$DB_USER\"" >> "$FICHIER_ENV"

# 3. Saisie du mot de passe
read -s -p "Entrez le mot de passe MariaDB : " password
echo "" # Saut de ligne après le mode masqué
DB_PASS="$password"
echo "DB_PASS=\"$DB_PASS\"" >> "$FICHIER_ENV"

# Vérification de la présence des variables d'environnement requises
if [ -z "${DB_USER:-}" ] || [ -z "${DB_PASS:-}" ]; then
    echo -e "\n[ERREUR] Les variables d'environnement DB_USER et/ou DB_PASS ne sont pas définies."
    echo "Veuillez vérifier votre fichier .env ou votre environnement."
    exit 1
fi

echo -e "\n[SUCCÈS] Les identifiants ont été réinitialisés avec succès !"