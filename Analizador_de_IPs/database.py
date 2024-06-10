import sqlite3
from tabulate import tabulate

DB_NAME = 'Teste_de_IPs.db'

def criar_tabela():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dispositivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        ip TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'desconhecido'
    )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def inserir_no_sqlite(nome_informado, ip_registrado):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "INSERT INTO dispositivos (nome, ip, status) VALUES (?, ?, 'desconhecido')"
        values = (nome_informado, ip_registrado)
        cursor.execute(query, values)
        conn.commit()
        print(f"Dados inseridos: Nome = {nome_informado}, IP = {ip_registrado}")
    except sqlite3.Error as err:
        print(f"Erro: {err}")
    finally:
        cursor.close()
        conn.close()

def imprimir_ips():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "SELECT id, nome, ip, status FROM dispositivos"
        cursor.execute(query)
        ips = cursor.fetchall()
        print("IPs cadastrados no banco de dados:")
        print(tabulate(ips, headers=["ID", "Nome", "IP", "Status"], tablefmt="grid"))
    except sqlite3.Error as err:
        print(f"Erro: {err}")
    finally:
        cursor.close()
        conn.close()

def deletar_ip(id_to_delete):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        delete_query = "DELETE FROM dispositivos WHERE id = ?"
        cursor.execute(delete_query, (id_to_delete,))
        conn.commit()
        reorganizar_indices(cursor, conn)
        print(f"Registro com ID {id_to_delete} deletado e índices reorganizados.")
    except sqlite3.Error as err:
        print(f"Erro: {err}")
    finally:
        cursor.close()
        conn.close()

def reorganizar_indices(cursor, conn):
    try:
        cursor.execute('''
        CREATE TABLE temp_dispositivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            ip TEXT NOT NULL,
            status TEXT NOT NULL
        )
        ''')
        cursor.execute('''
        INSERT INTO temp_dispositivos (nome, ip, status)
        SELECT nome, ip, status FROM dispositivos ORDER BY id
        ''')
        cursor.execute('DROP TABLE dispositivos')
        cursor.execute('ALTER TABLE temp_dispositivos RENAME TO dispositivos')
        conn.commit()
    except sqlite3.Error as err:
        print(f"Erro ao reorganizar os índices: {err}")
        conn.rollback()
