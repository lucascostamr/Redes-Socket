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
    soquete_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soquete_address = (address[0], address[1])
    soquete_server.connect(soquete_address)
    return soquete_server

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
    soquete_server = _connect_to_soquete(serverAddress)
    destinatario_data = _send_to_soquete(requestDestinatario, soquete_server)
    if not destinatario_data:
        print("Destinatario nao encontrado")
        return
    return destinatario_data

def _get_client_list(serverAddress):
    request = {
        "action": "get_client_list"
    }
    soquete_server = _connect_to_soquete(serverAddress)
    destinatarios = _send_to_soquete(request, soquete_server)
    if not destinatarios:
        print("Nenhum destinatario encontrado")
        return
    return destinatarios

def send(client, *args):
    destinatario = raw_input("Digite o destinatario: \n")
    message = raw_input("Digite a mensagem: \n")

    request = {
        "action": "save_message",
        "name": client["name"],
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

    soquete_destinatario = _connect_to_soquete((destinatario_data[0]["host"], destinatario_data[0]["port"]))
    _send_to_soquete(request, soqueteDestinatario)

def send_all(client, *args):
    message = raw_input("Digite a mensagem: \n")

    server_address = ('127.0.0.1', 5000)
    destinatarios = _get_client_list(server_address)
    clients = destinatarios

    for destinatario_data in destinatarios:

        request = {
            "action": "save_message",
            "name": client["name"],
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

def _exit(client, *args):
    with lock:
        global continuar
        continuar = False
        request = {
            "action": "exit",
        }
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
    print("\nCliente  iniciado e aguardando conexões...")
    while continuar:
        conexao, cliente = soquete.accept()
        if not continuar:
            conexao.send(json.dumps({"connection": "closed"}).encode('utf-8'))
            break
        print('\n\nVoce recebeu uma nova mensagem!')
        message = conexao.recv(1024)
        if not message: break
        data = json.loads(message)
        actions[data["action"]](data, conexao)
    conexao.close()
    print('\nConeccao fechada')

def _register_client():
    client_name = raw_input("Digite seu nome: \n")
    request = {
        "action": "register",
        "client_name": client_name
    }
    server_address = ('127.0.0.1', 5000)
    soquete_server = _connect_to_soquete(server_address)
    client = _send_to_soquete(request, soquete_server)
    return client

def _init_client():
    client = _register_client()
    soquete_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soquete_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soquete_client.bind(('127.0.0.1', client["port"]))
    soquete_client.listen(5)
    return [soquete_client, client]

actions = {
    "1": _list_messages,
    "2": send,
    "3": send_all,
    "4": _exit,
    "save_message": _save_message
}

def main():
    soquete_client, client = _init_client()

    client_thread = threading.Thread(
        target=handle_client,
        args=(soquete_client,)
    )
    client_thread.start()

    while continuar:
        option = raw_input("\n\nListar (1) | Enviar (2) | Eviar para todos (3) | Sair (4): \n")
        actions[option](client)


if __name__ == "__main__":
    main()