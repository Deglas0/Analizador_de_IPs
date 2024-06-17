import sqlite3
from tabulate import tabulate

DB_NAME = 'Teste_de_IPs.db'

class DatabaseManager:
    @staticmethod
    def criar_tabela():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dispositivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            ip TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'desconhecido',
            camera TEXT NOT NULL DEFAULT 'Desconhecido'
        )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def inserir_no_sqlite(nome_informado, ip_registrado, is_camera):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            # Verificar se o IP já está no banco de dados
            cursor.execute("SELECT camera FROM dispositivos WHERE ip = ?", (ip_registrado,))
            resultado = cursor.fetchone()

            if resultado:
                camera_status = resultado[0]
                if camera_status in ['Ativa', 'Desativa', 'Desconhecido']:
                    is_camera = True  # Se já for uma câmera, garantir que não será alterado para "Não"

            camera_status = 'Desconhecido' if is_camera else 'Não'
            query = "INSERT INTO dispositivos (nome, ip, status, camera) VALUES (?, ?, 'desconhecido', ?)"
            values = (nome_informado, ip_registrado, camera_status)
            cursor.execute(query, values)
            conn.commit()
            print(f"Dados inseridos: Nome = {nome_informado}, IP = {ip_registrado}, Camera = {camera_status}")
        except sqlite3.Error as err:
            print(f"Erro: {err}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obter_ips():
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            query = "SELECT id, nome, ip, status, camera FROM dispositivos"
            cursor.execute(query)
            ips = cursor.fetchall()
            print("IPs cadastrados no banco de dados:")
            print(tabulate(ips, headers=["ID", "Nome", "IP", "Status", "Camera"], tablefmt="grid"))
            return ips
        except sqlite3.Error as err:
            print(f"Erro: {err}")
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def deletar_ip(id_to_delete):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            delete_query = "DELETE FROM dispositivos WHERE id = ?"
            cursor.execute(delete_query, (id_to_delete,))
            conn.commit()
            DatabaseManager.reorganizar_indices(cursor, conn)
            print(f"Registro com ID {id_to_delete} deletado e índices reorganizados.")
        except sqlite3.Error as err:
            print(f"Erro: {err}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def reorganizar_indices(cursor, conn):
        try:
            cursor.execute('''
            CREATE TABLE temp_dispositivos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                ip TEXT NOT NULL,
                status TEXT NOT NULL,
                camera TEXT NOT NULL
            )
            ''')
            cursor.execute('''
            INSERT INTO temp_dispositivos (id, nome, ip, status, camera)
            SELECT NULL, nome, ip, status, camera FROM dispositivos ORDER BY id
            ''')
            cursor.execute('DROP TABLE dispositivos')
            cursor.execute('ALTER TABLE temp_dispositivos RENAME TO dispositivos')
            conn.commit()
        except sqlite3.Error as err:
            print(f"Erro ao reorganizar os índices: {err}")
            conn.rollback()
