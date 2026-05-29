import mysql.connector
import sys
from getpass import getpass

# Connexion globale
if len(sys.argv) >= 3 :
    user = sys.argv[1]
    password = sys.argv[2]
else :
    user = input("Nom d'utilisateur MariaDB [root] : ") or "root"
    password = getpass("Mot de passe : ")

try :
    connection = mysql.connector.connect(
        host='localhost',
        database = 'AppDb',
        user=user,
        password=password
    )
    print("Connexion réussie à la base de données")

except mysql.connector.Error as err:
    print(f"[ERREUR] Connexion impossible : {err}", file=sys.stderr)
    sys.exit(1)

# Constantes pour le menu
CMD_LOGIN = "connexion"
CMD_REGISTER = "inscription"

CMD_PROFIL = "profil"
CMD_HISTORY = "historique"
CMD_LEADERBOARD = "classement"
CMD_LIST_ACTIVE_USERS = "actifs"
CMD_LIST_INACTIVE_USERS = "inactifs"

CMD_LIST_COURSES = "liste"
CMD_ADD_COURSE = "ajouter"
CMD_PUBLISH = "publier"
CMD_VIEW_COURSE_SUMMARIES = "consulter"
CMD_MY_SUMMARIES = "mes_resumes"
CMD_RATE_SUMMARY = "noter"
CMD_EDIT_SUMMARY = "modifier"
CMD_DELETE_SUMMARY = "supprimer"
CMD_DOWNLOAD_SUMMARY = "telecharger"
CMD_TOP_SUMMARIES = "meilleurs"
CMD_TOP_COURSE = "top_cours"
CMD_AVG_SUMMARIES_PER_USER = "moyenne"

CMD_SHOP = "boutique"
CMD_INVENTORY = "inventaire"
CMD_TOP_ITEM = "top_objet"
CMD_ACTIVATE_TITLE = "activer_titre"
CMD_ACTIVATE_BADGE = "activer_badge"
CMD_HIGH_SPENDERS = "gros_depensiers"

CMD_DISCONNECTION = "deconnexion"
CMD_EXIT = "quitter"

# Libellés d'actions (doivent correspondre exactement à la table Action)
ACTION_PUBLISH_SUMMARY = "Publication d'un résumé"
ACTION_RATE_SUMMARY = "Évaluation d'un résumé"
ACTION_REGISTER = "Inscription sur la plateforme"
ACTION_BUY_TITLE = "Achat d'un titre cosmétique"
