# Author : BAYRAKTAR Anthony & Marc Wilmot 3SI2
#!/usr/bin/env python3
import subprocess, platform, os, argparse, ipaddress

def get_os():
    if("Linux" in platform.system()):
        return "Linux"
    elif("Windows" in platform.system()):
        return "Windows"
    else:
        return "Inconnu"
    
def find_ipv4() :   #Fonction pour récupérer les ip d'un fichier
    ip_mask = {}
    current_ip = None

    with open('conf.txt', 'r') as fl:
        lines = fl.readlines()

        for line in lines:
            if "IPv4" in line :
                current_ip = line.split(":")[-1].strip() #Récupérer la ligne Ipv4 en gardant que l'ip avec split(":")[-1] et strip pour supprimer les espaces
            if "Masque de sous" in line :
                 mask = line.split(":")[-1].strip()
                 mask = ipaddress.IPv4Interface((0,mask)) #Transforme le masque en CIDR sous la forme (0.0.0.0/24)
                 mask = mask._prefixlen #Récupère seulement le masque CIDR
                 ip_mask[current_ip] = mask #Ajouter l'ip et le masque dans un dictionnaire
        
        return ip_mask

def get_ip_configuration(system):
    dir_path = 'C:\\Users\\Anthony\\Desktop\\Esgi\\Cours\\3emeAnnee\\s1\\python\\Keylogger'

    if "Linux" in system:
        conf = subprocess.run("ip a > conf.txt", shell=True)
        print("Les fichiers presents sont :")
        subprocess.run("ls", shell=True)
    elif "Windows" in system:
        conf = subprocess.check_output(f'ipconfig | findstr /i "ipv4 & masque" > {dir_path}\\conf.txt', shell=True)
        print("Les fichiers presents sont :")
        subprocess.run(f"dir /B {dir_path}", shell=True)
    else:
        return "Erreur : OS inconnu"
    
    ip_list = find_ipv4()

    return ip_list
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script will check the running system and recover ip.')
    args = parser.parse_args()
    os = get_os()
    print(f"Nous sommes sur un systeme : {os}")
    ip_config = get_ip_configuration(os)
    print(ip_config)


