import socket
import time
from almacenar import tamanio, store, tiempo_fumar, tiempo_dormir
from utils import _print

def proceso(c, r):
    '''
    Se encarga de mandar mensajes entre el proveedor y el fumador para conectarlos y ver si están listos para empezar
    '''
    mensaje = '' #El mensaje q se va a ir cambiando
    while True:
        if mensaje != 'ack':#Esperamos a que nos llegue el recurso que necesitamos 
            _print('Esperando {}!'.format(store.get(c)['required']))
            r.send('need'.encode('UTF-8'))#Envíamos el pedido
        
        mensaje = r.recv(tamanio).decode('UTF-8')#Respuesta del servidor
        if mensaje == 'enable':#Hemos recibido el mensaje y preparamos todo para fumar
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
    '''
    Se encarga de comunicarse con el sevidor
    '''
    try:
        conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#creamos la conexión
        conexion.connect((ip, p))#nos conectamos a la ip y el servidor
        conexion.send('{}'.format(c).encode('UTF-8'))#enviamo la petición
        time.sleep(tiempo_dormir)
        
        respuesta = conexion.recv(tamanio).decode('UTF-8')#respuesta
        if respuesta =='accepte':
            proceso(c, conexion)#ejecutamos proceso, es decir, intercambian mensajes
        else: 
            _print('Rechazado')
        
        conexion.close()
    except KeyboardInterrupt:
        _print('Cerrando conexiones. . .')
        conexion.send('exit'.encode('UTF-8'))
        conexion.close()