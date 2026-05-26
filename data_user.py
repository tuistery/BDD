from helpers import execute_select_one, get_next_id


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

    def __str__(self):
        """Retourne une représentation string de l'utilisateur"""
        query = """
            SELECT RankLevel
            FROM Levels
            WHERE XpRequired <= %s
            ORDER BY XpRequired DESC
            LIMIT 1;
        """
        level = execute_select_one(query, (self.xp,))["RankLevel"]
        return f"Utilisateur: {self.username} | Points: {self.points} | Titre: {self.title} | XP: {self.xp} | Niveau: {level}"

    def __repr__(self):
        """Retourne une représentation détaillée de l'utilisateur"""
        return f"DataUser(id={self.user_id}, username='{self.username}', points={self.points}, title='{self.title}', Xp={self.xp})"
