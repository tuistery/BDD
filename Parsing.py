import csv
import json
import xml.etree.ElementTree as ET
import mysql.connector

COMMENTAIRES_PATH = "./data/commentaires.json"
COURS_PATH = "./data/cours.csv"
RECOMPENSES_PATH = "./data/recompenses.xml"
UTILISATEURS_PATH = "./data/utilisateurs.xml"

connection = mysql.connector.connect(
    host='localhost',
    database='ProjetBdd',
    user='enigma',
    password='Eni@2006'
)


def parse_cours():
    cursor = connection.cursor()
    with open(COURS_PATH, newline='', encoding='utf-8') as f:
        for cours in csv.DictReader(f):
            cursor.execute(
                "INSERT IGNORE INTO Course (Mnemonic, Name, Credits, Faculty) VALUES (%s, %s, %s, %s)",
                (cours['code_cours'], cours['nom'], int(cours['credits']), cours['faculte'])
            )
    connection.commit()
    cursor.close()


def parse_recompenses():
    cursor = connection.cursor()
    for objet in ET.parse(RECOMPENSES_PATH).getroot().findall('objet'):
        oid = objet.get('id')
        nom = objet.find('nom').text
        typ = objet.find('type').text
        desc = objet.find('description').text
        prix = float(objet.find('prix').text)
        cursor.execute(
            "INSERT IGNORE INTO Object (OID, Price, Name, Description) VALUES (%s, %s, %s, %s)",
            (oid, prix, nom, desc)
        )
        if typ == 'badge':
            cursor.execute("INSERT IGNORE INTO Badge (OID, Symbol) VALUES (%s, %s)", (oid, nom))
        elif typ == 'titre':
            cursor.execute("INSERT IGNORE INTO Title (OID, Label) VALUES (%s, %s)", (oid, nom))
        elif typ in ('thème', 'theme'):
            cursor.execute("INSERT IGNORE INTO Theme (OID, Colors) VALUES (%s, %s)", (oid, nom))
    connection.commit()
    cursor.close()


def parse_utilisateurs():
    cursor = connection.cursor()
    summary_counter = 0
    for user in ET.parse(UTILISATEURS_PATH).getroot().findall('utilisateur'):
        uid = user.get('id')
        uname = user.find('nomUtilisateur').text
        email = user.find('email').text
        reg_date = user.find('dateInscription').text
        points = int(user.find('points').text or 0)
        titre = user.find('titreActif').text
        cursor.execute(
            "INSERT IGNORE INTO User (UID, UName, Pass, Email, RegistrationDate, Points, Xp, Title) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (uid, uname, '', email, reg_date, points, 0, titre)
        )
        for resume in user.findall('resumes/resume'):
            summary_counter += 1
            cursor.execute(
                "INSERT IGNORE INTO Summary (SID, AuthorID, Course, PublicationDate, Title, Version, Visibility) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (summary_counter, uid, resume.find('cours').text, resume.find('datePublication').text, resume.find('titre').text, '1.0', 'public')
            )
        for achat in user.findall('achats/objet'):
            cursor.execute(
                "INSERT IGNORE INTO Inventory (OID, OwnerID) SELECT OID, %s FROM Object WHERE Name = %s",
                (uid, achat.text)
            )
    connection.commit()
    cursor.close()


def parse_commentaires():
    cursor = connection.cursor()
    with open(COMMENTAIRES_PATH, encoding='utf-8') as f:
        for idx, evaluation in enumerate(json.load(f)['evaluations'], start=1):
            note = evaluation['note']
            comment = evaluation['commentaire']
            cours = evaluation['resume']['cours']
            titre = evaluation['resume']['titre']
            auteur = evaluation['auteur']

            cursor.execute("SELECT UID FROM User WHERE UName = %s", (auteur,))
            uid_row = cursor.fetchone()

            cursor.execute("SELECT SID FROM Summary WHERE Course = %s AND Title = %s", (cours, titre))
            sid_row = cursor.fetchone()

            if not uid_row or not sid_row:
                continue

            cursor.execute(
                "INSERT IGNORE INTO Notes (NID, UID, SID, Note, Comment) VALUES (%s, %s, %s, %s, %s)",
                (str(idx), uid_row[0], sid_row[0], note, comment)
            )
    connection.commit()
    cursor.close()


if __name__ == "__main__":
    parse_cours()
    parse_recompenses()
    parse_utilisateurs()
    parse_commentaires()
    connection.close()
