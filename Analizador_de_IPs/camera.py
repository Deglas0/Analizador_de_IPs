import cv2
import sqlite3
import threading
from database import DB_NAME

def verificar_camera(ip):
    cap = cv2.VideoCapture(f"http://{ip}/video")
    if not cap.isOpened():
        print(f"Não foi possível acessar a câmera com IP {ip}.")
        return False
    ret, frame = cap.read()
    if not ret or frame is None:
        print(f"Falha ao capturar imagem da câmera com IP {ip}.")
        return False
    print(f"Câmera com IP {ip} está transmitindo imagens.")
    cap.release()
    return True

def verificar_cameras():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "SELECT ip FROM dispositivos ORDER BY id"
        cursor.execute(query)
        ips = cursor.fetchall()
        print("Verificando todas as câmeras cadastradas no banco de dados:")
        threads = []
        for (ip,) in ips:
            thread = threading.Thread(target=verificar_camera, args=(ip,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    except sqlite3.Error as err:
        print(f"Erro: {err}")
    finally:
        cursor.close()
        conn.close()
