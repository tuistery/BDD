import mysql.connector
import os
from datetime import date, datetime

from config import connection, ACTION_PUBLISH_SUMMARY, ACTION_RATE_SUMMARY
from helpers import execute_select, execute_select_one, execute_write, execute_write_reuse_id
from users import add_points


def publish_summary(author_id: int, mnemonic: str, title: str, desc: str, file_path: str, visibility="private") -> bool:
    if not connection.is_connected():
        return False
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
    except Exception as e:
        print(f"Impossible de lire le fichier : {e}")
        return False
    
    cursor = connection.cursor()

    query = "INSERT INTO Summary (AuthorID, Course, PublicationDate, Title, Description, Version, Visibility) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    params = (author_id, mnemonic, date.today(), title, desc, "1.0", visibility)

    file_query = "INSERT INTO Files (SID, Name, Size, Content) VALUES (%s, %s, %s, %s)"
    file_name = f"{author_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_params = (file_name, len(file_content), file_content)
    if execute_write_reuse_id(main_query=query, main_param=params, query1=file_query, param1=file_params) != -2 :
        print(f"Résumé avec le titre : {title} a été enregistré pour le cours {mnemonic} avec succès !")
        return True

def get_course_summaries(mnemonic: str, author_id=-1) -> list[dict]:
    if author_id == -1:
        query = "SELECT * FROM Summary WHERE Course = %s AND Visibility = 'public'"
        params = (mnemonic,)
    else:
        query = "SELECT * FROM Summary WHERE Course = %s AND AuthorID = %s"
        params = (mnemonic, author_id)
    return execute_select(query, params)

def rate_summary(user_id: int, summary_id: int, rating: int, comment: str) -> None:
    is_own = execute_select_one("SELECT SID FROM Summary WHERE SID = %s AND AuthorID = %s", (summary_id, user_id))
    if is_own:
        print("Vous ne pouvez pas noter votre propre résumé.")
        return
    already_rated = execute_select_one("SELECT UID, SID FROM Notes WHERE UID = %s AND SID = %s", (user_id, summary_id))
    if already_rated:
        print("Vous avez déjà noté ce résumé.")
        return
    query = "INSERT INTO Notes (UID, SID, Note, Comment) VALUES (%s, %s, %s, %s)"
    params = (user_id, summary_id, rating, comment)
    if execute_write(query1=query, param1=params) != -2:
        print(f"Note {rating} publiée avec succès !")
        add_points(ACTION_RATE_SUMMARY, user_id)

def get_own_summaries(author_id: int) -> list[dict]:
    query = """
        SELECT *
        FROM Summary
        WHERE AuthorID = %s
        ORDER BY PublicationDate DESC
    """
    return execute_select(query, (author_id,))

def update_summary(summary_id: int, author_id: int, new_title: str, new_desc: str) -> bool:
    query = """
        UPDATE Summary
        SET Title = %s, Description = %s
        WHERE SID = %s AND AuthorID = %s
    """
    params = (new_title, new_desc, summary_id, author_id)
    row_count = execute_write(query1=query, param1=params)
    if row_count == -2:
        return False
    elif row_count == 0:
        print("Résumé introuvable ou vous n'êtes pas l'auteur.")
        return False
    else:
        print(f"Résumé {summary_id} modifié avec succès !")
        return True

def delete_summary(summary_id: int, author_id: int) -> bool:
    query = "DELETE FROM Summary WHERE SID = %s AND AuthorID = %s"
    params = (summary_id, author_id)
    if execute_write(query1=query, param1=params) != -2:
        print(f"Résumé {summary_id} supprimé avec succès !")
        return True
    return False

def download_summary(summary_id: int, user_id: int, download_path: str) -> None:
    query = """
        SELECT f.Name, f.Content
        FROM Files f, Summary s
        WHERE f.SID = %s AND s.SID = %s AND (s.AuthorID = %s OR s.Visibility = 'public' OR s.Visibility = 'restricted')
    """
    params = (summary_id, summary_id, user_id)
    file_data = execute_select_one(query, params)
    if file_data is None:
        print("Vous n'avez pas accès à ce résumé.")
        return
    if download_path == "":
        download_path = file_data['Name']
    elif not os.path.isdir(download_path):
        print(f"Dossier inexistant : {download_path}")
        return
    else:
        download_path = os.path.join(download_path, file_data['Name'])
    try:
        with open(download_path, 'wb') as f:
            f.write(file_data['Content'])
    except Exception as e:
        print(f"Impossible d'écrire dans ce dossier : {e}")
        return
    print(f"Fichier enregistré sur {download_path}")

def get_top_rated_summaries() -> list[dict]:
    query = """
        SELECT c.Mnemonic, c.Name AS CourseName,
            s.SID, s.Title AS SummaryTitle,
            avg_notes.AverageNote
        FROM Course c
        JOIN Summary s ON c.Mnemonic = s.Course
        JOIN (SELECT SID, AVG(Note) AS AverageNote
              FROM Notes
              GROUP BY SID) AS avg_notes ON s.SID = avg_notes.SID
        JOIN (SELECT s2.Course, MAX(avg_note) AS max_avg
              FROM (SELECT s2.SID, s2.Course, AVG(n2.Note) AS avg_note
                    FROM Summary s2
                    JOIN Notes n2 ON s2.SID = n2.SID
                    GROUP BY s2.SID, s2.Course) AS s2
              GROUP BY s2.Course) AS course_max ON s.Course = course_max.Course
                AND avg_notes.AverageNote = course_max.max_avg
        ORDER BY c.Mnemonic
    """
    return execute_select(query)

def get_top_course() -> dict | None:
    query = """
        SELECT Course, COUNT(*) as nb_resumes
        FROM Summary
        GROUP BY Course
        ORDER BY nb_resumes DESC LIMIT 1
    """
    return execute_select_one(query)

def get_average_summary_per_user() -> dict | None:
    query = """
        SELECT AVG(nb_resumes) as avg_summaries
        FROM (SELECT AuthorID, COUNT(*) as nb_resumes
              FROM Summary
              GROUP BY AuthorID) as resume_par_user
    """
    return execute_select_one(query)
