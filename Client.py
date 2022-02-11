from logging import shutdown
from pydoc import cli
import socket
import sys
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('192.168.1.1', 10001))
client.send(b'{"cardId": "0C08F763", "command": "QRCODE", "ip": "192.168.1.1"}')
from_server = client.recv(1024)


print(from_server)