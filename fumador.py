import socket
import time
from almacenar import tamanio, store, tiempo_fumar, tiempo_dormir
from utils import _print

def proceso(c, r):
    mensaje = ''
    while True:
        if mensaje != 'ack':
            _print('Esperando {}!'.format(store.get(c)['required']))
            r.send('need'.encode('UTF-8'))
        
        mensaje = r.recv(tamanio).decode('UTF-8')
        if mensaje == 'enable':
            _print('Servido!')
            time.sleep(tiempo_dormir)
            r.send('ack'.encode('UTF-8'))   
            _print('Haciendo cigarro')
            time.sleep(tiempo_dormir)
            _print('Fumando')
            time.sleep(tiempo_fumar)
            r.send('enable'.encode('UTF-8'))   
        elif mensaje =='ack':
            pass
        
        time.sleep(tiempo_dormir)

def init(ip, p, c):
    try:
        r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        r.connect((ip, p))
        r.send('{}'.format(c).encode('UTF-8'))
        time.sleep(tiempo_dormir)
        
        e = r.recv(tamanio).decode('UTF-8')
        if e =='accepte':
            proceso(c, r)
        else: 
            _print('Rechazado')
        
        r.close()
    except:
        