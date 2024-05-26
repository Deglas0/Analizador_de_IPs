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
        query = "SELECT id , nome, ip FROM dispositivos"
        cursor.execute(query)

        # Recuperação dos resultados
        ips = cursor.fetchall()

        # Imprimir os IPs
        print("IPs cadastrados no banco de dados:")
        for ip in ips:
            id, nome, idip = ip
            print(f'ID:{id},  nome: {nome},  IP: {idip}')

    except mysql.connector.Error as err:
        print(f"Erro: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def deletar_ip(id_to_delete):
    try:
        # Conexão ao banco de dados
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='admin123@',
            database='Teste_de_IPs'
        )
        cursor = conn.cursor()

        # Deletar o registro com o ID fornecido
        delete_query = "DELETE FROM dispositivos WHERE id = %s"
        cursor.execute(delete_query, (id_to_delete,))

        # Confirmar a exclusão
        conn.commit()

        # Reorganizar os índices
        reorganizar_indices(cursor, conn)

        print(f"Registro com ID {id_to_delete} deletado e índices reorganizados.")

    except mysql.connector.Error as err:
        print(f"Erro: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def reorganizar_indices(cursor, conn):
    try:
        # Selecionar todos os registros ordenados pelo ID atual
        select_query = "SELECT id FROM dispositivos ORDER BY id"
        cursor.execute(select_query)
        registros = cursor.fetchall()

        # Atualizar os índices para ficarem em sequência
        new_id = 1
        for (old_id,) in registros:
            update_query = "UPDATE dispositivos SET id = %s WHERE id = %s"
            cursor.execute(update_query, (new_id, old_id))
            new_id += 1

        # Confirmar a reorganização
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Erro ao reorganizar os índices: {err}")


while True:
    escolha = str(input('''
    Escolha uma opção:
    1- adicionar IP novo
    2- Mostrar IPs adicionados
    3= Deletar IP
    x- fechar o menu opções
    '''))
    match escolha:
        case '1':
            nome_informado = input('Informe o nome do aparelho: ')
            ip_registrado = input('Informe o IP: ')
            inserir_no_mysql(nome_informado, ip_registrado)

        case '2':
            imprimir_ips()

        case '3':
            id_to_delete = int(input('Informe o ID do IP a ser deletado: '))
            deletar_ip(id_to_delete)

        case 'x':
            print('Voltando ao menu principal:')
            break

        case _:
            print('Opção não bate com as escolhas informadas, por favor tente novamente.')
            print('')


