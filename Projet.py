import mysql.connector
from datetime import date, datetime
import bcrypt

# Connexion globale
connection = mysql.connector.connect(
    host='localhost',
    database='ProjetBdd',
    user='enigma',
    password='Eni@2006'
)

# Constantes pour le menu
CMD_CONNECT = "connect"
CMD_LOGIN = "login"
CMD_REGISTER = "register"
CMD_EXIT = "exit"
CMD_LIST = "list"
CMD_COURS = "ajouter"
CMD_PROFIL = "profil"
CMD_PUBLIER = "publier"
CMD_CONSULTER = "get"
CMD_CONSULTER_MY_RESUMER = "get mine"
CMD_NOTE = "note"
CMD_MY_ITEMS = "inventaire"
CMD_SHOP = "boutique"
CMD_ACTIVATE_TITLE = "activer_titre"
CMD_ACTIVATE_BADGE = "activer_badge"
# TODO
CMD_LEADERBOARD = "classement"
CMD_MULTI_MATIERES = "actifs"

CMD_DOWNLOAD_SUMMARY = "telecharger_resume"
CMD_EDIT_SUMMARY = "modifier_resume"
CMD_DELETE_SUMMARY = "supprimer_resume"
CMD_HISTORY = "historique"
CMD_INNACTIF = "inactifs"
CMD_MEILLEURS = "meilleurs"

# Libellés d'actions (doivent correspondre exactement à la table Action)
ACTION_PUBLICATION_RESUME = "Publication d’un résumé"
ACTION_EVALUATION_RESUME = "Évaluation d’un résumé"
ACTION_INSCRIPTION = "Inscription sur la plateforme"
ACTION_ACHAT_TITRE = "Achat d’un titre cosmétique"

def print_structured_list(items, title="Resultats"):
    """Affiche proprement une liste de dictionnaires sous forme de tableau."""
    print(f"\n=== {title} ===")

    if not items:
        print("Aucun resultat.")
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

def get_next_id(table, id):
    cursor = connection.cursor()
    query = f"SELECT COALESCE(MAX({id}), 0) + 1 FROM {table}"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    return result[0]

class DataUser:
    def __init__(self, username: str, password: str, email: str, date_="2026-04-03", points=0, Xp=0, title="Null", id=-1):
        if id == -1:
            self.userId = get_next_id("User", "UID")
        else:
            self.userId = id
            
        self.username = username
        self.email = email
        self.password = password
        self.date_ = date_
        self.points = points
        self.Xp = Xp
        self.title = title

    def getEmail(self) -> str: return self.email
    def getUsername(self) -> str: return self.username
    def getPoints(self): return self.points
    def getXp(self): return self.Xp
    def getTitle(self) -> str: return self.title
    def getId(self) -> int: return self.userId
    def displayInfo(self):
        """Affiche les informations principales de l'utilisateur"""
        print(f"Username: {self.username}")
        print(f"Points: {self.points}")
        print(f"Title: {self.title}")
        print(f"XP: {self.Xp}")
    
    def reload_user(self):
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            try:
                query = "SELECT Points, Xp, Title FROM User WHERE UID = %s"
                cursor.execute(query, (self.getId(),))
                result = cursor.fetchone()
                
                if result:
                    self.points = result["Points"]
                    self.Xp = result["Xp"]
                    self.title = result["Title"]
                
            except mysql.connector.Error as err:
                print(f"Erreur lors du reload : {err}")
            finally:
                cursor.close()
    
    # Méthode __str__ pour print() direct
    def __str__(self):
        """Retourne une représentation string de l'utilisateur"""
        return f"Username: {self.username} | Points: {self.points} | Title: {self.title} | XP: {self.Xp}"
    
    # Méthode __repr__ pour debugging
    def __repr__(self):
        """Retourne une représentation détaillée de l'utilisateur"""
        return f"DataUser(id={self.userId}, username='{self.username}', points={self.points}, title='{self.title}', Xp={self.Xp})"

def getAmount(desc:str):
    if not connection.is_connected():
        return 0

    amount = 0
    cursor = connection.cursor(dictionary=True)
    query = "SELECT CoinGain FROM Action WHERE Description = %s"
    try:
        cursor.execute(query,(desc,))
        resultat = cursor.fetchone()
        if resultat and "CoinGain" in resultat:
            amount = resultat["CoinGain"]
    except mysql.connector.Error as err:
        print(f"Erreur de insert : {err}")
    finally:
        cursor.close()
        return amount

def ajoutTransaction(typeAction:str,userid:int):
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "INSERT INTO Transaction (TID,Description,UID,Amount,Date) VALUES (%s,%s,%s,%s,%s)"
        val = (get_next_id("Transaction", "TID"),typeAction,userid,getAmount(typeAction),date.today())
    try:
        cursor.execute(query, val)
        connection.commit()
        print(f"Ajout de la transaction de l'utilisateur {userid} avec succès !")
    except mysql.connector.Error as err:
        print(f"Erreur de insert : {err}")
    finally:
        cursor.close()

def ajoutPoints(typeAction:str,id:int):
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = """
            UPDATE User
            SET Xp = Xp + (SELECT XpGain FROM Action WHERE Description = %s),
                Points = Points + (SELECT CoinGain FROM Action WHERE Description = %s)
            WHERE UID = %s
        """
        val = (typeAction,typeAction,id)
    try:
        cursor.execute(query, val)
        connection.commit()
        print(f"Ajout des points et de l'xp a l'utilisateur {id} avec succès !")
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
    finally:
        cursor.close()
        ajoutTransaction(typeAction,id)
    
def register(userName: str, password: str, email: str) -> DataUser:
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    u = DataUser(userName, hashed, email,date.today())
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "INSERT INTO User (UID, UName, Pass, Email, RegistrationDate, Points, Xp, Title) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (u.getId(), u.getUsername(), u.password, u.getEmail(), u.date_, u.getPoints(), u.getXp(), u.getTitle())
        try:
            cursor.execute(query, val)
            connection.commit()
            ajoutPoints(ACTION_INSCRIPTION, u.getId())
            u.reload_user()
            print(f"Utilisateur {userName} enregistré avec succès !")
        except mysql.connector.Error as err:
            print(f"Erreur d'insertion : {err}")
        finally:
            cursor.close()
    return u

def login(userName: str, password: str) -> DataUser:
    password = password.encode('utf-8')
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM User WHERE UName = %s"
        cursor.execute(query, (userName,)) # Le tuple (valeur,) est important
        resultat = cursor.fetchone()
        cursor.close()

        if resultat and  bcrypt.checkpw(password, resultat["Pass"].encode('utf-8')):
            print("Le login a fonctionné avec succès")
            return DataUser(
                resultat["UName"], 
                resultat["Pass"], 
                resultat["Email"], 
                resultat["RegistrationDate"], 
                resultat["Points"], 
                resultat["Xp"], 
                resultat["Title"], 
                resultat["UID"]
            )
        else:
            print("Utilisateur introuvable ou mauvais mot de passe.")
            return None

def getListCours():
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM Course"
        cursor.execute(query)
        resultat = cursor.fetchall()
        cursor.close()
        return resultat 
    else:
        return None

def getCourseByMnemonic(mnemonic: str):
    if not connection.is_connected():
        return None

    cursor = connection.cursor(dictionary=True)
    query = "SELECT Mnemonic FROM Course WHERE Mnemonic = %s"
    try:
        cursor.execute(query, (mnemonic,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
        return None
    finally:
        cursor.close()

def ajoutCours(newMnemonic: str,newName: str,faculty: str,newCredit:int):
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "INSERT INTO Course (Mnemonic,Name,Faculty,Credits) VALUES (%s, %s, %s, %s)"
        val = (newMnemonic,newName,faculty,newCredit)
        try:
            cursor.execute(query, val)
            connection.commit()
            print(f"Cours {newName} enregistré avec succès !")
        except mysql.connector.Error as err:
            print(f"Erreur d'insertion : {err}")
        finally:
            cursor.close()

def publierResumer(authorID: int, mnemonique:str,title:str,desc:str, filePath:str, visibility = "private"):
     if connection.is_connected():
        cursor = connection.cursor(dictionary=True)

        try :
            with open(filePath, 'rb') as f:
                    fileContent = f.read()
        except Exception as e :
            print(f"Impossible de lire le fichier : {e}")
            return

        fileQuery = "INSERT INTO Files (Name, Size, Content) VALUES (%s, %s, %s)"
        fileName = f"{authorID}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        fileVal = (fileName, len(fileContent), fileContent)

        query = "INSERT INTO Summary (SID,AuthorID,FileID,Course,PublicationDate,Title,Description,Version,Visibility) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(fileQuery, fileVal)
            fileID = cursor.lastrowid
            val = (get_next_id("Summary", "SID"),authorID,fileID,mnemonique,date.today(),title,desc,"1.0",visibility)
            cursor.execute(query, val)
            connection.commit()
            print(f"Résumé avec le titre : {title} a été enregistré pour le cours {mnemonique} avec succès !")
            ajoutPoints(ACTION_PUBLICATION_RESUME, authorID)
        except mysql.connector.Error as err:
            print(f"Erreur d'insertion : {err}")
        finally:
            cursor.close()

def consulterResumé(mnemonic:str , userId = -1):
    resultat = []
    if not connection.is_connected():
        return resultat

    cursor = connection.cursor(dictionary=True)
    if userId == -1:
        query = "SELECT * FROM Summary WHERE Course = %s AND Visibility = 'public'"
        params = (mnemonic,)
    else:
        query = "SELECT * FROM Summary WHERE Course = %s AND AuthorID = %s"
        params = (mnemonic, userId)

    try:
        cursor.execute(query, params)
        resultat = cursor.fetchall()
        print(f"Demande de tout les resumés du cours : {mnemonic} avec succès !")
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
    finally:
        cursor.close()
    return resultat

def publierNote(UID:int,SID:int,Note:int,Comment:str):
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "INSERT INTO Notes (NID,UID,SID,Note,Comment) VALUES (%s, %s, %s, %s, %s)"
        val = (get_next_id("Notes", "NID"),UID,SID,Note,Comment)
        try:
            cursor.execute(query, val)
            connection.commit()
            print(f"Note {Note} publiée avec succès !")
            ajoutPoints(ACTION_EVALUATION_RESUME, UID)
        except mysql.connector.Error as err:
            print(f"Erreur de insert : {err}")
        finally:
            cursor.close()
        
def consulterInventaire(UID:int):
    resultat = []
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM Inventory WHERE OwnerID = %s"
        val = (UID,)
        try:
            cursor.execute(query, val)
            resultat = cursor.fetchall()
            print(f"Inventaire de l'utilisateur {UID} avec succès !")
        except mysql.connector.Error as err:
            print(f"Erreur de select : {err}")
        finally:
            cursor.close()
    return resultat

def ajoutInventaire(UID:int,OID:int):
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "INSERT INTO Inventory (OID,OwnerID) VALUES (%s, %s)"
        val = (OID,UID)
        try:
            cursor.execute(query, val)
            connection.commit()
            print(f"Objet {OID} ajouté à l'inventaire de l'utilisateur {UID} avec succès !")
        except mysql.connector.Error as err:
            print(f"Erreur de insert : {err}")
        finally:
            cursor.close()

def consulterBoutique():
    resultat = []
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM Object"
        try:
            cursor.execute(query)
            resultat = cursor.fetchall()
            print(f"Boutique avec succès !")
        except mysql.connector.Error as err:
            print(f"Erreur de select : {err}")
        finally:
            cursor.close()
    return resultat

def consulterTitresPossedes(UID:int):
    if not connection.is_connected():
        return []

    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT i.OID, t.Label, i.isActive
        FROM Inventory i
        JOIN Title t ON t.OID = i.OID
        WHERE i.OwnerID = %s
        ORDER BY i.OID
    """
    try:
        cursor.execute(query, (UID,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
        return []
    finally:
        cursor.close()

def consulterBadgesPossedes(UID:int):
    if not connection.is_connected():
        return []

    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT i.OID, b.Symbol, o.Name, i.isActive
        FROM Inventory i
        JOIN Badge b ON b.OID = i.OID
        JOIN Object o ON o.OID = i.OID
        WHERE i.OwnerID = %s
        ORDER BY i.OID
    """
    try:
        cursor.execute(query, (UID,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
        return []
    finally:
        cursor.close()

def consulterBadgeActif(UID:int):
    if not connection.is_connected():
        return None

    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT b.Symbol, o.Name
        FROM Inventory i
        JOIN Badge b ON b.OID = i.OID
        JOIN Object o ON o.OID = i.OID
        WHERE i.OwnerID = %s AND i.isActive = TRUE
        LIMIT 1
    """
    try:
        cursor.execute(query, (UID,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
        return None
    finally:
        cursor.close()

def acheterObjet(UID:int,OID:int):
    if not connection.is_connected():
        return False

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT Price, Name FROM Object WHERE OID = %s", (OID,))
        objet = cursor.fetchone()
        if not objet:
            print("Objet introuvable.")
            return False

        prix = int(float(objet["Price"]))
        cursor.execute("SELECT Points FROM User WHERE UID = %s", (UID,))
        user_data = cursor.fetchone()
        if not user_data:
            print("Utilisateur introuvable.")
            return False

        if user_data["Points"] < prix:
            return False

        # Débit atomique pour éviter les achats simultanés au-delà du solde.
        cursor.execute(
            "UPDATE User SET Points = Points - %s WHERE UID = %s AND Points >= %s",
            (prix, UID, prix)
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
            (OID, UID)
        )
        connection.commit()
        print(f"Objet '{objet['Name']}' acheté pour {prix} points.")

        # Récompense XP/coins définie dans la table Action.
        ajoutPoints(ACTION_ACHAT_TITRE, UID)
        return True
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Erreur de insert : {err}")
        return False
    finally:
        cursor.close()

def activerTitle(UID:int,OID:int):
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
            (UID, OID)
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
            (UID,)
        )
        cursor.execute(
            "UPDATE Inventory SET isActive = TRUE WHERE OwnerID = %s AND OID = %s",
            (UID, OID)
        )
        cursor.execute(
            "UPDATE User SET Title = %s WHERE UID = %s",
            (title_row["Label"], UID)
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

def activerBadge(UID:int,OID:int):
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
            (UID, OID)
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
            (UID,)
        )
        cursor.execute(
            "UPDATE Inventory SET isActive = TRUE WHERE OwnerID = %s AND OID = %s",
            (UID, OID)
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

def consulterClassement():
    if not connection.is_connected():
        return []

    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT UName, Points, Xp, Title
        FROM User
        ORDER BY Points DESC, Xp DESC, UName ASC
        LIMIT 10
    """
    try:
        cursor.execute(query)
        classement = cursor.fetchall()
        for idx, row in enumerate(classement, start=1):
            row["Rang"] = idx
        return classement
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
        return []
    finally:
        cursor.close()

def consulterUsersMultiMatieres():
    if not connection.is_connected():
        return []

    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT UName
        FROM User u
        WHERE (
            SELECT COUNT(DISTINCT Course)
            FROM Summary
            WHERE AuthorID = u.UID
        ) >= 3
    """
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
        return []
    finally:
        cursor.close()

def consulterHistorique(UID:int):
    if not connection.is_connected():
        return []

    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT TID, Description, Amount, Date
        FROM Transaction
        WHERE UID = %s
        ORDER BY Date DESC
    """
    try:
        cursor.execute(query, (UID,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
        return []
    finally:
        cursor.close()

def modifierResumer(SID:int,UID:int,newTitle:str,newDesc:str):
    if not connection.is_connected():
        return False

    cursor = connection.cursor(dictionary=True)
    query = """
        UPDATE Summary
        SET Title = %s, Description = %s
        WHERE SID = %s AND AuthorID = %s
    """
    try:
        cursor.execute(query, (newTitle, newDesc, SID, UID))
        if cursor.rowcount == 0:
            print("Résumé introuvable ou vous n'êtes pas l'auteur.")
            connection.rollback()
            return False
        connection.commit()
        print(f"Résumé {SID} modifié avec succès !")
        return True
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Erreur de update : {err}")
        return False
    finally:
        cursor.close()

def consulterMesResumes(UID:int):
    if not connection.is_connected():
        return []

    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM Summary WHERE AuthorID = %s ORDER BY PublicationDate DESC"
    try:
        cursor.execute(query, (UID,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
        return []
    finally:
        cursor.close()

def supprimerResumer(SID:int,UID:int):
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "DELETE FROM Summary WHERE SID = %s AND AuthorID = %s"
        val = (SID,UID)
        try:
            cursor.execute(query, val)
            connection.commit()
            print(f"Résumé {SID} supprimé avec succès !")
        except mysql.connector.Error as err:
            print(f"Erreur de delete : {err}")
        finally:
            cursor.close()

def telechargerResume(SID:int, UID:int, downloadPath:str) :
    if connection.is_connected() :
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT f.Name, f.Content 
        FROM Files f, Summary s
        WHERE s.FileID=f.FID AND s.SID=%s AND (s.AuthorID=%s OR s.Visibility='public' OR s.Visibility='restricted')
        """
        val = (SID, UID)
        try :
            cursor.execute(query, val)
            file = cursor.fetchone()
            if file is None :
                print("Vous n'avez pas accès à ce fichier ou le fichier est inexistant")
                return
            if downloadPath == "" :
                downloadPath = file['Name']
            elif not os.path.isdir(downloadPath) :
                print(f"Dossier inexistant : {downloadPath}")
                return
            else :
                downloadPath = os.path.join(downloadPath, file['Name'])
            try :
                with open(downloadPath, 'wb') as f :
                    f.write(file['Content'])
            except Exception as e :
                print(f"Impossible d'écrire dans ce dossier : {e}")
                return
            
            print(f"Fichier enregistré sur {downloadPath}")
        
        except mysql.connector.Error as err :
            print(f"Erreur : {err}")
        finally :
            cursor.close()
 
def afficherCommandes(connected: int):
    print("\n" + "=" * 64)
    print("                    MENU DES COMMANDES")
    print("=" * 64)
    if connected == 0:
        print("  Session")
        print("   - connect        : se connecter / s'inscrire")
        print("   - exit           : quitter l'application")
    else:
        print("  Utilisateur")
        print("   - profil         : voir votre profil")
        print("   - historique     : voir vos transactions")
        print("   - classement     : voir le leaderboard (top 10)")
        print("   - actifs         : utilisateurs avec resumes dans >= 3 matieres")
        print("   - inactifs       : utilisateurs n'ayant jamais publie de resume")
        print("")
        print("  Cours & Resumes")
        print("   - list           : lister les cours")
        print("   - ajouter        : ajouter un cours")
        print("   - publier        : publier un resume")
        print("   - get            : voir les resumes publics d'un cours")
        print("   - get mine       : voir vos resumes d'un cours")
        print("   - note           : noter un resume")
        print("   - modifier_resume: modifier un de vos resumes")
        print("   - supprimer_resume: supprimer un de vos resumes")
        print("   - telecharger_resume: télécharger un résumé sur le disque")
        print("   - meilleurs      : les resumes les mieux notes par cours")
        print("")
        print("  Boutique")
        print("   - boutique       : voir et acheter des objets")
        print("   - inventaire     : voir vos objets")
        print("   - activer_titre  : activer un titre possede")
        print("   - activer_badge  : activer un badge possede")
        print("   - exit           : quitter l'application")
    print("=" * 64)

def noteMaxDeChaqueResumé():
    if not connection.is_connected():
        return []

    cursor = connection.cursor(dictionary=True)
    query = "SELECT c.Mnemonic, c.Name AS CourseName, s.SID, s.Title AS SummaryTitle, avg_notes.AverageNote FROM Course c JOIN Summary s ON c.Mnemonic = s.Course JOIN (SELECT SID, AVG(Note) AS AverageNote FROM Notes GROUP BY SID) AS avg_notes ON s.SID = avg_notes.SID JOIN (SELECT s2.Course, MAX(avg_note) AS max_avg FROM (SELECT s2.SID, s2.Course, AVG(n2.Note) AS avg_note FROM Summary s2 JOIN Notes n2 ON s2.SID = n2.SID GROUP BY s2.SID, s2.Course) AS s2 GROUP BY s2.Course) AS course_max ON s.Course = course_max.Course AND avg_notes.AverageNote = course_max.max_avg ORDER BY c.Mnemonic;"
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
        return []
    finally:
        cursor.close()

def utilisateurQuiNontJamaisPublier():
    if not connection.is_connected():
        return []

    cursor = connection.cursor(dictionary=True)
    query = "SELECT u.UID, u.UName, u.Email, u.RegistrationDate FROM User u WHERE NOT EXISTS ( SELECT 1 FROM Summary s WHERE s.AuthorID = u.UID) ORDER BY u.UName;"
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erreur de select : {err}")
        return []
    finally:
        cursor.close()


def main():
    isActive = True
    connected = 0
    while isActive:
        afficherCommandes(connected)
        request = input("Votre commande > ").strip().lower()
        
        if request == CMD_CONNECT and connected == 0:
            Ctype = input("Register or Login : ").strip().lower()
            if Ctype == CMD_REGISTER:
                eMail = input("Email : ")
                userName = input("Username : ")
                PassWord = input("Password : ")
                CurrentUser = register(userName, PassWord, eMail)
                if CurrentUser != None:
                    connected = 1
            elif Ctype == CMD_LOGIN:
                userName = input("Username : ")
                PassWord = input("Password : ")
                CurrentUser= login(userName, PassWord)
                if CurrentUser != None:
                    connected = 1
        elif request == CMD_LIST and connected == 1:
            print_structured_list(getListCours(), "Liste des cours")
        elif request == CMD_COURS and connected == 1:
            newMnemonic = input("Mnemonic : ").strip().upper()
            newName = input("Name : ")
            faculty = input("Faculty : ")
            newCredit = int(input("Credits : "))
            ajoutCours(newMnemonic,newName,faculty,newCredit)
        elif request == CMD_PROFIL and connected == 1:
            print(f"\n{CurrentUser}")
            active_badge = consulterBadgeActif(CurrentUser.getId())
            if active_badge:
                print(f"Badge actif: {active_badge['Symbol']} {active_badge['Name']}")
            else:
                print("Badge actif: Aucun")
        elif request == CMD_PUBLIER and connected == 1:
            newMnemonic = input("Mnemonic : ").strip().upper()
            if not getCourseByMnemonic(newMnemonic):
                print(f"Le cours '{newMnemonic}' n'existe pas dans la table Course.")
                continue
            newTitle = input("Title : ")
            newDesc = input("Desc : ")
            newVisibility = input("Visibility (default = private) :")
            if (newVisibility == ""):
                newVisibility = "private"
            filePath = input("Entrez le chemin du fichier :")
            publierResumer(CurrentUser.getId(),newMnemonic,newTitle,newDesc, filePath, newVisibility)
            CurrentUser.reload_user()
        elif request == CMD_CONSULTER and connected == 1:
            mnemonic = input("Quel cours voulez voir les résumés ? : ").strip().upper()
            print_structured_list(consulterResumé(mnemonic), f"Resumes du cours {mnemonic}")
        elif request == CMD_CONSULTER_MY_RESUMER and connected == 1:
            mnemonic = input("Quel cours voulez voir les résumés ? : ").strip().upper()
            print_structured_list(consulterResumé(mnemonic,CurrentUser.getId()), f"Mes resumes du cours {mnemonic}")
        elif request == CMD_NOTE and connected == 1:
            mnemonic = input("Quel cours voulez voir les résumés pour les noter ? : ").strip().upper()
            list_course = consulterResumé(mnemonic)
            print_structured_list(list_course, f"Resumes a noter ({mnemonic})")
            sid = int(input("Quel résumé voulez vous noter ? : (entrer le SID) "))
            print("TEST : ",sid)
            if sid not in [int(item["SID"]) for item in list_course]:
                print("SID invalide")
                continue
            note = int(input("Note : "))
            comment = input("Comment : ")
            publierNote(CurrentUser.getId(),sid,note,comment)
        elif request == CMD_MY_ITEMS and connected == 1:
            print_structured_list(consulterInventaire(CurrentUser.getId()), "Mon inventaire")
        elif request == CMD_ACTIVATE_TITLE and connected == 1:
            titles = consulterTitresPossedes(CurrentUser.getId())
            print_structured_list(titles, "Mes titres")
            if not titles:
                continue
            oid = input("Quel titre activer ? (OID) : ").strip()
            if activerTitle(CurrentUser.getId(), oid):
                CurrentUser.reload_user()
        elif request == CMD_ACTIVATE_BADGE and connected == 1:
            badges = consulterBadgesPossedes(CurrentUser.getId())
            print_structured_list(badges, "Mes badges")
            if not badges:
                continue
            oid = input("Quel badge activer ? (OID) : ").strip()
            activerBadge(CurrentUser.getId(), oid)
        elif request == CMD_SHOP and connected == 1:
            shop_items = consulterBoutique()
            print_structured_list(shop_items, "Boutique")
            choix = input("Voulez vous acheter un objet ? (o/n) : ")
            if choix == "o":
                oid = int(input("Quel objet voulez vous acheter ? : (entrer le OID)"))
                if oid < 0 or oid > len(shop_items):
                    print("OID invalide")
                    continue
                if acheterObjet(CurrentUser.getId(),oid):
                    CurrentUser.reload_user()
                    print("Objet acheté avec succès !")
                else:
                    print("Vous n'avez pas assez de points pour acheter cet objet")
            else:
                print("Vous n'avez pas acheté d'objet")
        elif request == CMD_HISTORY and connected == 1:
            print_structured_list(consulterHistorique(CurrentUser.getId()), "Historique")
        elif request == CMD_LEADERBOARD and connected == 1:
            print_structured_list(consulterClassement(), "Classement Top 10")
        elif request == CMD_MULTI_MATIERES and connected == 1:
            print_structured_list(consulterUsersMultiMatieres(), "Utilisateurs actifs (>= 3 matieres)")
        elif request == CMD_DOWNLOAD_SUMMARY and connected == 1:
            sid = int(input("Quel résumé voulez-vous lire ? (entrer le SID) : "))
            downloadPath = input("Entrez le chemin de destination (par défaut : dossier courant) : ")
            telechargerResume(sid, CurrentUser.getId(), downloadPath)
        elif request == CMD_EDIT_SUMMARY and connected == 1:
            my_summaries = consulterMesResumes(CurrentUser.getId())
            print_structured_list(my_summaries, "Mes resumes")
            if not my_summaries:
                continue
            sid = int(input("Quel résumé voulez vous modifier ? : (entrer le SID)"))
            sid_exists = any(str(item.get("SID")) == str(sid) for item in my_summaries)
            if not sid_exists:
                print("SID invalide")
                continue
            newTitle = input("Nouveau titre : ")
            newDesc = input("Nouvelle description : ")
            modifierResumer(sid,CurrentUser.getId(),newTitle,newDesc)
        elif request == CMD_DELETE_SUMMARY and connected == 1:
            my_summaries = consulterMesResumes(CurrentUser.getId())
            print_structured_list(my_summaries, "Mes resumes")
            if not my_summaries:
                continue
            sid = int(input("Quel résumé voulez vous supprimer ? : (entrer le SID)"))
            sid_exists = any(str(item.get("SID")) == str(sid) for item in my_summaries)
            if not sid_exists:
                print("SID invalide")
                continue
            supprimerResumer(sid,CurrentUser.getId())
        elif request == CMD_INNACTIF and connected == 1:
            my_summaries = utilisateurQuiNontJamaisPublier()
            print_structured_list(my_summaries, "User qui n'ont pas publié")
        elif request == CMD_MEILLEURS and connected == 1:
            my_summaries = noteMaxDeChaqueResumé()
            print_structured_list(my_summaries, "Meilleurs resumés par cours")
        elif request == CMD_EXIT:
            isActive = False
            connection.close()
            print("Au revoir !")
        elif connected == 0:
            print("Veuillez vous connecter")
        else:
            print("Aucune commande n'a été spécifiée")
            

if __name__ == "__main__":
    main()
