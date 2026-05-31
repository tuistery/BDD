import bcrypt
from datetime import date, datetime

from config import ACTION_REGISTER
from helpers import execute_select, execute_select_one, execute_write
from data_user import DataUser


def get_amount(desc: str) -> int:
    query = "SELECT PointsGain FROM Action WHERE Description = %s"
    result = execute_select_one(query, (desc,))
    if result:
        return result["PointsGain"]
    return 0

def add_transaction(action_type: str, user_id: int, custom_amount: int=None) -> None:
    query = "INSERT INTO Transaction (Description,UID,Amount,Date) VALUES (%s,%s,%s,%s)"
    amount = custom_amount if custom_amount is not None else get_amount(action_type)
    params = (action_type, user_id, amount, datetime.now())
    if execute_write(query1=query, param1=params) == -2:
        print(f"Ajout de la transaction de l'utilisateur {user_id} avec succès !")

def add_points(action_type: str, user_id: int, custom_amount: int=None) -> None:
    update_query = """
        UPDATE User
        SET Xp = Xp + (SELECT XpGain FROM Action WHERE Description = %s),
            Points = Points + (SELECT PointsGain FROM Action WHERE Description = %s)
        WHERE UID = %s
    """
    update_params = (action_type, action_type, user_id)
    
    transaction_query = "INSERT INTO Transaction (Description,UID,Amount,Date) VALUES (%s,%s,%s,%s)"
    amount = custom_amount if custom_amount is not None else get_amount(action_type)
    transaction_params = (action_type, user_id, amount, datetime.now())

    if execute_write(query1=update_query, param1=update_params, query2=transaction_query, param2=transaction_params) != -2:
        print(f"Ajout des points et de l'XP à l'utilisateur {user_id} avec succès !")

def register(username: str, password: str, email: str) -> DataUser | None:
    already_exists = execute_select_one(
        "SELECT UID FROM User WHERE Uname = %s OR Email = %s",
        (username, email)
    )
    if already_exists:
        print("Email ou nom d'utilisateur déjà utilisé.")
        return None

    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    current_date = date.today()
    query = "INSERT INTO User (UName, EncryptedPassword, Email, RegistrationDate, Points, Xp, Title) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    params = (username, hashed, email, current_date, 0, 0, "Null")
    lastrowid = execute_write(query1=query, param1=params, get_lastrow=True)
    if lastrowid >= 0 :
        new_user = DataUser(lastrowid, username, hashed, email, current_date)
        add_points(ACTION_REGISTER, new_user.get_id())
        new_user.reload_user()
        return new_user
    return None

def login(username: str, password: str) -> DataUser | None:
    password = password.encode('utf-8')
    query = "SELECT * FROM User WHERE UName = %s"
    result = execute_select_one(query, (username,)) # Le tuple (valeur,) est important
    if result and bcrypt.checkpw(password, result["EncryptedPassword"].encode('utf-8')):
        print("Connexion réalisée avec succès !")
        return DataUser(
            result["UID"],
            result["UName"],
            result["EncryptedPassword"],
            result["Email"],
            result["RegistrationDate"],
            result["Points"],
            result["Xp"],
            result["Title"],
        )
    else:
        print("Identifiant ou mot de passe incorrect.")
        return None

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

def get_history(user_id: int) -> list[dict]:
    query = """
        SELECT TID, Description, Amount, Date
        FROM Transaction
        WHERE UID = %s
        ORDER BY Date DESC
    """
    return execute_select(query, (user_id,))