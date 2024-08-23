# -*- coding: utf-8 -*-
import socket
import json
import threading

host = '127.0.0.1'
porta = 5000

clients = []
messages = []
lock = threading.Lock()

def _get_available_port():
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temp_socket.bind((host, 0))
    _, port = temp_socket.getsockname()
    temp_socket.close()
    return port

def add_client(data, *args):
    client_port = _get_available_port()
    with lock:
        host, port = args[0]
        client = {
            "name": data["client_name"],
            "host": host,
            "port": client_port
        }
        clients.append(client)
        conexao.send(json.dumps(client).encode('utf-8'))

def get_client(data, *args):
    with lock:
        client = [client for client in clients if client == data["client_name"]]
        conexao.send(json.dumps(client).encode('utf-8'))

def save(data, *args):
    with lock:
        clients.append(data)
        print('Cliente salvo: {}'.format(data))
        getClient(data)

def _list(*args):
    with lock:
        conexao.send(json.dumps(clients).encode('utf-8'))

def get_client(data, *args):
    with lock:
        filtered_client = [client for client in clients if client["name"] == data["client_name"]]
        if not filtered_client:
            conexao.send(json.dumps([]))
            return
        
        conexao.send(json.dumps(filtered_client[0]).encode('utf-8'))

actions = {
    "save": save,
    "list": _list,
    "get_client": get_client,
    "register": add_client
}

def handle_client(conexao, cliente):
    print('Conectado por', cliente[1])
    while True:
        message = conexao.recv(1024)
        if not message: break
        data = json.loads(message)
        actions[data["action"]](data, cliente)
    conexao.close()
    print('Coneccao fechada')

soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
origem = (host, porta)
soquete.bind(origem)
soquete.listen(5)

print("Servidor iniciado e aguardando conexões...")

while True:
    conexao, cliente = soquete.accept()
    client_thread = threading.Thread(
        target=handle_client,
        args=(conexao, cliente)
    )
    client_thread.start()
