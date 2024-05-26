import Opcoes
escolha = str(1)
while escolha == '1':
    escolha = str(input('''
           digite 1:
           '''))
    match escolha:
        case '1':
            Opcoes.opcoes()