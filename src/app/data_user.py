from datetime import date

from helpers import execute_select_one


class DataUser:
    def __init__(self, user_id, username: str, password: str, email: str, registration_date=None, points=0, xp=0, title="Null"):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.date = registration_date if registration_date is not None else date.today()
        self.points = points
        self.xp = xp
        self.title = title

    def get_email(self) -> str: return self.email
    def get_username(self) -> str: return self.username
    def get_points(self): return self.points
    def get_xp(self): return self.xp
    def get_title(self) -> str: return self.title
    def get_id(self) -> int: return self.user_id

    def reload_user(self) -> None:
        query = "SELECT Points, Xp, Title FROM User WHERE UID = %s"
        result = execute_select_one(query, (self.get_id(),))
        if result:
            self.points = result["Points"]
            self.xp = result["Xp"]
            self.title = result["Title"]

    def __str__(self):
        """Retourne une représentation string de l'utilisateur"""
        query = """
            SELECT RankLevel
            FROM Levels
            WHERE XpRequired <= %s
            ORDER BY XpRequired DESC
            LIMIT 1;
        """
        result = execute_select_one(query, (self.xp,))
        level = result["RankLevel"] if result else 1
        return f"Utilisateur: {self.username} | Points: {self.points} | Titre: {self.title} | XP: {self.xp} | Niveau: {level}"

    def __repr__(self):
        """Retourne une représentation détaillée de l'utilisateur"""
        return f"DataUser(id={self.user_id}, username='{self.username}', points={self.points}, title='{self.title}', Xp={self.xp})"