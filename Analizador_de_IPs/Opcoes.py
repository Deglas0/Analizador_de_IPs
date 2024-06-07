import sqlite3
import re
import subprocess
import schedule
import time
import threading
import cv2
from tabulate import tabulate
import os

# Funções para operações no banco de dados
def criar_tabela():
    conn = sqlite3.connect('Teste_de_IPs.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dispositivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        ip TEXT NOT NULL
    )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def inserir_no_sqlite(nome_informado, ip_registrado):
    try:
        conn = sqlite3.connect('Teste_de_IPs.db')
        cursor = conn.cursor()
        query = "INSERT INTO dispositivos (nome, ip) VALUES (?, ?)"
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
        conn = sqlite3.connect('Teste_de_IPs.db')
        cursor = conn.cursor()
        query = "SELECT id, nome, ip FROM dispositivos"
        cursor.execute(query)
        ips = cursor.fetchall()
        print("IPs cadastrados no banco de dados:")
        print(tabulate(ips, headers=["ID", "Nome", "IP"], tablefmt="grid"))
    except sqlite3.Error as err:
        print(f"Erro: {err}")
    finally:
        cursor.close()
        conn.close()

def deletar_ip(id_to_delete):
    try:
        conn = sqlite3.connect('Teste_de_IPs.db')
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
        # Criar uma tabela temporária para os dados reorganizados
        cursor.execute('''
        CREATE TABLE temp_dispositivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            ip TEXT NOT NULL
        )
        ''')

        # Copiar os dados da tabela original para a tabela temporária
        cursor.execute('''
        INSERT INTO temp_dispositivos (nome, ip)
        SELECT nome, ip FROM dispositivos ORDER BY id
        ''')

        # Excluir a tabela original
        cursor.execute('DROP TABLE dispositivos')

        # Renomear a tabela temporária para o nome original
        cursor.execute('ALTER TABLE temp_dispositivos RENAME TO dispositivos')

        conn.commit()
    except sqlite3.Error as err:
        print(f"Erro ao reorganizar os índices: {err}")
        conn.rollback()

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
                return f'IP {ip_informado}: Parabéns por informar o IP correto'
        else:
            return f'IP {ip_informado}: IP informado não bate com o exigido pelo sistema'
    else:
        return f'IP {ip_informado}: IP informado não bate com o formato correto'

def ping_ip(ip):
    try:
        # Verifica o sistema operacional e ajusta o comando de ping
        ping_command = ["ping", "-n", "1", ip] if os.name == 'nt' else ["ping", "-c", "1", ip]
        output = subprocess.check_output(ping_command, universal_newlines=True)
        if "TTL=" in output:
            print(f"IP {ip} está respondendo.")
            return True
        else:
            print(f"IP {ip} não está respondendo.")
            return False
    except subprocess.CalledProcessError:
        print(f"Falha ao pingar o IP {ip}.")
        return False

def pingar_ips():
    try:
        conn = sqlite3.connect('Teste_de_IPs.db')
        cursor = conn.cursor()
        query = "SELECT ip FROM dispositivos ORDER BY id"
        cursor.execute(query)
        ips = cursor.fetchall()
        print("Pingando todos os IPs cadastrados no banco de dados:")
        threads = []
        for (ip,) in ips:
            thread = threading.Thread(target=ping_ip, args=(ip,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    except sqlite3.Error as err:
        print(f"Erro: {err}")
    finally:
        cursor.close()
        conn.close()

def verificar_camera(ip):
    cap = cv2.VideoCapture(f"http://{ip}/video")  # Ajuste a URL conforme necessário para o modelo da sua câmera
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
        conn = sqlite3.connect('Teste_de_IPs.db')
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

# Função para escolher opções
def indice_de_escolha(escolha):
    match escolha:
        case '1':
            nome_informado = input('Informe o nome do aparelho: ')
            ip_informado = input('Informe o IP: ')
            resultado = teste_de_IPs(ip_informado)
            print(resultado)
            if "Parabéns por informar o IP correto" in resultado:
                if ping_ip(ip_informado):
                    inserir_no_sqlite(nome_informado, ip_informado)
                else:
                    print(f"O IP {ip_informado} não está respondendo e não foi inserido no banco de dados.")
            else:
                print(f"O IP {ip_informado} não é válido e não foi inserido no banco de dados.")
        case '2':
            imprimir_ips()
        case '3':
            try:
                id_to_delete = int(input('Informe o ID do IP a ser deletado: '))
                deletar_ip(id_to_delete)
            except ValueError:
                print("ID inválido. Por favor, insira um número.")
        case '4':
            pingar_ips()
        case '5':
            verificar_cameras()
        case 'x':
            print("Fechando o menu de opções.")
            return False

# Configuração inicial
criar_tabela()
schedule.every(5).minutes.do(pingar_ips)
schedule.every(10).minutes.do(verificar_cameras)

# Loop principal
while True:
    escolha = input('''
Escolha uma opção:
1- Adicionar IP novo
2- Mostrar IPs adicionados
3- Deletar IP por ID
4- Ping todos os IPs cadastrados
5- Verificar câmeras
x- Fechar o menu de opções
''')

    if indice_de_escolha(escolha) == False:
        break

    schedule.run_pending()
    time.sleep(1)