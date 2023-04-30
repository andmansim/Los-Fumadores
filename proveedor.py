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
    bufer = ''
    def proceso(self):
        while True:
            mensaje = self.request.recv(tamanio).decode('UTF-8')
            if mensaje == 'need':
                _print('{}: Necesito {}'.format(store.get(self.code)['name'], store.get(self.code)['required']))
                if self.smoke_released:
                    self.smoke_released = False
                    global smoke
                    smoke = False
                    
            elif mensaje == 'enable':
                _print('{}: Terminó de fumar'.format(store.get(self.code)['name']))
                self.smoke_released = True
            elif mensaje == 'ack':
                time.sleep(tiempo_fumar)
            elif mensaje == 'exit':
                break
            
            time.sleep(tiempo_dormir)
        
    def handle(self):
        #proceso de reconocimiento
        self.code = self.request.recv(tamanio).decode('UTF-8')
        self.rejected = False
        self.smoke_released = False
        _print('Conectando fumador . . . ')
        if store.get(self.code)['flag'] is False:
            store.get(self.code)['request'] = self.request
            store.get(self.code)['flag'] = True
            _print('Fumador aceptado {}'.format(store.get(self.code)['name']))
            self.request.send('accepte'.encode('UTF-8'))
            self.proceso()
        else:
            self.rejected = True
            _print('Fumador rechazado {}'.format(store.get(self.code)['name']))
            self.request.send('rejected'.encode('UTF-8'))
    
    def terminar (self):
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
                activo = False
                break
        time.sleep(tiempo_dormir)
        if activo and smoke is False:
            break
        else:
            if activo is False:
                _print('Proveedor esperando a tosos los fumadores')

def init (port):
    try: 
        server = MyTCPServer(('0.0.0.0', port), MyTCPServerHandler)
        server.timeout = 10
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.timeout = 10
        _print('Esperando fumadores . . . ')
        server_thread.daemon = True
        server_thread.start()
        
        while True:
            verificar()
            global smoke_code 
            smoke_code = choice(codes)
            _print('Poveedor: Está disponible {}'.format(store.get(smoke_code)['required']))
            global smoke
            smoke = True
            store.get(smoke_code)['request'].send('enable'.encode('UTF-8'))
            _print('Poveedor: fumador {} servido'.format(store.get(smoke_code)['name']))
    except KeyboardInterrupt:
        _print('Cerrando conexiones . . .')
        server.shutdown()
        server.server_close()