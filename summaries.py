import mysql.connector
import os
from datetime import date, datetime

from db import connection, ACTION_PUBLISH_SUMMARY, ACTION_RATE_SUMMARY
from helpers import execute_select, execute_select_one, execute_write, get_next_id
from users import add_points


def publish_summary(author_id: int, mnemonic: str, title: str, desc: str, file_path: str, visibility="private") -> bool:
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)

        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
        except Exception as e:
            print(f"Impossible de lire le fichier : {e}")
            return False

        file_query = "INSERT INTO Files (Name, Size, Content) VALUES (%s, %s, %s)"
        file_name = f"{author_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_params = (file_name, len(file_content), file_content)

        query = "INSERT INTO Summary (SID, AuthorID, FileID, Course, PublicationDate, Title, Description, Version, Visibility) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(file_query, file_params)
            file_id = cursor.lastrowid
            params = (get_next_id("Summary", "SID"), author_id, file_id, mnemonic, date.today(), title, desc, "1.0", visibility)
            cursor.execute(query, params)
            connection.commit()
            print(f"Résumé avec le titre : {title} a été enregistré pour le cours {mnemonic} avec succès !")
            add_points(ACTION_PUBLISH_SUMMARY, author_id)
            return True
        except mysql.connector.Error as err:
            print(f"Erreur d'insertion : {err}")
            return False
        finally:
            cursor.close()


def get_course_summaries(mnemonic: str, author_id=-1) -> list[dict]:
    if author_id == -1:
        query = "SELECT * FROM Summary WHERE Course = %s AND Visibility = 'public'"
        params = (mnemonic,)
    else:
        query = "SELECT * FROM Summary WHERE Course = %s AND AuthorID = %s"
        params = (mnemonic, author_id)
    return execute_select(query, params)


def rate_summary(user_id: int, summary_id: int, rating: int, comment: str) -> None:
    query = "INSERT INTO Notes (NID, UID, SID, Note, Comment) VALUES (%s, %s, %s, %s, %s)"
    params = (get_next_id("Notes", "NID"), user_id, summary_id, rating, comment)
    if execute_write(query, params) != -1:
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
    row_count = execute_write(query, params)
    if row_count == -1:
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
    if execute_write(query, params) != -1:
        print(f"Résumé {summary_id} supprimé avec succès !")
        return True
    return False


def download_summary(summary_id: int, user_id: int, download_path: str) -> None:
    query = """
        SELECT f.Name, f.Content
        FROM Files f, Summary s
        WHERE s.FileID=f.FID AND s.SID=%s AND (s.AuthorID=%s OR s.Visibility='public' OR s.Visibility='restricted')
    """
    params = (summary_id, user_id)
    file_data = execute_select_one(query, params)
    if file_data is None:
        print("Vous n'avez pas accès à ce fichier ou le fichier est inexistant")
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
