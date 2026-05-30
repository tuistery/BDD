import mysql.connector
from config import connection


def print_structured_list(items, title="Résultats") -> None:
    """Affiche proprement une liste de dictionnaires ou un dictionnaire sous forme de tableau."""
    print(f"\n=== {title} ===")
    if not items:
        print("Aucun résultat.")
        return
    if isinstance(items, dict) :
        items = [items]
    if not isinstance(items, list) :
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

def ask_non_empty(prompt: str, error_msg: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print(error_msg)

def ask_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Veuillez entrer un nombre entier.")

def ask_positive_int(prompt: str) -> int:
    while True:
        value = ask_int(prompt)
        if value > 0:
            return value
        print("Le nombre doit être supérieur à 0.")

def ask_bounded_int(prompt: str, lo: int, hi: int) -> int:
    while True:
        value = ask_int(prompt)
        if lo <= value <= hi:
            return value
        print(f"Valeur invalide. Entrez un nombre entre {lo} et {hi}.")

def ask_yes_no(prompt: str) -> bool:
    while True:
        choice = input(prompt)
        if choice == "o":
            return True
        elif choice == "n":
            return False
        print("Réponse invalide. Entrez 'o' ou 'n'.")

def get_next_id(table, column) -> int:
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
