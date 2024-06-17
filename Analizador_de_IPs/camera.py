import sqlite3
import cv2
import threading
from database_manager import DatabaseManager

class Camera:
    @staticmethod
    def verificar_camera(ip, id, is_camera):
        if is_camera == 'Não':
            return  # Não fazer nada se não for uma câmera

        if is_camera in ['Desconhecido', 'Desativa']:
            cap = cv2.VideoCapture(f"http://{ip}:4747/video")
        else:
            cap = cv2.VideoCapture(f"http://{ip}/video")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        if not cap.isOpened():
            print(f"Não foi possível acessar a câmera com IP {ip}.")
            cursor.execute("UPDATE dispositivos SET camera = 'Desativa' WHERE id = ? AND camera != 'Não'", (id,))
            conn.commit()
            cursor.close()
            conn.close()
            return False

        ret, frame = cap.read()
        if not ret or frame is None:
            print(f"Falha ao capturar imagem da câmera com IP {ip}.")
            cursor.execute("UPDATE dispositivos SET camera = 'Desativa' WHERE id = ? AND camera != 'Não'", (id,))
            conn.commit()
            cursor.close()
            conn.close()
            return False

        print(f"Câmera com IP {ip} está transmitindo imagens.")
        cursor.execute("UPDATE dispositivos SET camera = 'Ativa' WHERE id = ?", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        cap.release()
        return True

    @staticmethod
    def verificar_cameras():
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            query = "SELECT id, ip, camera FROM dispositivos ORDER BY id"
            cursor.execute(query)
            dispositivos = cursor.fetchall()

            threads = []
            for id, ip, camera in dispositivos:
                thread = threading.Thread(target=Camera.verificar_camera, args=(ip, id, camera))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            MainApp.atualizar_tabela()
            messagebox.showinfo("Verificar Câmeras", "Verificação das câmeras concluída.")
        except sqlite3.Error as err:
            print(f"Erro: {err}")
        finally:
            cursor.close()
            conn.close()
