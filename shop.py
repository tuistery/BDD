import mysql.connector

from db import connection, ACTION_BUY_TITLE
from helpers import execute_select, execute_select_one
from users import add_points


def get_shop_items() -> list[dict]:
    query = "SELECT * FROM Object"
    return execute_select(query)


def get_inventory(user_id: int) -> list[dict]:
    query = "SELECT * FROM Inventory WHERE OwnerID = %s"
    return execute_select(query, (user_id,))


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


def get_top_item() -> dict | None:
    query = """
        SELECT o.OID, o.Name, SUM(i.Quantity) as nb_achats
        FROM Inventory i
        JOIN Object o ON o.OID = i.OID
        GROUP BY i.OID, o.Name
        ORDER BY nb_achats DESC LIMIT 1
    """
    return execute_select_one(query)
