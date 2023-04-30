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
            