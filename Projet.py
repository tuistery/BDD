import mysql.connector
from datetime import date

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

def get_table_length(table_name: str):
    cursor = connection.cursor()
    query = f"SELECT COUNT(*) FROM {table_name}"
    
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    
    return result[0]

userId_counter = get_table_length("User")

class DataUser:
    def __init__(self, username: str, password: str, email: str, date_="2026-04-03", points=0, Xp=0, title="Null", id=-1):
        global userId_counter
        if id == -1:
            userId_counter += 1
            self.userId = userId_counter
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
    
    # Méthode __str__ pour print() direct
    def __str__(self):
        """Retourne une représentation string de l'utilisateur"""
        return f"Username: {self.username} | Points: {self.points} | Title: {self.title} | XP: {self.Xp}"
    
    # Méthode __repr__ pour debugging
    def __repr__(self):
        """Retourne une représentation détaillée de l'utilisateur"""
        return f"DataUser(id={self.userId}, username='{self.username}', points={self.points}, title='{self.title}', Xp={self.Xp})"

def register(userName: str, password: str, email: str) -> DataUser:
    u = DataUser(userName, password, email,date.today())
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        # Ajout du VALUES et des %s
        query = "INSERT INTO User (UID, UName, Pass, Email, RegistrationDate, Points, Xp, Title) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (u.getId(), u.getUsername(), u.password, u.getEmail(), u.date_, u.getPoints(), u.getXp(), u.getTitle())
        
        try:
            cursor.execute(query, val)
            connection.commit()  # OBLIGATOIRE pour sauvegarder
            print(f"Utilisateur {userName} enregistré avec succès !")
        except mysql.connector.Error as err:
            print(f"Erreur d'insertion : {err}")
        finally:
            cursor.close()
    return u

def login(userName: str, password: str) -> DataUser:
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM User WHERE UName = %s"
        cursor.execute(query, (userName,)) # Le tuple (valeur,) est important
        resultat = cursor.fetchone()
        cursor.close()

        if resultat and resultat["Pass"] == password:
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

def ajoutCours(newMnemonic: str,newName: str,faculty: str):
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "INSERT INTO Course (Mnemonic,Name,Faculty) VALUES (%s, %s, %s)"
        val = (newMnemonic,newName,faculty)
        try:
            cursor.execute(query, val)
            connection.commit()  # OBLIGATOIRE pour sauvegarder
            print(f"Cours {newName} enregistré avec succès !")
        except mysql.connector.Error as err:
            print(f"Erreur d'insertion : {err}")
        finally:
            cursor.close()


def main():
    isActive = True
    connected = 0
    while isActive:
        request = input("\nNouvelle commande (connect / list / ajouter / profil / exit) : ").strip().lower()
        
        if request == CMD_CONNECT and connected == 0:
            Ctype = input("Register or Login : ").strip().lower()
            if Ctype == CMD_REGISTER:
                eMail = input("Email : ")
                userName = input("Username : ")
                PassWord = input("Password : ")
                CurrentUser = register(userName, PassWord, eMail)
                connected = 1
            elif Ctype == CMD_LOGIN:
                userName = input("Username : ")
                PassWord = input("Password : ")
                CurrentUser= login(userName, PassWord)
                connected = 1
        elif request == CMD_LIST and connected == 1:
            print(getListCours())
        elif request == CMD_COURS and connected == 1:
            newMnemonic = input("Mnemonic : ")
            newName = input("Name : ")
            faculty = input("Faculty : ")
            ajoutCours(newMnemonic,newName,faculty)
        elif request == CMD_PROFIL and connected == 1:
            print(f"\n{CurrentUser}")
        elif request == CMD_EXIT:
            isActive = False
            connection.close()
            print("Au revoir !")

if __name__ == "__main__":
    main()