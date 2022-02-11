from email.headerregistry import Address
import socket
import threading
import json
import sys
from db.beridb import VerimDb
db = VerimDb()
clients = []


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(100)
        while True:

            client, address = self.sock.accept()
            client.settimeout(60)
            clients.append([client, client.getpeername()])

            coninfo = client.getpeername()
            
            for x in clients:
                print(x[1][0] + "----" + coninfo[0])
                if x[1][0] == coninfo[0]:
                    print(str(x[1][1]) + "----" + str(coninfo[1]))
                    if str(x[1][1]) != str(coninfo[1]):
                        clients.remove(x)
                        print("silindi")
                        clients.append([client, client.getpeername()])  
            
            threading.Thread(target=self.listenToClient,
                             args=(client, address)).start()
            

    def listenToClient(self, client, address):
        print(f"[YENİ BAGLANTI] {address} baglandı ")
        size = 1024

        while True:
            data = client.recv(size)
            print(data)
            if data:
                gelenveri = json.loads(data)
                print("[MAKİNE GELEN JSON]", gelenveri, address)
                response = data
                if 'command' in gelenveri:
                    command = gelenveri["command"]
                    if command == 'NACK':
                        print("[COMAND=NACK]", response)
                        client.send(response)
                    elif command == 'CARD_REQUEST':
                        cardId = gelenveri["cardId"]
                        db.db_conn()
                        dataquery = db.exec_query(
                            "select gecissistemi.fonksiyon('"+str(cardId)+"', '"+str(address[0])+"')", "Y")
                        db.db_commit()
                        db.db_close()
                        data = dataquery[0]["kartkontrol"]
                        data = json.dumps(data, indent=3).encode('utf-8')
                        makineyegonder = data

                        client.send(makineyegonder)
                        print("[MAKİNEYE GÖNDERİLDİ]:",
                              makineyegonder, address)
                    elif command == 'CHECK':
                        print("[MAKİNEDURUM]", command, address)
                        client.send(response)
                    elif command == 'QRCODE':
                        print("[MAKİNEDURUM]", command, address)
                        cardId = gelenveri["cardId"]
                        ip = gelenveri["ip"]
                        db.db_conn()
                        dataquery = db.exec_query(
                            "select gecissistemi.fonksiyon('"+str(cardId)+"', '"+str(ip)+"')", "Y")
                        db.db_commit()
                        db.db_close()
                        data = dataquery[0]["kartkontrol"]
                        data = json.dumps(data, indent=3).encode('utf-8')
                        for x in clients:
                            if x[1][0] == gelenveri["ip"]:
                                x[0].sendall(data)
                        client.sendall(data)
                        client.close()
                        sys.exit()


if __name__ == "__main__":
    while True:
        port_num = 10001
        try:
            port_num = int(port_num)
            break
        except ValueError:
            pass

    ThreadedServer('192.168.1.1', port_num).listen()
