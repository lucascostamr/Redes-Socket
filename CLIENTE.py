# -*- coding: utf-8 -*-
import socket
import json
import threading

lock = threading.Lock()

continuar = True

clients = []
messages = []

def _send_to_soquete(request, soquete):
    soquete.send(json.dumps(request).encode('utf-8'))
    response = soquete.recv(1024)
    soquete.close()
    return json.loads(response)

def _connect_to_soquete(address):
    soqueteServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soqueteAddress = (address[0], address[1])
    soqueteServer.connect(soqueteAddress)
    return soqueteServer

def _list_messages(*args):
    author_width = 20
    message_width = 40

    print("\t{:<{author_width}} | {:<{message_width}}".format("Author", "Message", author_width=author_width, message_width=message_width))
    print("\t" + "-" * author_width + "-+-" + "-" * message_width)

    for message in reversed(messages):
        print("\t{:<{author_width}} | {:<{message_width}}".format(message["name"], message["message"], author_width=author_width, message_width=message_width))

def _get_client(destinatario, serverAddress):
    requestDestinatario = {
        "action": "get_client",
        "client_name": destinatario
    }
    soqueteServer = _connect_to_soquete(serverAddress)
    destinatario_data = _send_to_soquete(requestDestinatario, soqueteServer)
    if not destinatario_data:
        print("Destinatario nao encontrado")
        return
    return destinatario_data

def _get_client_list(serverAddress):
    request = {
        "action": "get_client_list"
    }
    soqueteServer = _connect_to_soquete(serverAddress)
    destinatarios = _send_to_soquete(request, soqueteServer)
    if not destinatarios:
        print("Nenhum destinatario encontrado")
        return
    return destinatarios

def send(name, *args):
    destinatario = raw_input("Digite o destinatario: \n")
    message = raw_input("Digite a mensagem: \n")

    request = {
        "action": "save_message",
        "name": name,
        "destinatario": destinatario,
        "message": message
    }

    destinatario_data = [client for client in clients if client["name"] == destinatario]

    if not destinatario_data:
        server_address = ('127.0.0.1', 5000)
        destinatario_data_server = _get_client(destinatario, server_address)
        if not destinatario_data_server:
            return
        soquete_destinatario = _connect_to_soquete((destinatario_data_server["host"], destinatario_data_server["port"]))
        _send_to_soquete(request, soquete_destinatario)
        clients.append(destinatario_data_server)
        return

    destinatario_data_server = _get_client(destinatario, serverAddress)

    if not destinatario_data_server:
        clients.remove(destinatario_data[0])
        return

    if not destinatario_data_server["port"] == destinatario_data[0]["port"]:
        index = clients.index(destinatario_data[0])
        clients[index] = destinatario_data_server
        destinatario_data[0] = destinatario_data_server

    soqueteDestinatario = _connect_to_soquete((destinatario_data[0]["host"], destinatario_data[0]["port"]))
    _send_to_soquete(request, soqueteDestinatario)

def send_all(name, *args):
    message = raw_input("Digite a mensagem: \n")

    server_address = ('127.0.0.1', 5000)
    destinatarios = _get_client_list(server_address)
    clients = destinatarios

    for destinatario_data in destinatarios:

        request = {
            "action": "save_message",
            "name": name,
            "destinatario": destinatario_data["name"],
            "message": message
        }

        soqueteDestinatario = _connect_to_soquete((destinatario_data["host"], destinatario_data["port"]))
        _send_to_soquete(request, soqueteDestinatario)

def _save_message(message, *args):
    messages.append(message)
    conexao = args[0]
    conexao.send(json.dumps({"connection": "closed"}).encode('utf-8'))
    conexao.close()

def _exit(*args):
    with lock:
        global continuar
        continuar = False
        request = {
            "action": "3",
        }
        client = args[1]
        soquete = _connect_to_soquete((client["host"], client["port"]))
        _send_to_soquete(request, soquete)

        server_address = ('127.0.0.1', 5000)
        soquete_server = _connect_to_soquete(server_address)
        request = {
            "action": "remove",
            "client": client
        }
        response = _send_to_soquete(request, soquete_server)


def handle_client(soquete):
    while continuar:
        conexao, cliente = soquete.accept()
        if not continuar:
            conexao.send(json.dumps({"connection": "closed"}).encode('utf-8'))
            break
        print('Nova menssagem de: ', cliente[1])
        message = conexao.recv(1024)
        if not message: break
        data = json.loads(message)
        actions[data["action"]](data, conexao)
    conexao.close()
    print('\nConeccao fechada')

actions = {
    "1": _list_messages,
    "2": send,
    "3": send_all,
    "4": _exit,
    "save_message": _save_message
}

client_name = raw_input("Digite seu nome: \n")

request = {
    "action": "register",
    "client_name": client_name
}

serverAddress = ('127.0.0.1', 5000)
soqueteServer = _connect_to_soquete(serverAddress)
response = _send_to_soquete(request, soqueteServer)

soqueteClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soqueteClient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
soqueteClient.bind(('127.0.0.1', response["port"]))
soqueteClient.listen(5)

print("\nCliente  iniciado e aguardando conexões...")

client_thread = threading.Thread(
    target=handle_client,
    args=(soqueteClient,)
)
client_thread.start()

while continuar:
    option = raw_input("\n\nListar (1) | Enviar (2) | Eviar para todos (3) | Sair (4): \n")
    actions[option](client_name, response)
