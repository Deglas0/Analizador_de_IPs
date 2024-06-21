import re
import subprocess
import cv2
import sqlite3
import os


DB_DISPOSITIVOS = 'Dispositivos.db'

def teste_de_IPs(ip_informado):
    padrao_ip = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    if re.match(padrao_ip, ip_informado):
        octetos = ip_informado.split('.')
        if all(0 <= int(octeto) <= 255 for octeto in octetos):
            if int(octetos[-1]) == 0:
                return f'IP {ip_informado}: O último octeto não pode ser 0.'
            elif ip_informado.startswith('127.'):
                return f'IP {ip_informado}: 127.0.0.0 a 127.255.255.255 é reservado e não pode ser usado aqui.'
            else:
                return f'IP {ip_informado}: IP válido.'
        else:
            return f'IP {ip_informado}: IP informado não está dentro do intervalo permitido.'
    else:
        return f'IP {ip_informado}: Formato de IP inválido.'


def ping_ip(ip):
    try:
        ping_command = ["ping", "-n", "1", ip] if os.name == 'nt' else ["ping", "-c", "1", ip]
        output = subprocess.check_output(ping_command, universal_newlines=True)
        return "TTL=" in output
    except subprocess.CalledProcessError:
        return False


def pingar_ips():
    try:
        with sqlite3.connect(DB_DISPOSITIVOS) as conn:
            cursor = conn.cursor()
            query = "SELECT id, ip, camera FROM dispositivos ORDER BY id"
            cursor.execute(query)
            dispositivos = cursor.fetchall()
            for id, ip, camera in dispositivos:
                status = 'respondendo' if ping_ip(ip) else 'não respondendo'
                cursor.execute("UPDATE dispositivos SET status = ? WHERE id = ?", (status, id))
            conn.commit()
    except sqlite3.Error as err:
        print(f"Erro: {err}")


def verificar_camera(ip, id, is_camera):
    if is_camera == 'Não':
        return

    if is_camera == 'Desconhecido' or is_camera == 'Desativa':
        cap = cv2.VideoCapture(f"http://{ip}:4747/video")
    else:
        cap = cv2.VideoCapture(f"http://{ip}/video")

    with sqlite3.connect(DB_DISPOSITIVOS) as conn:
        cursor = conn.cursor()

        if not cap.isOpened():
            print(f"Não foi possível acessar a câmera com IP {ip}.")
            cursor.execute("UPDATE dispositivos SET camera = 'Desativa' WHERE id = ? AND camera != 'Não'", (id,))
            return False

        ret, frame = cap.read()
        if not ret or frame is None:
            print(f"Falha ao capturar imagem da câmera com IP {ip}.")
            cursor.execute("UPDATE dispositivos SET camera = 'Desativa' WHERE id = ? AND camera != 'Não'", (id,))
            return False

        print(f"Câmera com IP {ip} está transmitindo imagens.")
        cursor.execute("UPDATE dispositivos SET camera = 'Ativa' WHERE id = ?", (id,))
        cap.release()
        return True


