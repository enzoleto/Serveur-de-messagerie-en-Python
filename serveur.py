import socket
import threading
import os


# Pseudos réservés (interdits) premier test pour savoir si les pseudos déja pris renvoyait bien une erreur 
ps = {"admin", "enzo", "coucou"}
# Pseudos actuellement connectés
present = set()
NameSocket = {}
Roles = {}


#ici ma fonction prendra mon message chiffré en CEASER et le renverra déchiffré
def cesar(message, decalage):
    resultat = ""
    for caractere in message:
        if caractere.isalpha():
            base = ord('A') if caractere.isupper() else ord('a')
            # Décalage circulaire dans l'alphabet
            resultat += chr((ord(caractere) - base + decalage) % 26 + base)
        else:
            # On garde les caractères non alphabétiques tels quels
            resultat += caractere
    return resultat


def handle_client(client_socket):
    #chaque client arrivera en premier ici pour choisir son pseudo
    while True:
        
        data = client_socket.recv(1024) #on récupère ce que le client envoie
        #si il n'envoi plus rien il est donc déco
        if not data:
            print("Client déconnecté avant d'avoir choisi un pseudo")
            return
        #on décode le pseudo car les message s'envoie avec .encode()
        pseudo = data.decode().strip()
        #on regarde si les pseudo rentré meme en majuscule sont déja présent 
        if pseudo.lower() in ps :
            client_socket.sendall("Pseudo déjà pris, choisis-en un autre".encode())
        else:
            #sinon on stocke donc le nouveau socket du client dans la premiere liste socket pour pouvoir le récuperer plus tard pour lui adresser des messages mp ou all
            NameSocket[pseudo] = client_socket
            #on ajoute les pseudos a la liste des pseudos déja pris 
            ps.add(pseudo)
            if not present :
                #on donnera le role d'admin seulement au premier arrivé dans la salle
                Roles[pseudo] = "admin"
            else :
                Roles[pseudo] = "clampin"
                #liste en dessous est la liste des personne présent ou les ajoutes quand il se connecte et enlève quand il se deconnecte
            present.add(pseudo)  
            #si il a un bon pseudo et que tout se passe bien il reçoit son message de bienvenu
            client_socket.sendall(f"Bienvenue {pseudo}".encode())
            print(f"Le client {client_socket} utilise le pseudo : {pseudo}")
            break

    
    while True:
        #ici on passe sur la deuxième et dernière boucle qui va gérer les commandes
        data = client_socket.recv(1024)
        #on revérifie que le client envoie quelque chose de remplis sinon on le kick
        if not data:
            print(f"{pseudo} déconnecté")
            #evidemment quand on le deco on l'enelev des listes présent car c'est la liste qui gère qui est présent dans la salle
            present.discard(pseudo)
            ps.discard(pseudo)
            break

        message = data.decode().strip()
        #on printera chaque message reçu dans le terminal histoire de debug
        print(f"Message de {pseudo} : {message}")

        # Gestion des commandes
        if message.startswith("/"):
            if message == "/quit":
                #ici le /quit va donc deconnecter l'user en question avec son socket et l'enlever de toutes les listes
                present.discard(pseudo)
                ps.discard(pseudo)
                del NameSocket[pseudo]
                #si il n'y a plus personne on ferme le serveur sinon juste le client
                if not present :
                    client_socket.close()
                    s.close()
                    os._exit(0)
                else : 
                    client_socket.close()
                break
                #le plus simple , afficher tout les clients présents ,on retourne juste la liste en question
            elif message == "/users":
                client_socket.sendall(("Dans la salle il y a : " + str(present)).encode())






    #commande pour expulser
            elif message.startswith('/kick'):
                #seul l'admin peut expulser
                if Roles[pseudo] == "admin" : 
                    parts = message.split(' ', 1) 
                    #si il n'a pas utiliser assez d'argument on lui rapelle la commande
                    if len(parts) < 2:
                        client_socket.sendall("Utilisation: /Kick <message>".encode())
                    else:
                        #sinon on recupere le pseudo , on va chercher son socket , on liu envoie qu'il est kick et on le kick tout en l'enlevant bien de toutes les listes
                        msg_echo = parts[1]
                        client_scoktt = NameSocket.get(msg_echo)
                        client_scoktt.sendall("Vous avez etez Kick".encode())
                        present.discard(msg_echo)
                        ps.discard(msg_echo)
                        del NameSocket[msg_echo]
                        client_scoktt.close()
                        print(msg_echo)
                        client_socket.sendall("Vous avez bien viré ".encode())
                else :
                    #si il n'est pas admin on le prévient gentiment
                   client_socket.sendall("t'es pas admin sale fou".encode())








            #commande pour envoyer un message a tout le monde
            elif message.startswith('/echo') :               
                parts = message.split(' ', 1) 
                if len(parts) < 2:
                    client_socket.sendall("Usage: /echo <message>".encode())
                else:
                    #comme avant on sépare la commande du message a envoyer
                    msg_echo = parts[1]  
                    #on parcours donc la liste des socket et on envoie le message a tout le monde
                    for pseudo_dest, sock_dest in NameSocket.items():
                        try:
                            sock_dest.sendall(f"[TOUS] {pseudo} dit : {msg_echo}".encode())
                        except:
                            pass
                #commande pour envoyer un mp
            elif message.startswith('/mp'):
                parts = message.split(' ', 2)  # On limite à 2 séparations : /mp, user, message
                if len(parts) < 3:
                    # encore si pas assez d'argument on le lui rapelle 
                    print("Usage: /mp <user> <message>")
                else:
                    #sinon comme avant on separe la commande du message et du pseudo on va récuperer son socket eton lui adresse un message
                    dest, message = parts[1], parts[2]
                    socket = NameSocket.get(dest)  
                    #les message mp son chifrré en ceaser avec un decalage de 7 donc on déchiffre ici le message 
                    message  = cesar(message, -7)
                    socket.sendall(("[MP]" + pseudo + " t'a dit: " + message).encode())
            else:
                client_socket.sendall("Commande inconnue".encode())
        else:
            # Echo du message normal
            client_socket.sendall(f"Tu as dit: {message}".encode())

    client_socket.close()
    
 

#ici que début vraiment le projet on créer son socket sur l'adresse localhost et le port 12345
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 12345))
s.listen(3)
print("Serveur en écoute ")

while True:
    #donc on a une boucle et un thread pour envoyer chaque client sur ma fonction handle
    client_socket, client_address = s.accept()
    print(f"Nouvelle connexion depuis {client_address}")
    threading.Thread(target=handle_client, args=(client_socket,)).start()

