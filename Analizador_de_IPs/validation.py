import re

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
