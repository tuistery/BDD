import os
from getpass import getpass

from config import *
from helpers import *
from users import *
from courses import *
from summaries import *
from shop import *


def ask_mnemonic() -> str | None:
    while True:
        entry = input("Mnémonique du cours : ").strip()
        if not entry:
            print("Veuillez entrer un mnémonique.")
            continue
        if entry.lower() == "annuler":
            return None
        mnemonic = entry.upper()
        if get_course_by_mnemonic(mnemonic):
            return mnemonic
        print(f"Le cours '{entry}' n'existe pas. Réessayer.")
        print("Tapez 'annuler' pour revenir.")

def ask_id_from_list(items: list[dict], key: str, prompt: str) -> int:
    while True:
        try:
            item_id = int(input(prompt))
            if item_id in [int(item[key]) for item in items]:
                return item_id
            print("ID invalide. Réessayez.")
        except ValueError:
            print("Veuillez entrer un nombre entier.")

def show_commands(connected: int) -> None:
    os.system('clear')
    print("\n" + "=" * 64)
    print("                    MENU DES COMMANDES")
    print("=" * 64)
    if connected == 0:
        print("  Session")
        print("   - connexion       : se connecter")
        print("   - inscription     : s'inscrire")
        print("   - quitter         : quitter l'application")
    else:
        print("  Utilisateur")
        print("   - profil          : voir votre profil")
        print("   - historique      : voir vos transactions")
        print("   - classement      : voir le leaderboard (top 10)")
        print("   - actifs          : résumés dans >= 3 matières")
        print("   - inactifs        : jamais publié de résumé")
        print("   - gros_depensiers : utilisateurs en déficit de points")
        print("")
        print("  Cours & Résumés")
        print("   - liste           : lister les cours")
        print("   - ajouter         : ajouter un cours")
        print("   - publier         : publier un résumé")
        print("   - consulter       : résumés publics d'un cours")
        print("   - mes_resumes     : vos résumés d'un cours")
        print("   - noter           : noter un résumé")
        print("   - modifier        : modifier un de vos résumés")
        print("   - supprimer       : supprimer un de vos résumés")
        print("   - telecharger     : télécharger un résumé")
        print("   - meilleurs       : top résumés par cours")
        print("   - top_cours       : cours avec le + de résumés")
        print("   - moyenne         : moyenne de résumés par auteur")
        print("")
        print("  Boutique")
        print("   - boutique        : catalogue et achat d'objets")
        print("   - inventaire      : voir vos objets")
        print("   - top_objet       : objet le plus acheté")
        print("   - activer_titre   : activer un titre possédé")
        print("   - activer_badge   : activer un badge possédé")
        print("")
        print("  Session")
        print("   - deconnexion     : se déconnecter")
        print("   - quitter         : quitter l'application")
    print("=" * 64)


# --- Command handlers ---

def cmd_register():
    email = input("Email : ")
    username = input("Utilisateur : ")
    password = getpass("Mot de passe : ")
    return register(username, password, email)

def cmd_login():
    username = input("Utilisateur : ")
    password = getpass("Mot de passe : ")
    return login(username, password)

def cmd_add_course() -> None:
    while True:
        mnemonic = input("Mnémonique : ").strip().upper()
        if mnemonic.isalnum():
            break
        print("Le mnémonique ne peut contenir que des lettres et des chiffres.")
    name = ask_non_empty("Nom : ", "Le nom ne peut pas être vide.")
    faculty = ask_non_empty("Faculté : ", "La faculté ne peut pas être vide")
    credits = ask_positive_int("Crédits : ")
    add_course(mnemonic, name, faculty, credits)

def cmd_profil(user) -> None:
    print(f"\n{user}")
    active_badges = get_active_badges(user.get_id())
    if active_badges:
        print("Badges actifs: ")
        for badge in active_badges:
            print(f"  - {badge['Name']}")
    else:
        print("Badges actifs: Aucun")

def cmd_publish(user) -> bool:
    while True:
        entry = input("Mnémonique : ").strip()
        if entry.lower() == "annuler":
            return False
        mnemonic = entry.upper()
        if get_course_by_mnemonic(entry):
            break
        print(f"Le cours '{entry}' n'existe pas dans la table 'Course', réessayez.")
        print("Tapez 'annuler' pour revenir.")
    title = ask_non_empty("Titre : ", "Le titre ne peut pas être vide.")
    desc = ask_non_empty("Description : ", "La description ne peut pas être vide.")
    while True:
        visibility = input("Visibilité (public, restricted, par défaut = private) : ")
        if visibility == "":
            visibility = "private"
            break
        if visibility in ("public", "restricted", "private"):
            break
        print("Valeur invalide. Choisissez : public, restricted ou private.")
    while True:
        file_path = input("Entrez le chemin du fichier : ").strip()
        if file_path == "annuler":
            return False
        if os.path.isfile(file_path):
            break
        print(f"Fichier introuvable : {file_path}. Réessayez.")
        print("Tapez 'annuler' pour revenir.")
    if publish_summary(user.get_id(), mnemonic, title, desc, file_path, visibility):
        user.reload_user()
        print("Résumé publié !")
    else:
        print("Échec de la publication.")
    return True

def cmd_view_course_summaries() -> bool:
    mnemonic = ask_mnemonic()
    if mnemonic is None:
        return False
    print_structured_list(get_course_summaries(mnemonic), f"Résumés du cours {mnemonic}")
    return True

def cmd_my_summaries(user) -> bool:
    mnemonic = ask_mnemonic()
    if mnemonic is None:
        return False
    print_structured_list(get_course_summaries(mnemonic, user.get_id()), f"Mes résumés du cours {mnemonic}")
    return True

def cmd_rate_summary(user) -> bool:
    mnemonic = ask_mnemonic()
    if mnemonic is None:
        return False
    list_course = get_course_summaries(mnemonic)
    print_structured_list(list_course, f"Résumés à noter ({mnemonic})")
    if not list_course:
        return True
    summary_id = ask_id_from_list(list_course, "SID", "ID du résumé que vous voulez noter : ")
    rate = ask_bounded_int("Note (0-5) : ", 0, 5)
    comment = ask_non_empty("Commentaire : ", "Le commentaire ne peut pas être vide")
    rate_summary(user.get_id(), summary_id, rate, comment)
    return True

def cmd_activate_title(user) -> None:
    titles = get_owned_items(user.get_id())
    print_structured_list(titles, "Mes titres")
    if titles:
        item_id = ask_id_from_list(titles, "OID", "ID du titre que vous voulez activer : ")
        if activate_title(user.get_id(), item_id):
            user.reload_user()

def cmd_activate_badge(user) -> None:
    badges = get_owned_badges(user.get_id())
    print_structured_list(badges, "Mes badges")
    if badges:
        item_id = ask_id_from_list(badges, "OID", "ID du badge que vous voulez activer : ")
        if activate_badge(user.get_id(), item_id):
            user.reload_user()

def cmd_shop(user) -> None:
    shop_items = get_shop_items()
    print_structured_list(shop_items, "Boutique")
    if ask_yes_no("Voulez vous acheter un objet ? (o/n) : "):
        item_id = ask_id_from_list(shop_items, "OID", "ID de l'objet que vous voulez acheter : ")
        if buy_item(user.get_id(), item_id):
            user.reload_user()
            print("Objet acheté avec succès !")
        else:
            print("Vous n'avez pas assez de points pour acheter cet objet.")
    else:
        print("Vous n'avez pas acheté d'objet.")

def cmd_download_summary(user) -> None:
    summary_id = ask_int("ID du résumé que vous voulez télécharger : ")
    exists = execute_select_one("SELECT SID FROM Summary WHERE SID = %s", (summary_id,))
    if not exists:
        print("Ce résumé n'existe pas.")
    else:
        download_path = input("Entrez le chemin de destination (par défaut : dossier courant) : ")
        download_summary(summary_id, user.get_id(), download_path)

def cmd_edit_summary(user) -> None:
    my_summaries = get_own_summaries(user.get_id())
    print_structured_list(my_summaries, "Mes résumés")
    if my_summaries:
        summary_id = ask_id_from_list(my_summaries, "SID", "ID du résumé que vous voulez modifier : ")
        new_title = input("Nouveau titre : ")
        new_desc = input("Nouvelle description : ")
        update_summary(summary_id, user.get_id(), new_title, new_desc)

def cmd_delete_summary(user) -> None:
    my_summaries = get_own_summaries(user.get_id())
    print_structured_list(my_summaries, "Mes résumés")
    if my_summaries:
        summary_id = ask_id_from_list(my_summaries, "SID", "ID du résumé que vous voulez supprimer : ")
        delete_summary(summary_id, user.get_id())


def main():
    is_active = True
    connected = 0
    current_user = None

    not_connected_dispatch = {
        CMD_REGISTER: cmd_register,
        CMD_LOGIN:    cmd_login,
    }

    connected_dispatch = {
        CMD_LIST_COURSES:           lambda: print_structured_list(get_list_courses(), "Liste des cours"),
        CMD_ADD_COURSE:             cmd_add_course,
        CMD_PROFIL:                 lambda: cmd_profil(current_user),
        CMD_PUBLISH:                lambda: cmd_publish(current_user),
        CMD_VIEW_COURSE_SUMMARIES:  cmd_view_course_summaries,
        CMD_MY_SUMMARIES:           lambda: cmd_my_summaries(current_user),
        CMD_RATE_SUMMARY:           lambda: cmd_rate_summary(current_user),
        CMD_INVENTORY:              lambda: print_structured_list(get_inventory(current_user.get_id()), "Mon inventaire"),
        CMD_ACTIVATE_TITLE:         lambda: cmd_activate_title(current_user),
        CMD_ACTIVATE_BADGE:         lambda: cmd_activate_badge(current_user),
        CMD_SHOP:                   lambda: cmd_shop(current_user),
        CMD_HISTORY:                lambda: print_structured_list(get_history(current_user.get_id()), "Historique"),
        CMD_LEADERBOARD:            lambda: print_structured_list(get_leaderboard(), "Classement Top 10"),
        CMD_LIST_ACTIVE_USERS:      lambda: print_structured_list(get_active_users(), "Utilisateurs actifs (>= 3 matières)"),
        CMD_DOWNLOAD_SUMMARY:       lambda: cmd_download_summary(current_user),
        CMD_EDIT_SUMMARY:           lambda: cmd_edit_summary(current_user),
        CMD_DELETE_SUMMARY:         lambda: cmd_delete_summary(current_user),
        CMD_LIST_INACTIVE_USERS:    lambda: print_structured_list(get_inactive_users(), "Utilisateurs qui n'ont pas publié"),
        CMD_TOP_SUMMARIES:          lambda: print_structured_list(get_top_rated_summaries(), "Meilleurs résumés par cours"),
        CMD_TOP_COURSE:             lambda: print_structured_list(get_top_course(), "Cours avec le plus de résumés"),
        CMD_AVG_SUMMARIES_PER_USER: lambda: print_structured_list(get_average_summary_per_user(), "Nombre moyen de résumés publiés par utilisateur"),
        CMD_TOP_ITEM:               lambda: print_structured_list(get_top_item(), "Objet cosmétique le plus acheté"),
        CMD_HIGH_SPENDERS:          lambda: print_structured_list(get_high_spenders(), "Utilisateurs ayant dépenses > solde actuel"),
    }

    while is_active:
        show_commands(connected)
        request = input("Votre commande > ").strip().lower()
        show_pause = True

        if request == CMD_EXIT:
            is_active = False
            show_pause = False
            connection.close()
            print("Au revoir !")
        elif request == CMD_DISCONNECTION:
            current_user = None
            connected = 0
            print("Déconnecté avec succès")
        elif connected == 1:
            handler = connected_dispatch.get(request)
            if handler:
                if handler() is False:
                    show_pause = False
            else:
                print("Commande invalide.")
        else:
            handler = not_connected_dispatch.get(request)
            if handler:
                result = handler()
                if result is not None:
                    current_user = result
                    connected = 1
            else:
                print("Commande invalide.")

        if is_active and show_pause:
            input("\nAppuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        connection.close()
        print("\nAu revoir !")
