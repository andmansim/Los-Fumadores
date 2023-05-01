import os

from almacenar import codes, store

def get_port():#Puerto del servidor
    while True:
        try:
            port = int(input('Puerto (1024 - 49151): '))
            if port >= 1024 and port <= 49151:
                break
        except Exception:
            pass
    return port

if __name__ == '__main__':
    '''
    Conecta todo y lo pone bonito
    '''
    os.system('cls')
    while True:
        print('1. Proveedor')
        print('2. Fumador')
        type = input ('Opción: ')
        if type in ['1', '2']:
            break
        else: os.system ('cls')
        
    os.system('cls')
    
    if type == '1':
        print('Proveedor')
        from proveedor import init
        init(get_port())
    else: 
        while True:
            print('Fumador')
            for i in codes:
                print('{}. {}'.format(i, store[i].get('name')))
                type = input('Opción: ')
            if type in codes:
                break
            else: 
                os.system('cls')
                    
        ip = input('Ip del proveedor: ')
        from fumador import init
        init(ip, get_port(), type)
        