# Los-Fumadores

Mi dirección de GitHub para este repositorio es la siguiente: [GitHub](https://github.com/andmansim/Los-Fumadores.git)
https://github.com/andmansim/Los-Fumadores.git

# Main
```
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
        
```
# Utils
```
import datetime

def _print(mensaje):
    print('[{}] {}'.format(datetime.datetime.today(), mensaje))

```
# Almacenar
```
global store
codes = ('1', '2', '3', '4', '5') #Lo que tiene cada persona y lo que necesita
store = {'1':{'name': 'Papel', 'required': 'Tabaco, Fósforos, Filtros, Cerillas', 'flag': False, 'request': None},
         '2':{'name': 'Tabaco', 'required': 'Papel, Fósforos, Filtros, Cerillas', 'flag': False, 'request': None},
         '3':{'name': 'Fósforo', 'required': 'Papel, Tabaco, Filtros, Cerillas', 'flag': False, 'request': None},
         '4':{'name': 'Filtros', 'required': 'Papel, Tabaco, Fósforos, Cerillas', 'flag': False, 'request': None},
         '5':{'name': 'Cerillas', 'required': 'Papel, Tabaco, Filtros, Fósforos', 'flag': False, 'request': None}}

tiempo_fumar = 5
tiempo_dormir = 1
tamanio = 1024
```
# Fumador
```
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
```
# Proveedor

```
import threading
import time
from random import choice
import socketserver
from almacenar import codes, tamanio, store, tiempo_dormir, tiempo_fumar
from utils import _print

global smoke
smoke = False
global smoke_code

class MyTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class MyTCPServerHandler(socketserver.BaseRequestHandler):
    '''
    Clase para modificar el servidor
    '''
    bufer = ''
    
    def proceso(self):
        while True:
            mensaje = self.request.recv(tamanio).decode('UTF-8')#recibo mensaje
            if mensaje == 'need': #indicamos el recurso que necesita
                _print('{}: Necesito {}'.format(store.get(self.code)['name'], store.get(self.code)['required']))
                if self.smoke_released:
                    self.smoke_released = False #no está fumando
                    global smoke
                    smoke = False
                    
            elif mensaje == 'enable': #el fumador fuma
                _print('{}: Terminó de fumar'.format(store.get(self.code)['name']))
                self.smoke_released = True # está fumando
                
            elif mensaje == 'ack':
                time.sleep(tiempo_fumar)
                
            elif mensaje == 'exit':
                break
            
            time.sleep(tiempo_dormir)
        
    def handle(self):
        #proceso de reconocimiento, es para manejar el servidor
        self.code = self.request.recv(tamanio).decode('UTF-8')
        self.rejected = False
        self.smoke_released = False
        _print('Conectando fumador . . . ')#Intentamos conectarnos al fumador
        
        if store.get(self.code)['flag'] is False: #nos hemos conectado
            
            store.get(self.code)['request'] = self.request
            store.get(self.code)['flag'] = True
            _print('Fumador aceptado {}'.format(store.get(self.code)['name']))
            self.request.send('accepte'.encode('UTF-8'))
            self.proceso()
            
        else: # no se ha podido conectar
            self.rejected = True
            _print('Fumador rechazado {}'.format(store.get(self.code)['name']))
            self.request.send('rejected'.encode('UTF-8'))
    
    def terminar (self):
        '''
        Es para cuando terminan todosde fumar
        '''
        _print('Fumador desconectado {}'.format(store.get(self.code)['name']))
        
        if self.rejected is False:
            store.get(self.code)['flag'] = False
        global smoke_code
        if smoke_code == self.code:
            global smoke 
            smoke = False
    
    def handle_timeout(self):
        print('Tiempo de espera agotado')
        
def verificar():
    #se verifica si están todos los fumadores conectados 
    while True:
        activo = True
        for i in codes:
            if store[i].get('flag') is False:
                activo = False #los fumadores no están activos
                break
        time.sleep(tiempo_dormir)
        if activo and smoke is False: #salimos cuando no están fumando porque han terminado
            break
        else:
            if activo is False: #no se han conectado pero aún no han fumado
                _print('Proveedor esperando a todos los fumadores')

def init (port):
    try: 
        server = MyTCPServer(('0.0.0.0', port), MyTCPServerHandler)#creamos el servidor
        server.timeout = 10
        server_thread = threading.Thread(target=server.serve_forever)#creamos un hilo
        server_thread.timeout = 10
        _print('Esperando fumadores . . . ')
        server_thread.daemon = True # para que escuche las peticiones en segundo plano
        server_thread.start()
        
        while True:
            verificar() # miramos si los fumadores están conectados
            global smoke_code 
            smoke_code = choice(codes)
            _print('Poveedor: Está disponible {}'.format(store.get(smoke_code)['required']))#hay un fumador disponible, le damos lo que pide
            global smoke
            smoke = True
            store.get(smoke_code)['request'].send('enable'.encode('UTF-8'))#mensaje: ha consumido el recurso
            _print('Poveedor: fumador {} servido'.format(store.get(smoke_code)['name']))
    except KeyboardInterrupt:
        _print('Cerrando conexiones . . .')
        server.shutdown()
        server.server_close()
```