import csv
import json
import xml.etree.ElementTree as ET
import mysql.connector
import sys

COMMENTS_PATH = "./data/commentaires.json"
COURSES_PATH = "./data/cours.csv"
REWARDS_PATH = "./data/recompenses.xml"
USERS_PATH = "./data/utilisateurs.xml"
PDF_PATH = "./data/placeholder.pdf"

connection = mysql.connector.connect(
    host='localhost',
    database='AppDb',
    user=sys.argv[1],
    password=sys.argv[2]
)


def parse_courses() -> None:
    cursor = connection.cursor()
    with open(COURSES_PATH, newline='', encoding='utf-8') as f:
        for course in csv.DictReader(f):
            cursor.execute(
                "INSERT IGNORE INTO Course (Mnemonic, Name, Credits, Faculty) VALUES (%s, %s, %s, %s)",
                (course['code_cours'], course['nom'], int(course['credits']), course['faculte'])
            )
    connection.commit()
    cursor.close()


def parse_rewards() -> None:
    cursor = connection.cursor()
    for reward in ET.parse(REWARDS_PATH).getroot().findall('objet'):
        object_id = reward.get('id')
        name = reward.find('nom').text
        type = reward.find('type').text
        desc = reward.find('description').text
        price = float(reward.find('prix').text)
        cursor.execute(
            "INSERT IGNORE INTO Object (OID, Price, Name, Description) VALUES (%s, %s, %s, %s)",
            (object_id, price, name, desc)
        )
        if type == 'badge':
            cursor.execute("INSERT IGNORE INTO Badge (OID, Symbol) VALUES (%s, %s)", (object_id, name))
        elif type == 'titre':
            cursor.execute("INSERT IGNORE INTO Title (OID, Label) VALUES (%s, %s)", (object_id, name))
        elif type in ('thème', 'theme'):
            cursor.execute("INSERT IGNORE INTO Theme (OID, Colors) VALUES (%s, %s)", (object_id, name))
    connection.commit()
    cursor.close()


def parse_users() -> None:
    cursor = connection.cursor()
    summary_counter = 0
    with open(PDF_PATH, 'rb') as f:
        file_content = f.read()

    for user in ET.parse(USERS_PATH).getroot().findall('utilisateur'):
        user_id = user.get('id')
        username = user.find('nomUtilisateur').text
        email = user.find('email').text
        reg_date = user.find('dateInscription').text
        points = int(user.find('points').text or 0)
        title = user.find('titreActif').text
        cursor.execute(
            "INSERT IGNORE INTO User (UID, UName, Pass, Email, RegistrationDate, Points, Xp, Title) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, username, '', email, reg_date, points, 0, title)
        )
        for summary in user.findall('resumes/resume'):
            summary_counter += 1
            file_name = f"{user_id}_{summary_counter}.pdf"
            cursor.execute(
                "INSERT IGNORE INTO File (SID, Name, Size, Content) VALUES (%s, %s, %s, %s)",
                (summary_counter, file_name, len(file_content), file_content)
            )
            cursor.execute(
                "INSERT IGNORE INTO Summary (SID, AuthorID, Course, PublicationDate, Title, Version, Visibility) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (summary_counter, user_id, summary.find('cours').text, summary.find('datePublication').text, summary.find('titre').text, '1.0', 'public')
            )
        for purchase in user.findall('achats/objet'):
            cursor.execute(
                "INSERT IGNORE INTO Owns (UID, OID) SELECT OID, %s FROM Object WHERE Name = %s",
                (user_id, purchase.text)
            )
    connection.commit()
    cursor.close()


def parse_comments() -> None:
    cursor = connection.cursor()
    with open(COMMENTS_PATH, encoding='utf-8') as f:
        for entry in json.load(f)['evaluations']:
            rate = entry['note']
            comment = entry['commentaire']
            course = entry['resume']['cours']
            title = entry['resume']['titre']
            author = entry['auteur']

            cursor.execute("SELECT UID FROM User WHERE UName = %s", (author,))
            uid_row = cursor.fetchone()

            cursor.execute("SELECT SID FROM Summary WHERE Course = %s AND Title = %s", (course, title))
            sid_row = cursor.fetchone()

            if not uid_row or not sid_row:
                continue

            cursor.execute(
                "INSERT IGNORE INTO Rates (UID, SID, Note, Comment) VALUES (%s, %s, %s, %s)",
                (uid_row[0], sid_row[0], rate, comment)
            )
    connection.commit()
    cursor.close()


if __name__ == "__main__":
    parse_courses()
    parse_rewards()
    parse_users()
    parse_comments()
    connection.close()
