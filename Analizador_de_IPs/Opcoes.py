import sqlite3
import re
import subprocess
import schedule
import time
def opcoes():
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
            for ip in ips:
                id, nome, idip = ip
                print(f'ID: {id}, Nome: {nome}, IP: {idip}')
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
            select_query = "SELECT id FROM dispositivos ORDER BY id"
            cursor.execute(select_query)
            registros = cursor.fetchall()
            new_id = 1
            for (old_id,) in registros:
                update_query = "UPDATE dispositivos SET id = ? WHERE id = ?"
                cursor.execute(update_query, (new_id, old_id))
                new_id += 1
            conn.commit()
        except sqlite3.Error as err:
            print(f"Erro ao reorganizar os índices: {err}")

    def teste_de_IPs(ip_informado):
        padrao_ip = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if re.match(padrao_ip, ip_informado):
            octetos = ip_informado.split('.')
            if all(0 <= int(octeto) <= 255 for octeto in octetos):
                if ip_informado.startswith('127.'):
                    return f'IP {ip_informado}: 127.0.0.0 a 127.255.255.255 é reservado e não pode ser usado aqui.'
                else:
                    return f'IP {ip_informado}: Parabéns por informar o IP correto'
            else:
                return f'IP {ip_informado}: IP informado não bate com o exigido pelo sistema'
        else:
            return f'IP {ip_informado}: IP informado não bate com o formato correto'

    def ping_ip(ip):
        try:
            output = subprocess.check_output(["ping", "-c", "1", ip], universal_newlines=True)
            if "1 packets transmitted, 1 received" in output:
                print(f"IP {ip} está respondendo.")
            else:
                print(f"IP {ip} não está respondendo.")
        except subprocess.CalledProcessError:
            print(f"Falha ao pingar o IP {ip}.")

    def pingar_ips_sequencialmente():
        try:
            conn = sqlite3.connect('Teste_de_IPs.db')
            cursor = conn.cursor()
            query = "SELECT ip FROM dispositivos ORDER BY id"
            cursor.execute(query)
            ips = cursor.fetchall()
            print("Pingando todos os IPs cadastrados no banco de dados:")
            for (ip,) in ips:
                ping_ip(ip)
                time.sleep(10)  # Esperar 10 segundos antes de pingar o próximo IP
        except sqlite3.Error as err:
            print(f"Erro: {err}")
        finally:
            cursor.close()
            conn.close()

    def indice_de_escolha(escolha):
        match escolha:
            case '1':
                nome_informado = input('Informe o nome do aparelho: ')
                ip_informado = input('Informe o IP: ')
                resultado = teste_de_IPs(ip_informado)
                print(resultado)
                if "Parabéns por informar o IP correto" in resultado:
                    inserir_no_sqlite(nome_informado, ip_informado)
                else:
                    print(f"O IP {ip_informado} não é válido e não foi inserido no banco de dados.")
            case '2':
                imprimir_ips()
            case '3':
                id_to_delete = int(input('Informe o ID do IP a ser deletado: '))
                deletar_ip(id_to_delete)
            case '4':
                pingar_ips_sequencialmente()
            case 'x':
                print("Fechando o menu de opções.")
                return False

    criar_tabela()
    schedule.every(5).minutes.do(pingar_ips_sequencialmente)

    while True:
        escolha = input('''
    Escolha uma opção:
    1- Adicionar IP novo
    2- Mostrar IPs adicionados
    3- Deletar IP por ID
    4- Ping todos os IPs cadastrados
    x- Fechar o menu de opções
    ''')

        if not indice_de_escolha(escolha):


            schedule.run_pending()
            time.sleep(1)
