import bcrypt
from datetime import date

from config import ACTION_REGISTER
from helpers import execute_select, execute_select_one, execute_write, get_next_id
from data_user import DataUser


def get_amount(desc: str) -> int:
    query = "SELECT CoinGain FROM Action WHERE Description = %s"
    result = execute_select_one(query, (desc,))
    if result:
        return result["CoinGain"]
    return 0


def add_transaction(action_type: str, user_id: int, custom_amount: int=None) -> None:
    query = "INSERT INTO Transaction (TID,Description,UID,Amount,Date) VALUES (%s,%s,%s,%s,%s)"
    amount = custom_amount if custom_amount is not None else get_amount(action_type)
    params = (get_next_id("Transaction", "TID"), action_type, user_id, amount, date.today())
    if execute_write(query, params) != -1:
        print(f"Ajout de la transaction de l'utilisateur {user_id} avec succès !")


def add_points(action_type: str, user_id: int, custom_amount: int=None) -> None:
    query = """
        UPDATE User
        SET Xp = Xp + (SELECT XpGain FROM Action WHERE Description = %s),
            Points = Points + (SELECT CoinGain FROM Action WHERE Description = %s)
        WHERE UID = %s
    """
    params = (action_type, action_type, user_id)
    if execute_write(query, params) != -1:
        print(f"Ajout des points et de l'XP à l'utilisateur {user_id} avec succès !")
        add_transaction(action_type, user_id, custom_amount)


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
