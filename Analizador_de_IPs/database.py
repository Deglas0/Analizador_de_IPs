import sqlite3
from tabulate import tabulate
from tkinter import messagebox

DB_DISPOSITIVOS = 'Dispositivos.db'
DB_TELEFONES = 'Telefones.db'

def criar_tabela_dispositivos():
    with sqlite3.connect(DB_DISPOSITIVOS) as conn:
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


def criar_tabela_telefone():
    with sqlite3.connect(DB_TELEFONES) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS telefones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            senha TEXT NOT NULL
        )
        ''')


def inserir_no_sqlite(nome_informado, ip_registrado, is_camera):
    try:
        with sqlite3.connect(DB_DISPOSITIVOS) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT camera FROM dispositivos WHERE ip = ?", (ip_registrado,))
            resultado = cursor.fetchone()

            if resultado:
                camera_status = resultado[0]
                if camera_status in ['Ativa', 'Desativa', 'Desconhecido']:
                    is_camera = True

            camera_status = 'Desconhecido' if is_camera else 'Não'
            query = "INSERT INTO dispositivos (nome, ip, status, camera) VALUES (?, ?, 'desconhecido', ?)"
            values = (nome_informado, ip_registrado, camera_status)
            cursor.execute(query, values)
            print(f"Dados inseridos: Nome = {nome_informado}, IP = {ip_registrado}, Camera = {camera_status}")
    except sqlite3.Error as err:
        print(f"Erro: {err}")


def inserir_telefone(numero, senha):
    try:
        with sqlite3.connect(DB_TELEFONES) as conn:
            cursor = conn.cursor()
            query = "INSERT INTO telefones (numero, senha) VALUES (?, ?)"
            cursor.execute(query, (numero, senha))
            print(f"Telefone inserido: Número = {numero}")
    except sqlite3.Error as err:
        print(f"Erro: {err}")


def obter_ips():
    try:
        with sqlite3.connect(DB_DISPOSITIVOS) as conn:
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


def obter_telefones():
    try:
        with sqlite3.connect(DB_TELEFONES) as conn:
            cursor = conn.cursor()
            query = "SELECT id, numero FROM telefones"
            cursor.execute(query)
            telefones = cursor.fetchall()
            print("Telefones cadastrados no banco de dados:")
            print(tabulate(telefones, headers=["ID", "Número"], tablefmt="grid"))
            return telefones
    except sqlite3.Error as err:
        print(f"Erro: {err}")
        return []


def obter_telefone_por_id(id, senha):
    try:
        with sqlite3.connect(DB_TELEFONES) as conn:
            cursor = conn.cursor()
            query = "SELECT numero FROM telefones WHERE id = ? AND senha = ?"
            cursor.execute(query, (id, senha))
            telefone = cursor.fetchone()
            return telefone[0] if telefone else None
    except sqlite3.Error as err:
        print(f"Erro: {err}")
        return None


def deletar_ip(id_to_delete):
    try:
        with sqlite3.connect(DB_DISPOSITIVOS) as conn:
            cursor = conn.cursor()
            delete_query = "DELETE FROM dispositivos WHERE id = ?"
            cursor.execute(delete_query, (id_to_delete,))
            reorganizar_indices(cursor, conn)
            print(f"Registro com ID {id_to_delete} deletado e índices reorganizados.")
    except sqlite3.Error as err:
        print(f"Erro: {err}")


def deletar_telefone(id_to_delete, senha):
    try:
        with sqlite3.connect(DB_TELEFONES) as conn:
            cursor = conn.cursor()
            query = "SELECT senha FROM telefones WHERE id = ?"
            cursor.execute(query, (id_to_delete,))
            result = cursor.fetchone()
            if result and result[0] == senha:
                delete_query = "DELETE FROM telefones WHERE id = ?"
                cursor.execute(delete_query, (id_to_delete,))
                reorganizar_indices_telefones(cursor, conn)
                print(f"Telefone com ID {id_to_delete} deletado.")
            else:
                messagebox.showerror("Erro", "Senha incorreta.")
    except sqlite3.Error as err:
        print(f"Erro: {err}")


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
    except sqlite3.Error as err:
        print(f"Erro ao reorganizar os índices: {err}")
        conn.rollback()


def reorganizar_indices_telefones(cursor, conn):
    try:
        cursor.execute('''
        CREATE TABLE temp_telefones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            senha TEXT NOT NULL
        )
        ''')
        cursor.execute('''
        INSERT INTO temp_telefones (id, numero, senha)
        SELECT NULL, numero, senha FROM telefones ORDER BY id
        ''')
        cursor.execute('DROP TABLE telefones')
        cursor.execute('ALTER TABLE temp_telefones RENAME TO telefones')
    except sqlite3.Error as err:
        print(f"Erro ao reorganizar os índices: {err}")
        conn.rollback()