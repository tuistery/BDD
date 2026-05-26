import mysql.connector
from datetime import date, datetime
import bcrypt
import sys
import os
import getpass

# Connexion globale
connection = mysql.connector.connect(
    host='localhost',
    database='ProjetBdd',
    user=sys.argv[1],
    password=sys.argv[2]
)

# Constantes pour le menu
CMD_CONNECT = "connexion"
CMD_EXIT = "quitter"

CMD_LOGIN = "connecter"
CMD_REGISTER = "inscrire"

CMD_PROFIL = "profil"
CMD_HISTORY = "historique"
CMD_LEADERBOARD = "classement"
CMD_LIST_ACTIVE_USERS = "actifs"
CMD_LIST_INACTIVE_USERS = "inactifs"

CMD_LIST_COURSES = "liste"
CMD_ADD_COURSE = "ajouter"
CMD_PUBLISH = "publier"
CMD_VIEW_COURSE_SUMMARIES = "consulter"
CMD_MY_SUMMARIES = "mes_resumes"
CMD_RATE_SUMMARY = "noter"
CMD_EDIT_SUMMARY = "modifier"
CMD_DELETE_SUMMARY = "supprimer"
CMD_DOWNLOAD_SUMMARY = "telecharger"
CMD_TOP_SUMMARIES = "meilleurs"
CMD_TOP_COURSE = "top_cours"
CMD_AVG_SUMMARIES_PER_USER = "moyenne"

CMD_SHOP = "boutique"
CMD_INVENTORY = "inventaire"
CMD_TOP_ITEM = "top_objet"
CMD_ACTIVATE_TITLE = "activer_titre"
CMD_ACTIVATE_BADGE = "activer_badge"
CMD_HIGH_SPENDERS = "gros_depensiers"

# Libellés d'actions (doivent correspondre exactement à la table Action)
ACTION_PUBLISH_SUMMARY = "Publication d’un résumé"
ACTION_RATE_SUMMARY = "Évaluation d’un résumé"
ACTION_REGISTER = "Inscription sur la plateforme"
ACTION_BUY_TITLE = "Achat d’un titre cosmétique"

def print_structured_list(items, title="Résultats"):
    """Affiche proprement une liste de dictionnaires sous forme de tableau."""
    print(f"\n=== {title} ===")

    if not items:
        print("Aucun résultat.")
        return

    if not isinstance(items, list):
        print(items)
        return

    if not all(isinstance(item, dict) for item in items):
        for idx, item in enumerate(items, start=1):
            print(f"{idx:>2}. {item}")
        return

    columns = []
    for row in items:
        for key in row.keys():
            if key not in columns:
                columns.append(key)

    widths = {col: len(str(col)) for col in columns}
    for row in items:
        for col in columns:
            value = "" if row.get(col) is None else str(row.get(col))
            widths[col] = max(widths[col], len(value))

    header = " | ".join(f"{col:<{widths[col]}}" for col in columns)
    separator = "-+-".join("-" * widths[col] for col in columns)
    print(header)
    print(separator)

    for row in items:
        line = " | ".join(
            f"{('' if row.get(col) is None else str(row.get(col))):<{widths[col]}}"
            for col in columns
        )
        print(line)

def get_next_id(table, column):
    cursor = connection.cursor()
    query = f"SELECT COALESCE(MAX({column}), 0) + 1 FROM {table}"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    return result[0]

def execute_select(query: str, params: tuple=None) -> list[dict]:
    if not connection.is_connected():
        return []
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
        return []
    finally:
        cursor.close()

def execute_select_one(query: str, params: tuple=None) -> dict | None:
    if not connection.is_connected():
        return None
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
        return None
    finally:
        cursor.close()

def execute_write(query: str, params: tuple=None) -> int:
    if not connection.is_connected():
        return -1
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        connection.commit()
        return cursor.rowcount
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Erreur : {err}")
        return -1
    finally:
        cursor.close()

class DataUser:
    def __init__(self, username: str, password: str, email: str, date_="2026-04-03", points=0, xp=0, title="Null", user_id=-1):
        if user_id == -1:
            self.user_id = get_next_id("User", "UID")
        else:
            self.user_id = user_id
            
        self.username = username
        self.email = email
        self.password = password
        self.date_ = date_
        self.points = points
        self.xp = xp
        self.title = title

    def get_email(self) -> str: return self.email
    def get_username(self) -> str: return self.username
    def get_points(self): return self.points
    def get_xp(self): return self.xp
    def get_title(self) -> str: return self.title
    def get_id(self) -> int: return self.user_id
    def display_info(self):
        """Affiche les informations principales de l'utilisateur"""
        print(f"Utilisateur: {self.username}")
        print(f"Points: {self.points}")
        print(f"Titre: {self.title}")
        print(f"XP: {self.xp}")
    
    def reload_user(self) -> None:
        query = "SELECT Points, Xp, Title FROM User WHERE UID = %s"
        result = execute_select_one(query, (self.get_id(),))
        if result:
            self.points = result["Points"]
            self.xp = result["Xp"]
            self.title = result["Title"]
    
    # Méthode __str__ pour print() direct
    def __str__(self):
        """Retourne une représentation string de l'utilisateur"""
        query = """
            SELECT RankLevel
            FROM Levels
            WHERE XpRequired <= %s
            ORDER BY XpRequired DESC
            LIMIT 1;
        """
        level_row = execute_select_one(query, (self.xp,))["RankLevel"]
        return f"Utilisateur: {self.username} | Points: {self.points} | Titre: {self.title} | XP: {self.xp} | Niveau: {level_row}"
    
    # Méthode __repr__ pour debugging
    def __repr__(self):
        """Retourne une représentation détaillée de l'utilisateur"""
        return f"DataUser(id={self.user_id}, username='{self.username}', points={self.points}, title='{self.title}', Xp={self.xp})"

def get_amount(desc: str) -> int:
    query = "SELECT CoinGain FROM Action WHERE Description = %s"
    result = execute_select_one(query, (desc,))
    if result:
        return result["CoinGain"]
    return 0

def add_transaction(action_type: str, user_id: int, custom_amount: int = None) -> None:
    query = "INSERT INTO Transaction (TID,Description,UID,Amount,Date) VALUES (%s,%s,%s,%s,%s)"
    amount = custom_amount if custom_amount is not None else get_amount(action_type)
    params = (get_next_id("Transaction", "TID"), action_type, user_id, amount, date.today())
    if execute_write(query, params) != -1:
        print(f"Ajout de la transaction de l'utilisateur {user_id} avec succès !")

def add_points(action_type: str, user_id: int, custom_amount: int = None) -> None:
    query = """
        UPDATE User
        SET Xp = Xp + (SELECT XpGain FROM Action WHERE Description = %s),
            Points = Points + (SELECT CoinGain FROM Action WHERE Description = %s)
        WHERE UID = %s
    """
    params = (action_type, action_type, user_id)
    if execute_write(query, params) != -1:
        print(f"Ajout des points et de l'XP a l'utilisateur {user_id} avec succès !")
        add_transaction(action_type, user_id, custom_amount)

def register(username: str, password: str, email: str) -> DataUser | None:
    already_exists = execute_select_one("SELECT UID FROM User WHERE Uname = %s OR Email = %s",
                                        (username, email)
    )
    if already_exists:
        print("Email ou nom d'utilisateur déjà utilisé.")
        return None
    
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    new_user = DataUser(username, hashed, email, date.today())
    query = "INSERT INTO User (UID, UName, Pass, Email, RegistrationDate, Points, Xp, Title) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    params = (new_user.get_id(), new_user.get_username(), new_user.password, new_user.get_email(), new_user.date_, new_user.get_points(), new_user.get_xp(), new_user.get_title())
    if execute_write(query, params) != -1:
        add_points(ACTION_REGISTER, new_user.get_id())
        new_user.reload_user()
        return new_user
    return None

def login(username: str, password: str) -> DataUser | None:
    password = password.encode('utf-8')
    query = "SELECT * FROM User WHERE UName = %s"
    result = execute_select_one(query, (username,)) # Le tuple (valeur,) est important
    if result and bcrypt.checkpw(password, result["Pass"].encode('utf-8')):
        print("Connexion réalisée avec succès")
        return DataUser(
            result["UName"], 
            result["Pass"], 
            result["Email"], 
            result["RegistrationDate"], 
            result["Points"], 
            result["Xp"], 
            result["Title"], 
            result["UID"]
        )
    else:
        print("Identifiant ou mot de passe incorrect.")
        return None

def get_list_courses() -> list[dict]:
    query = "SELECT * FROM Course"
    return execute_select(query)

def get_course_by_mnemonic(mnemonic: str) -> dict | None:
    query = "SELECT Mnemonic FROM Course WHERE Mnemonic = %s"
    return execute_select_one(query, (mnemonic,))

def add_course(mnemonic: str, name: str, faculty: str, credits: int) -> None:
    query = "INSERT INTO Course (Mnemonic,Name,Faculty,Credits) VALUES (%s, %s, %s, %s)"
    params = (mnemonic, name, faculty, credits)
    if execute_write(query, params) != -1:
        print(f"Cours {name} enregistré avec succès !")

def publish_summary(author_id: int, mnemonic: str, title: str, desc:str, file_path:str, visibility = "private") -> bool:
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

def get_course_summaries(mnemonic:str , author_id = -1) -> list[dict]:
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

def get_inventory(user_id: int) -> list[dict]:
    query = "SELECT * FROM Inventory WHERE OwnerID = %s"
    return execute_select(query, (user_id,))

def get_shop_items() -> list[dict]:
    query = "SELECT * FROM Object"
    return execute_select(query)

def get_owned_items(user_id: int) -> list[dict]:
    query = """
        SELECT i.OID, t.Label, i.isActive
        FROM Inventory i
        JOIN Title t ON t.OID = i.OID
        WHERE i.OwnerID = %s
        ORDER BY i.OID
    """
    return execute_select(query, (user_id,))

def get_owned_badges(user_id: int) -> list[dict]:
    query = """
        SELECT i.OID, b.Symbol, o.Name, i.isActive
        FROM Inventory i
        JOIN Badge b ON b.OID = i.OID
        JOIN Object o ON o.OID = i.OID
        WHERE i.OwnerID = %s
        ORDER BY i.OID
    """
    return execute_select(query, (user_id,))

def get_active_badge(user_id: int) -> dict | None:
    query = """
        SELECT b.Symbol, o.Name
        FROM Inventory i
        JOIN Badge b ON b.OID = i.OID
        JOIN Object o ON o.OID = i.OID
        WHERE i.OwnerID = %s AND i.isActive = TRUE
        LIMIT 1
    """
    return execute_select_one(query, (user_id,))

def buy_item(user_id: int, object_id: int) -> bool:
    if not connection.is_connected():
        return False

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT Price, Name FROM Object WHERE OID = %s", (object_id,))
        item = cursor.fetchone()
        if not item:
            print("Objet introuvable.")
            return False

        price = int(float(item["Price"]))
        cursor.execute("SELECT Points FROM User WHERE UID = %s", (user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            print("Utilisateur introuvable.")
            return False

        if user_data["Points"] < price:
            return False

        # Débit atomique pour éviter les achats simultanés au-delà du solde.
        cursor.execute(
            "UPDATE User SET Points = Points - %s WHERE UID = %s AND Points >= %s",
            (price, user_id, price)
        )
        if cursor.rowcount == 0:
            connection.rollback()
            return False
        cursor.execute(
            """
            INSERT INTO Inventory (OID, OwnerID, Quantity)
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE Quantity = Quantity + 1
            """,
            (object_id, user_id)
        )
        connection.commit()
        print(f"Objet '{item['Name']}' acheté pour {price} points.")

        # Récompense XP/coins définie dans la table Action.
        add_points(ACTION_BUY_TITLE, user_id, custom_amount=-price)
        return True
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Erreur de insert : {err}")
        return False
    finally:
        cursor.close()

def activate_title(user_id: int, object_id: int) -> bool:
    if not connection.is_connected():
        return False

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT t.Label
            FROM Inventory i
            JOIN Title t ON t.OID = i.OID
            WHERE i.OwnerID = %s AND i.OID = %s
            """,
            (user_id, object_id)
        )
        title_row = cursor.fetchone()
        if not title_row:
            print("Ce titre n'est pas dans votre inventaire.")
            return False

        cursor.execute(
            """
            UPDATE Inventory i
            JOIN Title t ON t.OID = i.OID
            SET i.isActive = FALSE
            WHERE i.OwnerID = %s
            """,
            (user_id,)
        )
        cursor.execute(
            "UPDATE Inventory SET isActive = TRUE WHERE OwnerID = %s AND OID = %s",
            (user_id, object_id)
        )
        cursor.execute(
            "UPDATE User SET Title = %s WHERE UID = %s",
            (title_row["Label"], user_id)
        )
        connection.commit()
        print(f"Titre activé : {title_row['Label']}")
        return True
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Erreur de update : {err}")
        return False
    finally:
        cursor.close()

def activate_badge(user_id: int, object_id: int) -> bool:
    if not connection.is_connected():
        return False

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT b.Symbol, o.Name
            FROM Inventory i
            JOIN Badge b ON b.OID = i.OID
            JOIN Object o ON o.OID = i.OID
            WHERE i.OwnerID = %s AND i.OID = %s
            """,
            (user_id, object_id)
        )
        badge_row = cursor.fetchone()
        if not badge_row:
            print("Ce badge n'est pas dans votre inventaire.")
            return False

        cursor.execute(
            """
            UPDATE Inventory i
            JOIN Badge b ON b.OID = i.OID
            SET i.isActive = FALSE
            WHERE i.OwnerID = %s
            """,
            (user_id,)
        )
        cursor.execute(
            "UPDATE Inventory SET isActive = TRUE WHERE OwnerID = %s AND OID = %s",
            (user_id, object_id)
        )
        connection.commit()
        print(f"Badge activé : {badge_row['Symbol']} {badge_row['Name']}")
        return True
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Erreur de update : {err}")
        return False
    finally:
        cursor.close()

def get_leaderboard() -> list[dict]:
    query = """
        SELECT UName, Points, Xp, Title
        FROM User
        ORDER BY Points DESC, Xp DESC, UName ASC
        LIMIT 10
    """
    leaderboard = execute_select(query)
    if leaderboard:
        for idx, row in enumerate(leaderboard, start=1):
            row["Rang"] = idx
    return leaderboard

def get_active_users() -> list[dict]:
    query = """
        SELECT UName
        FROM User u
        WHERE (
            SELECT COUNT(DISTINCT Course)
            FROM Summary
            WHERE AuthorID = u.UID
        ) >= 3
    """
    return execute_select(query)

def get_history(user_id: int) -> list[dict]:
    query = """
        SELECT TID, Description, Amount, Date
        FROM Transaction
        WHERE UID = %s
        ORDER BY Date DESC
    """
    return execute_select(query, (user_id,))

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

def get_own_summaries(author_id: int) -> list[dict]:
    query = """
        SELECT * 
        FROM Summary 
        WHERE AuthorID = %s 
        ORDER BY PublicationDate DESC
    """
    return execute_select(query, (author_id,))

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
        with open(download_path, 'wb') as f :
            f.write(file_data['Content'])
    except Exception as e:
        print(f"Impossible d'écrire dans ce dossier : {e}")
        return
    
    print(f"Fichier enregistré sur {download_path}")
 
def show_commands(connected: int) -> None:
    os.system('clear')
    print("\n" + "=" * 64)
    print("                    MENU DES COMMANDES")
    print("=" * 64)
    if connected == 0:
        print("  Session")
        print("   - connexion       : se connecter / s'inscrire")
        print("   - quitter         : quitter l'application")
    else:
        print("  Utilisateur")
        print("   - profil          : voir votre profil")
        print("   - historique      : voir vos transactions")
        print("   - classement      : voir le leaderboard (top 10)")
        print("   - actifs          : résumés dans >= 3 matières")
        print("   - inactifs        : jamais publié de résumé")
        print("   - gros_depensiers : utilisateurs en déficit de points")
        print("")
        print("  Cours & Résumés")
        print("   - liste           : lister les cours")
        print("   - ajouter         : ajouter un cours")
        print("   - publier         : publier un résumé")
        print("   - consulter       : résumés publics d'un cours")
        print("   - mes_resumes     : vos résumés d'un cours")
        print("   - noter           : noter un résumé")
        print("   - modifier        : modifier un de vos résumés")
        print("   - supprimer       : supprimer un de vos résumés")
        print("   - telecharger     : télécharger un résumé")
        print("   - meilleurs       : top résumés par cours")
        print("   - top_cours       : cours avec le + de résumés")
        print("   - moyenne         : moyenne de résumés par auteur")
        print("")
        print("  Boutique")
        print("   - boutique        : catalogue et achat d'objets")
        print("   - inventaire      : voir vos objets")
        print("   - top_objet       : objet le plus acheté")
        print("   - activer_titre   : activer un titre possédé")
        print("   - activer_badge   : activer un badge possédé")
        print("   - quitter         : quitter l'application")
    print("=" * 64)

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

def get_top_item() -> dict | None:
    query = """
        SELECT o.OID, o.Name, SUM(i.Quantity) as nb_achats
        FROM Inventory i
        JOIN Object o ON o.OID = i.OID
        GROUP BY i.OID, o.Name
        ORDER BY nb_achats DESC LIMIT 1
    """
    return execute_select_one(query)


def get_inactive_users() -> list[dict]:
    query = """
        SELECT u.UID, u.UName, u.Email, u.RegistrationDate
        FROM User u 
        WHERE NOT EXISTS (SELECT 1
                          FROM Summary s
                          WHERE s.AuthorID = u.UID)
        ORDER BY u.UName
    """
    return execute_select(query)

def get_high_spenders() -> list[dict]:
    query = """
        SELECT u.UID, u.UName, u.Email, u.RegistrationDate
        FROM User u
        WHERE (SELECT -SUM(t.Amount) FROM Transaction t WHERE t.UID=u.UID AND t.Amount < 0) > u.Points
    """
    return execute_select(query)

def main():
    is_active = True
    connected = 0
    while is_active:
        show_commands(connected)
        request = input("Votre commande > ").strip().lower()
        show_pause = True

        if request == CMD_CONNECT and connected == 0:
            auth_choice = input("inscrire ou connecter : ").strip().lower()
            if auth_choice == CMD_REGISTER:
                email = input("Email : ")
                username = input("Utilisateur : ")
                password = getpass.getpass("Mot de passe : ")
                current_user = register(username, password, email)
                if current_user != None:
                    connected = 1
            elif auth_choice == CMD_LOGIN:
                username = input("Utilisateur : ")
                password = getpass.getpass("Mot de passe : ")
                current_user = login(username, password)
                if current_user != None:
                    connected = 1
        elif request == CMD_LIST_COURSES and connected == 1:
            print_structured_list(get_list_courses(), "Liste des cours")
        elif request == CMD_ADD_COURSE and connected == 1:
            mnemonic = input("Mnémonique : ").strip().upper()
            name = input("Nom : ")
            faculty = input("Faculté : ")
            credit = int(input("Crédits : "))
            add_course(mnemonic, name, faculty, credit)
        elif request == CMD_PROFIL and connected == 1:
            print(f"\n{current_user}")
            active_badge = get_active_badge(current_user.get_id())
            if active_badge:
                print(f"Badge actif: {active_badge['Symbol']} {active_badge['Name']}")
            else:
                print("Badge actif: Aucun")
        elif request == CMD_PUBLISH and connected == 1:
            mnemonic = input("Mnémonique : ").strip().upper()
            if not get_course_by_mnemonic(mnemonic):
                print(f"Le cours '{mnemonic}' n'existe pas dans la table Course.")
                continue
            title = input("Titre : ")
            desc = input("Description : ")
            visibility = input("Visibilité (public, restricted, par défaut = private) : ")
            if (visibility == ""):
                visibility = "private"
            file_path = input("Entrez le chemin du fichier : ")
            if publish_summary(current_user.get_id(), mnemonic, title, desc, file_path, visibility):
                current_user.reload_user()
                print("Résumé publié !")
            else:
                print("Échec de la publication")
        elif request == CMD_VIEW_COURSE_SUMMARIES and connected == 1:
            mnemonic = input("Mnémonique du cours : ").strip().upper()
            print_structured_list(get_course_summaries(mnemonic), f"Résumés du cours {mnemonic}")
        elif request == CMD_MY_SUMMARIES and connected == 1:
            mnemonic = input("Mnémonique du cours : ").strip().upper()
            print_structured_list(get_course_summaries(mnemonic,current_user.get_id()), f"Mes résumés du cours {mnemonic}")
        elif request == CMD_RATE_SUMMARY and connected == 1:
            mnemonic = input("Mnémonique du cours : ").strip().upper()
            list_course = get_course_summaries(mnemonic)
            print_structured_list(list_course, f"Résumés à noter ({mnemonic})")
            summary_id = int(input("ID du résumé que vous voulez noter : "))
            if summary_id not in [int(item["SID"]) for item in list_course]:
                print("Résumé invalide")
                continue
            rate = int(input("Note : "))
            comment = input("Commentaire : ")
            rate_summary(current_user.get_id(), summary_id, rate, comment)
        elif request == CMD_INVENTORY and connected == 1:
            print_structured_list(get_inventory(current_user.get_id()), "Mon inventaire")
        elif request == CMD_ACTIVATE_TITLE and connected == 1:
            titles = get_owned_items(current_user.get_id())
            print_structured_list(titles, "Mes titres")
            if not titles:
                continue
            item_id = input("ID du titre que vous voulez activer : ").strip()
            if activate_title(current_user.get_id(), item_id):
                current_user.reload_user()
        elif request == CMD_ACTIVATE_BADGE and connected == 1:
            badges = get_owned_badges(current_user.get_id())
            print_structured_list(badges, "Mes badges")
            if not badges:
                continue
            item_id = input("ID du badge que vous voulez activer : ").strip()
            activate_badge(current_user.get_id(), item_id)
        elif request == CMD_SHOP and connected == 1:
            shop_items = get_shop_items()
            print_structured_list(shop_items, "Boutique")
            choice = input("Voulez vous acheter un objet ? (o/n) : ")
            if choice == "o":
                item_id = int(input("ID de l'objet que vous voulez acheter : "))
                if item_id < 0 or item_id > len(shop_items):
                    print("Objet invalide")
                    continue
                if buy_item(current_user.get_id(),item_id):
                    current_user.reload_user()
                    print("Objet acheté avec succès !")
                else:
                    print("Vous n'avez pas assez de points pour acheter cet objet")
            else:
                print("Vous n'avez pas acheté d'objet")
        elif request == CMD_HISTORY and connected == 1:
            print_structured_list(get_history(current_user.get_id()), "Historique")
        elif request == CMD_LEADERBOARD and connected == 1:
            print_structured_list(get_leaderboard(), "Classement Top 10")
        elif request == CMD_LIST_ACTIVE_USERS and connected == 1:
            print_structured_list(get_active_users(), "Utilisateurs actifs (>= 3 matières)")
        elif request == CMD_DOWNLOAD_SUMMARY and connected == 1:
            summary_id = int(input("ID du résumé que vous voulez lire : "))
            download_path = input("Entrez le chemin de destination (par défaut : dossier courant) : ")
            download_summary(summary_id, current_user.get_id(), download_path)
        elif request == CMD_EDIT_SUMMARY and connected == 1:
            my_summaries = get_own_summaries(current_user.get_id())
            print_structured_list(my_summaries, "Mes résumés")
            if not my_summaries:
                continue
            summary_id = int(input("ID du résumé que vous voulez modifier : "))
            sid_exists = any(str(item.get("SID")) == str(summary_id) for item in my_summaries)
            if not sid_exists:
                print("Résumé invalide")
                continue
            new_title = input("Nouveau titre : ")
            new_desc = input("Nouvelle description : ")
            update_summary(summary_id,current_user.get_id(), new_title, new_desc)
        elif request == CMD_DELETE_SUMMARY and connected == 1:
            my_summaries = get_own_summaries(current_user.get_id())
            print_structured_list(my_summaries, "Mes résumés")
            if not my_summaries:
                continue
            summary_id = int(input("ID du résumé que vous voulez supprimer : "))
            sid_exists = any(str(item.get("SID")) == str(summary_id) for item in my_summaries)
            if not sid_exists:
                print("Résumé invalide")
                continue
            delete_summary(summary_id,current_user.get_id())
        elif request == CMD_LIST_INACTIVE_USERS and connected == 1:
            inactive_users = get_inactive_users()
            print_structured_list(inactive_users, "Utilisateur qui n'ont pas publié")
        elif request == CMD_TOP_SUMMARIES and connected == 1:
            top_summaries = get_top_rated_summaries()
            print_structured_list(top_summaries, "Meilleurs résumés par cours")
        elif request == CMD_TOP_COURSE and connected == 1:
            top_course = get_top_course()
            print_structured_list(top_course, "Cours avec le plus de résumés")
        elif request == CMD_AVG_SUMMARIES_PER_USER and connected == 1:
            avg_result = get_average_summary_per_user()
            print_structured_list(avg_result, "Nombre moyen de résumés publiés par utilisateur")
        elif request == CMD_TOP_ITEM and connected == 1:
            top_item = get_top_item()
            print_structured_list(top_item, "Objet cosmétique le plus acheté")
        elif request == CMD_HIGH_SPENDERS and connected == 1:
            high_spenders = get_high_spenders()
            print_structured_list(high_spenders, "Utilisateurs ayant dépenses > solde actuel")
        elif request == CMD_EXIT:
            is_active = False
            show_pause = False
            connection.close()
            print("Au revoir !")
        elif connected == 0:
            print("Veuillez vous connecter")
            show_pause = False
        else:
            print("Aucune commande n'a été spécifiée")
            show_pause = False
        if is_active and show_pause:
            input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()