import subprocess
import os
import sqlite3
from database import DB_NAME, imprimir_ips

def ping_ip(ip):
    try:
        ping_command = ["ping", "-n", "1", ip] if os.name == 'nt' else ["ping", "-c", "1", ip]
        output = subprocess.check_output(ping_command, universal_newlines=True)
        if "TTL=" in output:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False

def pingar_ips():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "SELECT id, ip FROM dispositivos ORDER BY id"
        cursor.execute(query)
        dispositivos = cursor.fetchall()
        for id, ip in dispositivos:
            if not ping_ip(ip):
                print(f"IP {ip} não está respondendo.")
                cursor.execute("UPDATE dispositivos SET status = 'não respondendo' WHERE id = ?", (id,))
            else:
                cursor.execute("UPDATE dispositivos SET status = 'respondendo' WHERE id = ?", (id,))
            conn.commit()
    except sqlite3.Error as err:
        print(f"Erro: {err}")
    finally:
        cursor.close()
        conn.close()

    # Imprimir IPs após pingar
    imprimir_ips()
