# -*- coding: utf-8 -*-
import socket
import json
import threading

host = '127.0.0.1'
porta = 5000

clients = []
lock = threading.Lock()

def send(data):
    with lock:
        clients.append(data)
        print('Cliente salvo: {}'.format(data))
        getClient(data)

def _list(*args):
    with lock:
        conexao.send(json.dumps(clients).encode('utf-8'))

def getClient(data):
    filtered_client = [client for client in messages if client["name"] == data["destinatario"]]
    with lock:
        conexao.send(json.dumps(filtered_client).encode('utf-8'))

actions = {
    "send": send,
    "list": _list
}

def handle_client(conexao, cliente):
    print('Conectado por', cliente[1])
    port = cliente[1]
    while True:
        message = conexao.recv(1024)
        if not message: break
        data = json.loads(message)
        data["port"] = port
        actions[data["action"]](data)
    conexao.close()


soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
origem = (host, porta)
soquete.bind(origem)
soquete.listen(5)

print("Servidor iniciado e aguardando conexões...")

while True:
    conexao, cliente = soquete.accept()
    client_thread = threading.Thread(
        target=handle_client, args=(conexao, cliente))
    client_thread.start()
