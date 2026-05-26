import os

from config import *
from helpers import *
from users import *
from courses import *
from summaries import *
from shop import *


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
        print("   - quitter         : quitter l'application")
    print("=" * 64)


def main():
    is_active = True
    connected = 0
    while is_active:
        show_commands(connected)
        request = input("Votre commande > ").strip().lower()
        show_pause = True

        if connected == 0:
            if request == CMD_REGISTER:
                email = input("Email : ")
                username = input("Utilisateur : ")
                password = input("Mot de passe : ")
                current_user = register(username, password, email)
                if current_user is not None:
                    connected = 1
            elif request == CMD_LOGIN:
                username = input("Utilisateur : ")
                password = input("Mot de passe : ")
                current_user = login(username, password)
                if current_user is not None:
                    connected = 1
        elif request == CMD_LIST_COURSES and connected == 1:
            print_structured_list(get_list_courses(), "Liste des cours")
        elif request == CMD_ADD_COURSE and connected == 1:
            mnemonic = input("Mnémonique : ").strip().upper()
            name = input("Nom : ")
            faculty = input("Faculté : ")
            credit = int(input("Crédits : "))
            add_course(mnemonic, name, faculty, credit)
        elif request == CMD_PROFIL and connected == 1:
            print(f"\n{current_user}")
            active_badge = get_active_badge(current_user.get_id())
            if active_badge:
                print(f"Badge actif: {active_badge['Symbol']} {active_badge['Name']}")
            else:
                print("Badge actif: Aucun")
        elif request == CMD_PUBLISH and connected == 1:
            mnemonic = input("Mnémonique : ").strip().upper()
            if not get_course_by_mnemonic(mnemonic):
                print(f"Le cours '{mnemonic}' n'existe pas dans la table Course.")
                continue
            title = input("Titre : ")
            desc = input("Description : ")
            visibility = input("Visibilité (public, restricted, par défaut = private) : ")
            if visibility == "":
                visibility = "private"
            file_path = input("Entrez le chemin du fichier : ")
            if publish_summary(current_user.get_id(), mnemonic, title, desc, file_path, visibility):
                current_user.reload_user()
                print("Résumé publié !")
            else:
                print("Échec de la publication")
        elif request == CMD_VIEW_COURSE_SUMMARIES and connected == 1:
            mnemonic = input("Mnémonique du cours : ").strip().upper()
            print_structured_list(get_course_summaries(mnemonic), f"Résumés du cours {mnemonic}")
        elif request == CMD_MY_SUMMARIES and connected == 1:
            mnemonic = input("Mnémonique du cours : ").strip().upper()
            print_structured_list(get_course_summaries(mnemonic, current_user.get_id()), f"Mes résumés du cours {mnemonic}")
        elif request == CMD_RATE_SUMMARY and connected == 1:
            mnemonic = input("Mnémonique du cours : ").strip().upper()
            list_course = get_course_summaries(mnemonic)
            print_structured_list(list_course, f"Résumés à noter ({mnemonic})")
            summary_id = int(input("ID du résumé que vous voulez noter : "))
            if summary_id not in [int(item["SID"]) for item in list_course]:
                print("Résumé invalide.")
                continue
            rate = int(input("Note : "))
            comment = input("Commentaire : ")
            rate_summary(current_user.get_id(), summary_id, rate, comment)
        elif request == CMD_INVENTORY and connected == 1:
            print_structured_list(get_inventory(current_user.get_id()), "Mon inventaire")
        elif request == CMD_ACTIVATE_TITLE and connected == 1:
            titles = get_owned_items(current_user.get_id())
            print_structured_list(titles, "Mes titres")
            if not titles:
                continue
            item_id = input("ID du titre que vous voulez activer : ").strip()
            if activate_title(current_user.get_id(), item_id):
                current_user.reload_user()
        elif request == CMD_ACTIVATE_BADGE and connected == 1:
            badges = get_owned_badges(current_user.get_id())
            print_structured_list(badges, "Mes badges")
            if not badges:
                continue
            item_id = input("ID du badge que vous voulez activer : ").strip()
            activate_badge(current_user.get_id(), item_id)
        elif request == CMD_SHOP and connected == 1:
            shop_items = get_shop_items()
            print_structured_list(shop_items, "Boutique")
            choice = input("Voulez vous acheter un objet ? (o/n) : ")
            if choice == "o":
                item_id = int(input("ID de l'objet que vous voulez acheter : "))
                if item_id < 0 or item_id > len(shop_items):
                    print("Objet invalide")
                    continue
                if buy_item(current_user.get_id(), item_id):
                    current_user.reload_user()
                    print("Objet acheté avec succès !")
                else:
                    print("Vous n'avez pas assez de points pour acheter cet objet")
            else:
                print("Vous n'avez pas acheté d'objet")
        elif request == CMD_HISTORY and connected == 1:
            print_structured_list(get_history(current_user.get_id()), "Historique")
        elif request == CMD_LEADERBOARD and connected == 1:
            print_structured_list(get_leaderboard(), "Classement Top 10")
        elif request == CMD_LIST_ACTIVE_USERS and connected == 1:
            print_structured_list(get_active_users(), "Utilisateurs actifs (>= 3 matières)")
        elif request == CMD_DOWNLOAD_SUMMARY and connected == 1:
            summary_id = int(input("ID du résumé que vous voulez lire : "))
            download_path = input("Entrez le chemin de destination (par défaut : dossier courant) : ")
            download_summary(summary_id, current_user.get_id(), download_path)
        elif request == CMD_EDIT_SUMMARY and connected == 1:
            my_summaries = get_own_summaries(current_user.get_id())
            print_structured_list(my_summaries, "Mes résumés")
            if not my_summaries:
                continue
            summary_id = int(input("ID du résumé que vous voulez modifier : "))
            sid_exists = any(str(item.get("SID")) == str(summary_id) for item in my_summaries)
            if not sid_exists:
                print("Résumé invalide")
                continue
            new_title = input("Nouveau titre : ")
            new_desc = input("Nouvelle description : ")
            update_summary(summary_id, current_user.get_id(), new_title, new_desc)
        elif request == CMD_DELETE_SUMMARY and connected == 1:
            my_summaries = get_own_summaries(current_user.get_id())
            print_structured_list(my_summaries, "Mes résumés")
            if not my_summaries:
                continue
            summary_id = int(input("ID du résumé que vous voulez supprimer : "))
            sid_exists = any(str(item.get("SID")) == str(summary_id) for item in my_summaries)
            if not sid_exists:
                print("Résumé invalide")
                continue
            delete_summary(summary_id, current_user.get_id())
        elif request == CMD_LIST_INACTIVE_USERS and connected == 1:
            inactive_users = get_inactive_users()
            print_structured_list(inactive_users, "Utilisateurs qui n'ont pas publié")
        elif request == CMD_TOP_SUMMARIES and connected == 1:
            top_summaries = get_top_rated_summaries()
            print_structured_list(top_summaries, "Meilleurs résumés par cours")
        elif request == CMD_TOP_COURSE and connected == 1:
            top_course = get_top_course()
            print_structured_list(top_course, "Cours avec le plus de résumés")
        elif request == CMD_AVG_SUMMARIES_PER_USER and connected == 1:
            avg_result = get_average_summary_per_user()
            print_structured_list(avg_result, "Nombre moyen de résumés publiés par utilisateur")
        elif request == CMD_TOP_ITEM and connected == 1:
            top_item = get_top_item()
            print_structured_list(top_item, "Objet cosmétique le plus acheté")
        elif request == CMD_HIGH_SPENDERS and connected == 1:
            high_spenders = get_high_spenders()
            print_structured_list(high_spenders, "Utilisateurs ayant dépenses > solde actuel")
        elif request == CMD_EXIT:
            is_active = False
            show_pause = False
            connection.close()
            print("Au revoir !")
        elif connected == 0:
            print("Veuillez vous connecter")
            show_pause = False
        else:
            print("Aucune commande n'a été spécifiée")
            show_pause = False
        if is_active and show_pause:
            input("\nAppuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    main()
