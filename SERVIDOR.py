# -*- coding: utf-8 -*-
import socket
import json
import threading

host = '127.0.0.1'
porta = 5000

clients = []

lock = threading.Lock()

def _get_available_port():
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temp_socket.bind((host, 0))
    _, port = temp_socket.getsockname()
    temp_socket.close()
    return port

def _update_client_port(client_name, new_port):
    for client in clients:
        if client.get("name") == client_name:
            client["port"] = new_port
            return client
    return None

def save(data, *args):
    client_port = _get_available_port()
    with lock:
        host, port = args[0]

        is_client = _update_client_port(data["client_name"], client_port)

        if not is_client:
            new_client = {
                "name": data["client_name"],
                "host": host,
                "port": client_port
            }
            clients.append(new_client)
            conexao.send(json.dumps(new_client).encode('utf-8'))

        conexao.send(json.dumps(is_client).encode('utf-8'))

def list_clients(*args):
    with lock:
        conexao.send(json.dumps(clients).encode('utf-8'))

def get_client(data, *args):
    with lock:
        filtered_client = [client for client in clients if client["name"] == data["client_name"]]
        if not filtered_client:
            conexao.send(json.dumps([]))
            return

        conexao.send(json.dumps(filtered_client[0]).encode('utf-8'))

def remove_client(data, *args):
    client = data["client"]
    clients.remove(client)
    conexao.send(json.dumps({"message": "client removed"}).encode('utf-8'))

actions = {
    "list": list_clients,
    "get_client": get_client,
    "register": save,
    "remove": remove_client
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
