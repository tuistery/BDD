import mysql.connector

from config import connection, ACTION_BUY_TITLE
from helpers import execute_select, execute_select_one
from users import add_points


def get_shop_items() -> list[dict]:
    query = "SELECT * FROM Object"
    return execute_select(query)

def get_inventory(user_id: int) -> list[dict]:
    query = "SELECT * FROM Owns WHERE UID = %s"
    return execute_select(query, (user_id,))

def get_owned_items(user_id: int) -> list[dict]:
    query = """
        SELECT ow.OID, o.Name, ow.isActive
        FROM Owns ow
        JOIN Object o ON o.OID = ow.OID
        WHERE ow.UID = %s
        ORDER BY ow.OID
    """
    return execute_select(query, (user_id,))

def get_owned_badges(user_id: int) -> list[dict]:
    query = """
        SELECT ow.OID, o.Name, ow.isActive
        FROM Owns ow
        JOIN Object o ON o.OID = ow.OID
        WHERE ow.UID = %s AND o.Type = 'badge'
        ORDER BY ow.OID
    """
    return execute_select(query, (user_id,))

def get_active_badges(user_id: int) -> list[dict]:
    query = """
        SELECT o.Name
        FROM Owns ow
        JOIN Object o ON o.OID = ow.OID
        WHERE ow.UID = %s AND o.Type = 'badge' AND ow.isActive = TRUE
    """
    return execute_select(query, (user_id,))

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
            INSERT INTO Owns (OID, UID, Quantity)
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
            SELECT o.Name
            FROM Owns ow
            JOIN Object o ON o.OID = ow.OID
            WHERE ow.UID = %s AND ow.OID = %s AND o.Type = 'titre'
            """,
            (user_id, object_id)
        )
        title_row = cursor.fetchone()
        if not title_row:
            print("Ce titre n'est pas dans votre inventaire.")
            return False

        cursor.execute(
            """
            UPDATE Owns ow
            JOIN Object o ON o.OID = ow.OID
            SET ow.isActive = FALSE
            WHERE ow.UID = %s AND o.Type = 'titre'
            """,
            (user_id,)
        )
        cursor.execute(
            "UPDATE Owns SET isActive = TRUE WHERE UID = %s AND OID = %s",
            (user_id, object_id)
        )
        cursor.execute(
            "UPDATE User SET Title = %s WHERE UID = %s",
            (title_row["Name"], user_id)
        )
        connection.commit()
        print(f"Titre activé : {title_row['Name']}")
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
            SELECT o.Name
            FROM Owns ow
            JOIN Object o ON o.OID = ow.OID
            WHERE ow.UID = %s AND ow.OID = %s AND o.Type = 'badge'
            """,
            (user_id, object_id)
        )
        badge_row = cursor.fetchone()
        if not badge_row:
            print("Ce badge n'est pas dans votre inventaire.")
            return False

        cursor.execute(
            "UPDATE Owns SET isActive = TRUE WHERE UID = %s AND OID = %s",
            (user_id, object_id)
        )
        connection.commit()
        print(f"Badge activé : {badge_row['Name']}")
        return True
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Erreur de update : {err}")
        return False
    finally:
        cursor.close()

def get_top_item() -> dict | None:
    query = """
        SELECT o.OID, o.Name, SUM(ow.Quantity) as nb_achats
        FROM Owns ow
        JOIN Object o ON o.OID = ow.OID
        GROUP BY ow.OID, o.Name
        ORDER BY nb_achats DESC LIMIT 1
    """
    return execute_select_one(query)