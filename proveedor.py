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