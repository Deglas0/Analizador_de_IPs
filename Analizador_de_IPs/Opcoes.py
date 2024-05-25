import mysql.connector

def inserir_no_mysql(nome_informado, ip_registrado):
    try:
        # Conexão ao banco de dados
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='admin123@',
            database='Teste_de_IPs'
        )
        cursor = conn.cursor()

        # Inserção dos dados
        query = "INSERT INTO dispositivos (nome, ip) VALUES (%s, %s)"
        values = (nome_informado, ip_registrado)
        cursor.execute(query, values)

        # Confirmação da inserção
        conn.commit()

        print(f"Dados inseridos: Nome = {nome_informado}, IP = {ip_registrado}")

    except mysql.connector.Error as err:
        print(f"Erro: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
def imprimir_ips():
    try:
        # Conexão ao banco de dados
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='admin123@',
            database='Teste_de_IPs'
        )
        cursor = conn.cursor()

        # Seleção dos IPs
        query = "SELECT ip FROM dispositivos"
        cursor.execute(query)

        # Recuperação dos resultados
        ips = cursor.fetchall()

        # Imprimir os IPs
        print("IPs cadastrados no banco de dados:")
        for ip in ips:
            print(ip[0])

    except mysql.connector.Error as err:
        print(f"Erro: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

while True:
    escolha = str(input('''
    Escolha uma opção:
    1- adicionar IP novo
    2- Mostrar IPs adicionados
    x- fechar o menu opções
    '''))
    match escolha:
        case '1':
            nome_informado = input('Informe o nome do aparelho: ')
            ip_registrado = input('Informe o IP: ')
            inserir_no_mysql(nome_informado, ip_registrado)

        case '2':
            imprimir_ips()

        case _:
            print('Opção não bate com as escolhas informadas, por favor tente novamente.')
