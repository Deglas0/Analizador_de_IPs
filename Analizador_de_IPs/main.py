import schedule
import time
import threading
from database import criar_tabela, inserir_no_sqlite, imprimir_ips, deletar_ip
from validation import teste_de_IPs
from network import pingar_ips
from camera import verificar_cameras
from sms import verificar_erros_e_enviar_sms


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
            try:
                id_to_delete = int(input('Informe o ID do IP a ser deletado: '))
                deletar_ip(id_to_delete)
            except ValueError:
                print("ID inválido. Por favor, insira um número.")
        case '4':
            pingar_ips()  # Esta função já imprime os IPs após pingar
        case '5':
            verificar_cameras()
        case 'x':
            print("Fechando o menu de opções.")
            return False


def configuracao_inicial():
    criar_tabela()
    schedule.every(5).minutes.do(pingar_ips)
    schedule.every(10).minutes.do(verificar_cameras)
    schedule.every(10).minutes.do(verificar_erros_e_enviar_sms)


def pingar_ips_em_segundo_plano():
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    configuracao_inicial()
    thread_ping = threading.Thread(target=pingar_ips_em_segundo_plano)
    thread_ping.daemon = True
    thread_ping.start()

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


if __name__ == '__main__':
    main()
