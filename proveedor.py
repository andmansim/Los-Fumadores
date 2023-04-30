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

class MTCPServerHandler(socketserver.BaseRequestHandler):
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