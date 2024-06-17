import os
import subprocess
import sqlite3
from database_manager import DatabaseManager

class Network:
    @staticmethod
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

    @staticmethod
    def pingar_ips():
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            query = "SELECT id, ip, camera FROM dispositivos ORDER BY id"
            cursor.execute(query)
            dispositivos = cursor.fetchall()
            for id, ip, camera in dispositivos:
                if not Network.ping_ip(ip):
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
