import socket
import threading
import os
#ici debut le fichier je tente de me connecter au serveur
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect(("127.0.0.1", 12345))
#fonction ceaser pour chiffrer mon messsage en decalant de 7 donc la fct prends en argument le message et de combien et decale 
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

# Thread pour lire en continu les messages du serveur
def receive_thread(sock):
    while True:
        try:
            data = sock.recv(1024)
            #si j'ai été kick je recvrai le premier message et j'arretreai le programme , pareil si je ne recois rien sinon j'affiche juste
            if data.decode() == "Vous avez etez Kick" :
                print("\nServeur déconnecté")
                os._exit(0) # <--- ici j'ai laisser os car avec sys j'avais des problèmes que je n'ai pas réussi a gérer
                break
            elif not data:
                print("\nServeur déconnecté")
                os._exit(0) # <--- pareil du coup
                break
            else : 
                print("\n" + data.decode())
        except:
            break

# Thread pour envoyer les messages
def send_thread(sock):
   
    while True: 
        #je recupere mon message que je veux envoyer et je le chiffre si ça commence par /mp et ensuite je l'envoie au serveur qui gerera a qui je l'envoi
        msg = input(">")
        if msg.startswith('/mp') :
            parts = msg.split(' ', 2)
            dest, message = parts[1] , parts[2]
            message = cesar(message, 7)
            sock.sendall(("/mp " + dest + " " + message ).encode()) 
        else : 
            sock.sendall(msg.encode())

#ma premiere boucle pour gerer si mon pseudo est invalide il me redemendera en boucle , si il est bon je recevrai binenvenu et donc je break
while True:
    msg = input("Choisissez un pseudo > ")
    c.sendall(msg.encode())
    data = c.recv(1024)
    if not data:
        print("Serveur déconnecté")
        c.close()
        exit()
    response = data.decode()
    print(response)
    if response.startswith("Bienvenue"):
        break  

# Lancer les threads d'envoi et réception un chacun car sinon au début il attendais que je recoive pour envoyer , une vrai galère

threading.Thread(target=receive_thread, args=(c,), daemon=True).start()
threading.Thread(target=send_thread, args=(c,), daemon=True).start()

# Bloquer le thread principal pour ne pas quitter
threading.Event().wait()
