set -a
source .env
set +a

echo "  Lancement de main.py..."
# Correction ici : utilisation constante de 'python3' pour éviter les conflits hors du venv
python3 main.py "$DB_USER" "$DB_PASS"