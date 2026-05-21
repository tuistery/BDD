python3 -m venv venv
source venv/bin/activate

mariadb -u enigma -p'Eni@2006' -e "DROP DATABASE IF EXISTS ProjetBdd; CREATE DATABASE ProjetBdd;"
mariadb -u enigma -p'Eni@2006' ProjetBdd < ProjetBdd.sql

python3 Parsing.py

python Projet.py
