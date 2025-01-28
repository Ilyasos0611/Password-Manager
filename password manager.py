import random
import string
import re
import os
from datetime import datetime

"""verifier_login permet de vérifier si le login passé en argument est déjà existant sur login.txt, et dans ce cas là, la fonction retourne la ligne."""
def verifier_login(login):
    login_pattern = r"Login:\s*([^,]+)"#modèle à trouver
    with open("logins.txt", "r") as fichier:  # Ouvre le fichier en mode lecture
            for line in fichier:#parcourt toutes les lignes
                login_match = re.search(login_pattern, line)#cherche la pattern voulu dans la ligne
                if login_match:#si un pattern est trouvé
                    login_list = login_match.group(1)#gardons que l'ID sans espace
                    if login_list == login:#s'il correspond à l'ID donné en argument
                        return line #afin qu'on modifie directement le mot de passe
                    
"""Cette fonction nous permet de modifier la ligne avec le login dans login.txt ou dans le cas où il n'existe pas l'ajouter au fichier txt"""                
def add_mod_mdp(crypté, login, line, cryptage, label):
    password_pattern = r"Password:\s*.+"#modèle du mot de passe à trouver
    label_pattern = r"Label:\s*.*?(?=,)"#modèle du label à trouver
    date_depot = datetime.now().strftime("%Y-%m-%d %H:%M:%S")#permet d'avoir la date actuelle
    if cryptage == "c":
        mention = "(CESAR)"#ici on décrypte en fonction du type de cryptage
    else:  
        mention = "(RSA)"
    label_str = " / ".join(label)#vu que label passé en argument est une liste, on utilise ça pour le transformer en chaîne de caractères et dans le cas où on a deux label les séparer par un /
    with open("history.txt", "a") as fichier:#on ouvre history.txt en mode "ajouter"
        fichier.write(f"Label: {label_str}, Login: {login}, Password: {crypté}, Date: {date_depot} {mention}\n")
    if line:#si line contient quelque chose
        with open("logins.txt", "r+") as fichier:#on ouvre login.txt en mode lecture et écriture
                lines = fichier.readlines()  # Lire toutes les lignes du fichier
                fichier.seek(0)  # Retour au début du fichier pour réécriture
                fichier.truncate()  # Truncate le fichier pour supprimer tout excédent de données
                fichier.writelines([
                    re.sub(password_pattern, f"Password: {crypté} {mention}", 
                    re.sub(label_pattern, f"Label: {' / '.join(label)}", l)) if line in l else l 
                    for l in lines
                ])# dans le cas où le login est déjà dans le fichier txt, on réecris en modifiant la ligne en question
                
                fichier.seek(0, 2)#on met le curseur à la fin du document(facultatif)
    else:#dans le cas ou line est vide
        with open("logins.txt", "a") as fichier:#on ouvre login.txt en mode "ajouter"
            fichier.write(f"Label: {label_str}, Login: {login}, Password: {crypté} {mention}\n")# et on ajoute la ligne avec le nouveau login
    print("Mot de passe ajouté avec succès dans le fichier !") # rassure l'utilisateur

"""cette fonction permet de restaurer une version antérieure du mot de passe à l'aide du login"""
def restaurer_mdp(login):
    with open("history.txt", "r") as fichier:# on ouvre history.txt en mode lecture
        lignes = fichier.readlines()#on lit toutes les lignes
        for ligne in lignes:#on itère dans les differentes lignes
            if f"Login: {login}" in ligne:#si le login est trouvé
                print(ligne)  # Afficher toutes les lignes correspondantes
        if not any(f"Login: {login}" in ligne for ligne in lignes):#si le login n'est pas trouvé dans une ligne
            print(f"Le login n'a pas été trouvé.")#on affiche cela
            return#et on sort immédiatement de la fonction
        date_souhaitee = input("Entrez la date du mot de passe à restaurer (format : 2024-12-23 13:51:27) : ")#on demande à l'utilisateur la date afin qu'on sache quel version du mdp il veut utiliser
        
        # Trouver la ligne correspondante
        for ligne in lignes:#on itere dans les differentes lignes 
            if f"Login: {login}" in ligne and date_souhaitee in ligne:#Si on trouve le login et la date souhaite dans history.txt
                if "(CESAR)" in ligne:#s'il est crypté en césar
                    mention = "(CESAR)"#on affecte (CESAR) à mention
                elif "(RSA)" in ligne:#s'il est crypté en RSA
                    mention = "(RSA)"# on affecte (RSA) à mention
                match = re.search(r"Password:\s*(\[[^\]]+\]|[^\s,]+)", ligne)#on associe à match la mention Password: mdp
                label_match = re.search(r"Label:\s*([^,]+)", ligne)#on associe à label_match la mention Label: label
                mot_de_passe = match.group(1)#on ne garde que mdp
                label = label_match.group(1)#on ne garde que label
                break

    if mot_de_passe:
        with open("logins.txt", "r+") as fichier:#on ouvre login.txt en mode lecture et écriture
            lignes = fichier.readlines()#lignes correspond à toutes les lignes du fichier
            fichier.seek(0)#on remet le curseur au début du fichier
            modified = False# on affecte modified à false
            for i, line in enumerate(lignes):#on itère à travers les différentes lignes du fichier
                if f"Login: {login}" in line:#si on trouve la ligne avec le login
                    existing_password_match = re.search(r"Password:\s*(\[[^\]]+\]|[^\s,]+)", line)#on recherche le pattern Password: mdp (dans la ligne)
                    if existing_password_match and existing_password_match.group(1) == mot_de_passe:#si on a ce pattern et que le mot de passe que celui qu'on voulait restaurer
                        print(f"Le mot de passe pour {login} est déjà à jour. Aucune modification nécessaire.")#alors on affiche ça 
                        return  # Quitter immédiatement la fonction
                    lignes[i] = re.sub(r"Password:\s*(\[[^\]]+\]|[^\s,]+)", f"Password: {mot_de_passe}", line)#on modifie le mot de passe par l'ancienne version
                    lignes[i] = re.sub(r"Label:\s*[^,]+", f"Label: {label}", lignes[i])#on modifie le label par l'ancienne version
                    modified = True#on affecte True à modified
            if not modified:#dans le cas ou le mot de passe a été supprimé
                lignes.append(f"Label: {label}, Login: {login}, Password: {mot_de_passe} {mention}\n")#on ajoute tout simplement la ligne, en enlevant la date
            fichier.writelines(lignes)#puis on écrit lignes, ceci aura pour conséquence d'écraser ce qu'on avait dans login.txt
        print(f"Le mot de passe pour {login} a été restauré avec succès !")#on affiche ca
        with open("history.txt", "a") as fichier:#on ouvre history.txt en mode ajouter
            date_depot = datetime.now().strftime("%Y-%m-%d %H:%M:%S")#on affecte la date actuelle dans date_depot
            fichier.write(f"Label: {label}, Login: {login}, Password: {mot_de_passe}, Date: {date_depot} {mention}\n")#on stocke la donnée de connexion restaurée avec une nouvelle date

"""cette fonction permet de supprimer la ligne contenant le login en tout simplement le préciser"""
def supprimer_login(login):
    # Cherche si le login existe et récupère la ligne correspondante
    line = verifier_login(login)#on vérifie si le login existe déjà dans login.txt et dans ce cas là ou retourne la ligne qu'on affecte à line
    if line:#si line contient quelque chose
        # Si la ligne existe, on la supprime
        with open("logins.txt", "r+") as fichier:#on ouvre login.txt en mode écriture et lecture
            lines = fichier.readlines()  # Lire toutes les lignes du fichier
            # Remettre le curseur au début du fichier
            fichier.seek(0)
            fichier.truncate()  # Vider le contenu du fichier
            # Filtrer les lignes pour ne garder que celles qui ne correspondent pas aux lignes contenant le login à supprimer
            for ligne in lines:
                if ligne != line:
                    fichier.write(ligne)  # on réecrit toutes les lignes sauf celle contenant le login
        print(f"La ligne avec le login '{login}' a été supprimée.")
    else:#dans le cas où line est vide
        print(f"Aucun login trouvé pour '{login}'.")

"""cette fonction a pour but de définir la métrique de robustesse du mot de passe et le retourner uniquement s'il est reconnu comme excellent"""
def ajouter_password():
    # Ajoute un login et un mot de passe après vérification de la robustesse.
    while True:  # Boucle jusqu'à obtenir un mot de passe robuste
        mot_de_passe = input("Entrez le mot de passe : ")

        # Vérification de la robustesse du mot de passe
        length = len(mot_de_passe)#longueur mot de passe
        has_lowercase = any(lettre.islower() for lettre in mot_de_passe)#s'il contient une lettre miniscule
        has_uppercase = any(lettre.isupper() for lettre in mot_de_passe)#s'il contient une lettre majuscule
        has_digit = any(lettre.isdigit() for lettre in mot_de_passe)#s'il contient un nombre
        has_special = any(lettre in "!@#$%^&/~=+-*(),.?\":{}|<>" for lettre in mot_de_passe)#s'il contient un caractère spécial

        # Définir les niveaux de robustesse
        if length < 6:#si sa longueur est inférieur à 6
            print("FAIBLE : Le mot de passe contient moins de 6 caractères. Veuillez entrer un mot de passe plus long.")
        elif 6 <= length < 8:#s'il contient 6 ou 7 caractères
            if not (has_lowercase or has_digit or has_uppercase or has_special):#s'il ne contient pas un de ces types de caractères
                print("FAIBLE : Votre mot de passe ne contient aucun caractère varié. Ajoutez des majuscules, des chiffres ou des caractères spéciaux.")
            elif has_lowercase and not (has_uppercase or has_digit or has_special):#s'il contient uniquement des miniscules
                print("MOYEN : Le mot de passe contient des minuscules uniquement. Ajoutez des majuscules, chiffres ou caractères spéciaux.")
            elif has_digit and not (has_lowercase or has_uppercase or has_special):#s'il contient uniquement des nombres
                print("MOYEN : Le mot de passe contient des chiffres uniquement. Ajoutez des lettres ou des caractères spéciaux.")
            else:# dans le cas contraire, on affiche cela
                print("MOYEN : Ajoutez plus de variété et augmentez la longueur pour renforcer le mot de passe.")
        elif length >= 8:#si le mot de passe est supérieur ou égal à 8
            if has_lowercase and has_uppercase and has_digit and has_special:#s'il a les 4 types de caractères
                print("EXCELLENT : Mot de passe sécurisé.")
                return mot_de_passe  # Sortir de la boucle si le mot de passe est robuste
            elif has_lowercase and has_uppercase and has_digit:#s'il a ces 3 types de caractères
                print("FORT : Ajoutez des caractères spéciaux pour renforcer le mot de passe.")
            elif has_lowercase and has_uppercase:#s'il a ces deux types deux caractères
                print("FORT : Ajoutez des chiffres et des caractères spéciaux pour renforcer.")
            elif has_lowercase and has_digit:#s'il a ces deux types de caractères
                print("FORT : Ajoutez des majuscules et des caractères spéciaux pour renforcer.")
            elif has_uppercase and has_digit:#s'il a ces deux types de caractères
                print("FORT : Ajoutez des minuscules et des caractères spéciaux pour renforcer.")
            else:#autrement on affiche cela
                print("FORT : Le mot de passe pourrait être plus robuste. Ajoutez des caractères variés (majuscules, chiffres, caractères spéciaux, etc.).")
    

"""Le Code de César est une méthode de chiffrement où chaque lettre du message est décalée d’un certain nombre de positions dans l'alphabet."""
def cryptage_cesar(mot_de_passe):
    crypté = ""#on initialise crypté
    for char in mot_de_passe:#on itère à travers chaque caractère du mot de passe
        if char.isalpha():  # Si le caractère est une lettre
            decalage_base = 65 if char.isupper() else 97#Code ASCII pour "a" et "A"
            crypté += chr((ord(char) - decalage_base + 4) % 26 + decalage_base)  # modulo: Déplacement dans la plage des lettres(a et z/ A et Z)
        elif char.isdigit():  # Si le caractère est un chiffre
            decalage_base = 48  # Code ASCII pour '0'
            crypté += chr((ord(char) - decalage_base + 4) % 10 + decalage_base)  # modulo: Déplacement dans la plage des chiffres(0 à 9)/chr(ASCII en str)
        else:
            crypté += char  # Si ce n'est pas une lettre ni un chiffre, on laisse le caractère tel quel(ex :#)
    return crypté#on retourne le mot de passe en crypté

"""Cette fonction permet de décrypter un mot de passe crypté à l'aide de la fonction juste avent"""
def decryptage_cesar(mot_de_passe_crypte):
    mot_de_passe = ""
    for char in mot_de_passe_crypte:
        if char.isalpha():  # Si le caractère est une lettre
            decalage_base = 65 if char.isupper() else 97#Code ASCII pour "a" et "A"
            mot_de_passe += chr((ord(char) - decalage_base - 4) % 26 + decalage_base)  # Soustraction du décalage
        elif char.isdigit():  # Si le caractère est un chiffre
            decalage_base = 48  # Code ASCII pour '0'
            mot_de_passe += chr((ord(char) - decalage_base - 4) % 10 + decalage_base)  # Soustraction du décalage
        else:
            mot_de_passe += char  # Si ce n'est pas une lettre ni un chiffre, on laisse le caractère tel quel
    return mot_de_passe

"""cette fonction permet de crypter un argument sous la forme d'un tuple(la clé privée par ex) à l'aide du cryptage césar"""
def crypter_key(private):
    tpl_str = [str(element) for element in private]#une liste avec les deux éléments du tuple en format string 
    tpl_crypté = [cryptage_cesar(element) for element in tpl_str]#une liste avec les deux éléments du tuple en format string mais cette fois ci chaque numéro a un décalage
    return tuple(tpl_crypté)#le remettre en format tuple

"""cette fonction permet de décrypter un argument sous la forme d'un tuple à l'aide du décryptage césar"""
def decrypter_key(private_crypte):
    tpl_decrypte = [int(decryptage_cesar(element)) for element in private_crypte]#une liste avec deux nombres
    return tuple(tpl_decrypte)#le remettre en forme de tuple

"""cette fonction de vérifier si l'entrée de l'utilisateur matche avec la donnée en interne selon trois critères: login, label, mot de passe"""
def rechercher_afficher_lignes(critere, private_key):
    # Demander à l'utilisateur le choix du mot de passe (clair ou crypté) avant la boucle
    choix_mdp = input("Voulez-vous voir la ligne avec le mot de passe en (1) clair ou (2) crypté ? (1 ou 2) : ")
    # Demander à l'utilisateur le critère de recherche (login, label, ou mot de passe)
    if critere == '1':  # Recherche par Login
        recherche = input("Entrez le login à rechercher : ")
    elif critere == '2':  # Recherche par Label
        recherche = input("Entrez le label à rechercher : ")
    elif critere == '3':  # Recherche par Mot de Passe
        recherche = input("Entrez le mot de passe à rechercher : ")

    trouve = False  # Variable pour vérifier si une ligne a été trouvée

    with open("logins.txt", "r") as fichier:#on ouvre logins.txt en mode "lecture"
        for ligne in fichier:#on itère dans les différentes lignes du fichier
            if (critere == '1' and f"Login: {recherche}" in ligne) or \
               (critere == '2' and f"Label: {recherche}" in ligne):  #Si la recherche(label ou login) correspond et le critère correspond
                print_ligne_choisie(ligne, choix_mdp)#on affiche la ligne selon le choix de l'utilisateur
                trouve = True #pour prouver qu'on a trouvé
            elif critere == '3':  # Recherche par Mot de Passe
                match = re.search(r"Password: (.+)", ligne)#voici le pattern à trouver
                if match:#si la ligne contient ce pattern
                    mot_de_passe = match.group(1)#mot de passe = au premier terme suivant Password: 
                    mot_de_passe_decrypte = mot_de_passe  # Initialisation avec le mot de passe en clair
                    # Vérifier si le mot de passe est crypté en César ou RSA, puis on le décrypte
                    if "(CESAR)" in mot_de_passe:
                        mot_de_passe_decrypte = decryptage_cesar(mot_de_passe.replace(" (CESAR)", ""))
                    elif "(RSA)" in mot_de_passe:
                        mot_de_passe_decrypte = décrypter_password(eval(mot_de_passe.replace(" (RSA)", "")), private_key)

                    if mot_de_passe_decrypte == recherche:#si le mot de passe decryptée est le même que l'entrée de l'utilisateur
                        print_ligne_choisie(ligne, choix_mdp)#on affiche en claire ou en cryptée
                        trouve = True#grâce à cela, on n'affiche pas aucun résultat

    if not trouve:
        print(f"Aucun résultat trouvé pour ce critère : {recherche}.")

"""cette fonction permet d'afficher soit la ligne en claire ou en crypté"""
def print_ligne_choisie(ligne, choix_mdp):
    # Extraire le mot de passe de la ligne
    match = re.search(r"Password: (.+)", ligne)#trouver le pattern du password dans la ligne
    if match:#si on trouve
        mot_de_passe = match.group(1)#on ne garde que le mot de passe
        # Vérifier si le mot de passe est crypté en César ou RSA
        if "(CESAR)" in mot_de_passe:#si mention césar
            mot_de_passe_decrypte = decryptage_cesar(mot_de_passe.replace(" (CESAR)", ""))#on décrypte avec CESAR
        elif "(RSA)" in mot_de_passe:#si mention RSA 
            mot_de_passe_decrypte = décrypter_password(eval(mot_de_passe.replace(" (RSA)", "")), private_key)#on decrypte avec RSA
        # Afficher selon le choix de l'utilisateur
        if choix_mdp == '1':  # Afficher le mot de passe en clair
            ligne_claire = ligne.replace(mot_de_passe, mot_de_passe_decrypte).replace(" (RSA)", "").replace(" (CESAR)", "")#on remplace le mot de passe par le mot de passe décrypté et on enlève les mentions (RSA) et (CESAR)
            print(ligne_claire.strip())#puis on l'affiche
        elif choix_mdp == '2':  # Afficher le mot de passe crypté
            print(ligne.strip())#on affiche la ligne comme telle
        else:
            print("Choix invalide. Affichage de la ligne avec le mot de passe crypté par défaut.")#si l'utilisateur met autre chose
            print(ligne.strip())#on affiche simplement la ligne en crypté

"""Cette fonction est capable de créer des mots de passe selon 4 critères:longueur souhaitée, types de caractères souhaités, utilisation des  mots du dictionnaire et robustesse désirée"""
def generer_mot_de_passe():
    robustesse = ""#pour initialiser la boucle

    while robustesse not in ['faible', 'moyenne', 'forte']:#tant que l'utilisateur n'entre pas un choix valide
        robustesse = input("\nChoisissez la robustesse du mot de passe ('faible', 'moyenne', 'forte') : ").strip().lower()#on lui redemande d'insérer la robustesse

    while True:
        try:#dans le cas ou l'utilisateur rentre un nombre
            #ici on définit la métrique de robustesse pour le générateur
            if robustesse == "faible":
                longueur = int(input("Entrez la longueur souhaitée pour le mot de passe (entre 8 et 10) : "))
                if longueur >= 8:
                    break
            elif robustesse == "moyenne":
                longueur = int(input("Entrez la longueur souhaitée pour le mot de passe (entre 10 et 13) : "))#ajouter la fonctionnalité d'ajouter 2 mdp
                if 10 <= longueur <= 13:
                    break
            elif robustesse == "forte":
                longueur = int(input("Entrez la longueur souhaitée pour le mot de passe (entre 14 et 16) : "))
                if 14 <= longueur <= 16:
                    break
            else:#dans le cas où l'utilisateur ne respecte pas la longueur
                print("Veuillez respecter la longueur demandée. ")
        except ValueError:#dans le cas ou l'utilisateur entre des lettres et des caractères spéciaux
            print("Veuillez entrer un nombre valide.")

    #Ceci est un dictionnaire, pour chaque clé, la valeur est une chaine de caractères avec les caractères correspondants
    caracteres_types = {
        "min": string.ascii_lowercase,
        "maj": string.ascii_uppercase,
        "num": string.digits,
        "spec": string.punctuation,
    }

    print("\nTypes de caractères à inclure :")
    print("  'min' - minuscules, 'maj' - majuscules, 'num' - chiffres, 'spec' - caractères spéciaux")
    while True:#tant qu'on a aucune valeur dans in_caracteres_types
        types_caracteres = input("Entrez les types de caractères séparés par une virgule (exemple : num,spec) : ").strip().split(',')
        in_caracteres_types = [tc.strip() for tc in types_caracteres if tc.strip() in caracteres_types]#Ici on filtre en ne laissant que les types de caractères présents dans caracteres_types

        if in_caracteres_types:#s'il contient des valeurs
            break#on sort de la boucle
        print("Vous devez inclure au moins un type de caractères valide.")#autrement on affiche cela
    
    # 3. Inclure des mots mémorables du dictionnaire
    with open("dictionnaire.csv", "r", encoding='utf-8') as fichier:#on ouvre dictionnaire.csv en mode "lecture", on fait l'encoding afin qu'on puisse lire les caractères spéciaux et les accents
        lignes = fichier.readlines()#correspond à toutes les lignes du fichier
        # Créer une seule liste de mots, en supprimant les virgules et en divisant par les espaces, afin d'y inclure tout les mots du dictionnaire
        mots_dictionnaire = [mot.strip(",") for ligne in lignes for mot in ligne.strip().split()]
    #on ne laisse que les mots qui ont la longueur parfaite, une fois qu'on soustrait les caractères à inclure
    mots_possibles = [mot for mot in mots_dictionnaire if len(mot) == longueur - len(in_caracteres_types)]
   
    if set(in_caracteres_types) == {"maj"} or set(in_caracteres_types) == {"min", "maj"}:#dans le cas ou l'input de l'utilisateur est (min,maj) ou maj
        mots_possibles = [mot for mot in mots_dictionnaire if len(mot) == longueur]#on a pas de caractères supplémentaires à inclure
    elif set(in_caracteres_types) == {"min"}:#dans le cas ou l'input de l'utilisateur est min
        mots_possibles = [mot.lower() for mot in mots_dictionnaire if len(mot) == longueur]#de même

    #True or False
    utiliser_dictionnaire = input("\nVoulez-vous inclure des mots mémorables du dictionnaire (oui/non) ? [si oui il y'aura par défaut des caractères majuscules et miniscules] ").strip().lower() == 'oui'

    mot_de_passe = ""#on initialise
    valeurs_selectionnees_dic = {tc : caracteres_types[tc] for tc in in_caracteres_types if tc not in ["min", "maj"]}#on enlève "min" et "maj" car ils sont par défaut inclus dans les mots du dictionnaire
    valeurs_selectionnees = {tc : caracteres_types[tc] for tc in in_caracteres_types}

    if utiliser_dictionnaire:#si renvoie True
        mot_dictionnaire = random.choice(mots_possibles)#on choisit un mot de passe dans la liste
        mot_de_passe += mot_dictionnaire#mot de passe est dictionnaire
        longueur -= len(mot_dictionnaire)#longueur restante pour les caractères
        # Assure que chaque type de caractère est représenté au moins une fois
        while longueur > 0:
            for char_set in valeurs_selectionnees_dic.values():
                if longueur > 0:
                    mot_de_passe += random.choice(char_set)
                    longueur -= 1
    else:#si on utilise pas le dictionnaire
        while longueur > 0:
            for char_set in valeurs_selectionnees.values():#Donc on peut utilise les caractères "min" et "maj", plusieurs fois dans le mot de passe
                if longueur > 0:
                    mot_de_passe += random.choice(char_set)
                    longueur -= 1
    
    print("\nMot de passe généré :", mot_de_passe)#on ensuite dans les deux cas on affiche le mot de passe généré
    return mot_de_passe#on le renvoie pour le crypter

### Il est mieux expliqué sur la page wiki de RSA : https://en.wikipedia.org/wiki/RSA_(cryptosystem)
"""vérifie si le nombre est premier ou non"""
def est_prime(n):    
    if n <= 1:#un nombre inférieur à 1, ne peut pas être premier
        return False#donc, on retourne false
    for i in range(2, int(n ** 0.5) + 1):#car s'il est divisible, il est divisible par un nombre plus grand(c'est pour cela, on met la racine)
        if n % i == 0:#si le reste correspond à 0, on peut encore le diviser
            return False#il n'est donc pas premier
    return True#dans le cas contraire on a un nombre premier

"""Génération d'un nombre premier"""
def générer_prime(min_val, max_val): #dans quel intervalle, on veut notre nombre premier          
    while True:# tant qu'on ne trouve pas un nombre premier
        num = random.randint(min_val, max_val)
        if est_prime(num):                           # renvoie true : le nombre est premier
            return num                               #on renvoie donc le nombre en question

"""cette fonction permet de déterminer le plus grand diviseur commun de a et b"""
def pgcd(a, b):
    while b != 0:#tant que le reste n'est pas égal à 0, on peut encore le diviser
        reste = a % b#on affecte à reste, le reste de a/b
        a = b#on affecte à a la valeur de b
        b = reste#on affecte à b la valeur du reste, on fait un décalage horizontal
    return a#le pgcd



"""cette fonction permet de générer les clés publiques et clés privées"""
def générer_cles():
    p = générer_prime(100, 1000)  # Générer un nombre premier aléatoire p entre 100 et 1000
    q = générer_prime(100, 1000)  # Générer un nombre premier aléatoire q entre 100 et 1000
    n = p * q #on multiplie p par q                
    phi = (p - 1) * (q - 1)#on soustrait p et q de 1, et on les multiplie à nouveau  

    # Choisir e tel que 1 < e < phi et pgcd(e, phi) = 1
    # e est utilisé pour la clé publique afin de chiffrer
    e = random.randint(2, phi - 1)
    while pgcd(e, phi) != 1:#tant qu'il y a aucun diviseur entre eux à part 1, on choisit un autre e
        e = random.randint(2, phi - 1)
    
    # d est utilisé pour la clé privée afin de déchiffrer
    d = pow(e, -1, phi)    # puissance modulaire: (d * e) mod phi
    
    return (e, n), (d, n)  # Clés publique et privée

"""cette fonction permet de crypter en utilisant le chiffrage RSA(puissance modulaire)"""
def encrypter_password(password, public_key):#on y insère le mot de passe et la clé publique
    e, n = public_key#on affecte à e et n, les éléments du tuple public_key
    password_int = [ord(char) for char in password]      # liste avec les code ASCII des différentes caractères du mot de passe
    crypté = [pow(char, e, n) for char in password_int]  # on crypte password int avec la puissance modulaire
    return crypté#puis on retourne cette valeur, pour le décrypter plus tard

"""Cette fonction permet de décrypter le chiffrage RSA en utilisant la puissance modulaire"""
def décrypter_password(crypté_password, private_key):# on y insère le mot de passe crypté et la clé privée              
    d, n = private_key#on affecte à d et n, les éléments du tuple private_key
    décrypté = [chr(pow(char, d, n)) for char in crypté_password]  #fais l'inverse du cryptage puis transforme l'ASCII en lettres
    return ''.join(décrypté)# puis on rassemble les lettres(pour avoir une chaîne de caractères):c'est notre mot de passe

"""cette condition permet d'utiliser une clé publique et privée pour tout les mots de passe, et en même temps les protéger"""
if not os.path.exists("key.txt"):#si la clé n'existe pas dans le dossier
    public_key, private_key = générer_cles()#on génere les clès
    with open("key.txt", "w") as fichier:# On ouvre key.txt en mode "écriture"
        fichier.write(f"Public Key: {public_key}, Private Key: {crypter_key(private_key)} (CRYPTE)")#on écrit la clé publique et la clé privée dans le fichier txt
else:
    # Si le fichier existe déjà, ne rien faire
    pass

def extraire_cles():
    with open("key.txt", "r") as fichier:#on ouvre key.txt en mode "lecture"
        contenu = fichier.read()#on affecte contenu à la seule ligne du fichier
        match_private = re.search(r"Private Key: \('(\d+)', '(\d+)'\)", contenu)#on affecte match_private au pattern Private Key: mdp(dans le fichier txt)
        match_public = re.search(r"Public Key: \((\d+), (\d+)\)",contenu)#on fait de même pour la clé publique 
        private_key = match_private.group(1), match_private.group(2)#retourne uniquement le tuple(Private Key)
        public_key = int(match_public.group(1)), int(match_public.group(2))#on met les éléments en format nombre, car on va pas les décrypter plus tard
    return public_key, decrypter_key(private_key)#on retourne la clé publique et la clé privée décryptéé(grâce à la fonction vue précedemment)

public_key, private_key = extraire_cles()#on affecte public_key et private_key aux deux tuples retournées par extraire_cles afin de les utiliser dans toute la fonction menu

"""Cette fonction est le coeur du programme, elle permet de mettre en relation toutes les fonctions définies précedemment ,et dans le programme c'est la seule fonction qui est appellée"""
def menu():
    while True:
        print("\n--- Menu du Gestionnaire de Mots de Passe ---")
        print("1. Ajouter un mot de passe")
        print("2. Supprimer un mot de passe")
        print("3. Modifier un mot de passe")
        print("4. Chercher dans les données de connexion")
        print("5. Restaurer un ancien mot de passe")
        print("6. Quitter")
        
        choix = input("Entrez votre choix (1-6) : ").strip()#on demande à l'utilisateur de choisir une action
        
        if choix in ['1', '3']:#j'ai mis 1 et 3, car c'est globalement la même chose si on veut ajouter un login déjà existant, on le modifie(grâce à cela, on économise des ligne de code)
            A = True#on initialise la boucle suivante
            login = input("Entrez le login : ")
            line = verifier_login(login)#on retourne la ligne de login.txt, dans laquelle le login est déjà présent ou pas.
            labels = input("""
                Voici quelques exemples:
                1.🔒 Travail – Pour les comptes liés à l'entreprise
                2.🛒 Shopping – Pour les sites e-commerce
                3.🎮 Gaming – Pour les plateformes de jeux
                4.📧 Email – Pour différents fournisseurs de messagerie\n
                Vous pouvez entrer un ou plusieurs labels séparés par des virgules. Vous pouvez entrer ce que vous voulez : """
                ).strip()#travail, perso, gaming
            label_list = [label.strip() for label in labels.split(",")]#['travail', 'perso', 'gaming'], on fait une liste avec les différents labels choisis
            while A == True:#tant que A est vrai
                #on demande à l'utilisateur de générer ou d'entrer manuellement
                avec_ou_sans_gen = input("Veuillez choisir une option : entrez 'g' pour générer automatiquement un mot de passe sécurisé ou 'm' pour saisir manuellement votre mot de passe: ")
                if avec_ou_sans_gen == "m":#si "m", on utilise ajouter_password()
                    mdp = ajouter_password()
                elif avec_ou_sans_gen == "g":#si "g", on utilise generer_mot_de_passe() 
                    mdp = generer_mot_de_passe()
                else:
                    print("Entrez une valeur valide.")#dans le cas contraire, on demande d'entrer une valeur valide
                    continue# et on ignore le reste de la boucle
                while True:
                    #on demande à l'utilisateur de choisir le cryptage
                    cryptage = input("Veuillez choisir le chiffrement souhaité : saisissez 'c' pour le chiffrement utilisant le code César, ou 'r' pour le chiffrement RSA: ")
                    if cryptage == "c":
                        mdp_crypté = cryptage_cesar(mdp)#on crypte mdp avec le chiffrage césar
                        add_mod_mdp(mdp_crypté, login, line, cryptage, label_list)#puis on l'ajoute à history et login.txt
                        A = False#nous permet de ne pas recommencer la première boucle
                        break#et d'arrêter la deuxième boucle
                    elif cryptage == "r":
                        mdp_crypté = encrypter_password(mdp, public_key)#on crypte mdp avec le chiffrage RSA
                        add_mod_mdp(mdp_crypté, login, line, cryptage, label_list)#puis on l'ajoute à history et login.txt
                        A = False#nous permet de ne pas recommencer la première boucle
                        break#et d'arrêter la deuxième boucle
                    else:#rappeller à l'utilisateur d'entrer une lettre valide
                        print("veuillez entrer soit la lettre ""c"" soit la lettre ""r"" (en miniscule).")
        elif choix == '2':#dans le cas où on veut supprimer
            login = input("Veuillez entrer le login du mot de passe que vous souhaitez supprimer : ")#on demande à l'utilisateur le login
            supprimer_login(login)#puis on utilise la fonction pour le supprimer de login.txt
        elif choix == '4':#dans le cas où on veut rechercher une donnée de connexion
            critere = ""#on initialise critère pour lancer la boucle
            while critere not in ["1", "2", "3"]:#tant que l'utilisateur n'entre pas un choix valide, il recommence
                critere = input("""
                    Choisissez le critère de recherche :
                    1. Recherche par Login
                    2. Recherche par Label
                    3. Recherche par Mot de Passe
                    Entrez le numéro de votre choix (1, 2 ou 3) : """)
            rechercher_afficher_lignes(critere, private_key)#private_key est utilisé dans le cas on recherche avec un mot de passe chiffré en RSA
        elif choix == '5':#si l'utilisateur veut restaurer une ancienne version du mot de passe
            login = input("Veuillez entrer le login du mot de passe que vous souhaitez restaurer : ")#il entre le login
            restaurer_mdp(login)#puis le programme utilise la fonction définit précedemment
        elif choix == '6':#dans le cas où l'utilisateur veut quitter
            print("Au revoir !")
            break#on sort tout simplement de la boucle
        else:#dans le cas où l'utilisateur entre autre chose qu'un nombre de (1-6)
            print("Choix invalide. Veuillez entrer un nombre entre 1 et 6.")

# Lancer le programme
menu()