import socket 
from threading import Thread 
from socketserver import ThreadingMixIn
import json
import base64
from keras.models import Sequential, load_model

update_model = {}
running = True

def startCentralizedServer():
    class UpdateModel(Thread): 
 
        def __init__(self,ip,port): 
            Thread.__init__(self) 
            self.ip = ip 
            self.port = port 
            print('Request received from Client IP : '+ip+' with port no : '+str(port)+"\n") 
 
        def run(self): 
            data = conn.recv(1000000)
            data = json.loads(data.decode())
            request_type = str(data.get("request"))
            station = str(data.get("station"))
            model = data.get("model")
            model = model.encode()
            model = base64.b64decode(model)
            print(type(model))
            if request_type == 'update_model':
                print("Updating model of station = "+station)
                update_model[station] = model
                print("Model successfully updated")
                print("Total updated models are : "+str(len(update_model))+"\n")
                with open('received/'+station+'.hdf5', 'wb') as file:
                    file.write(model)
                file.close()          
                conn.send(str('Model updated to server successfully').encode())         
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server.bind(('localhost', 2222))
    print("Centralized Server Started & waiting for incoming connections\n\n")
    while running:
        server.listen(4)
        (conn, (ip,port)) = server.accept()
        newthread = UpdateModel(ip,port) 
        newthread.start() 
    
def startServer():
    Thread(target=startCentralizedServer).start()

startServer()

