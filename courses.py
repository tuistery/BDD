from helpers import execute_select, execute_select_one, execute_write


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
