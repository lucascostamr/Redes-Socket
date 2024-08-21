# -*- coding: utf-8 -*-
import socket
import json
import threading

continuar = True

clients_registered = []

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

def _list(name):
    data = {
        "action": "list",
        "name": name
    }

    soqueteServer.send(json.dumps(data).encode('utf-8'))
    response = soqueteServer.recv(1024)
    messages = json.loads(response)

    print("\nMensagens recebidas:")
    for msg in messages:
        print("De {}: {}".format(msg["name"], msg["message"]))

def connectSoqueteDestinatario(connection):
    if len(connection) == 0:
        return None
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soquete.connect(connection)
    return soquete

def send(name):
    destinatario = raw_input("Digite o destinatario: \n")
    message = raw_input("Digite a mensagem: \n")

    request = {
        "action": "send",
        "name": name,
        "destinatario": destinatario,
        "message": message
    }

    destinatarioAddress = [(host, port) for client in clients_registered if client["name"] == destinatario]

    if not destinatarioAddress:
        request = {
            "action": "get_client",
            "client_name": destinatario
        }
        serverAddress = ('127.0.0.1', 5000)
        soqueteServer = _connect_to_soquete(serverAddress)
        destinatarioAddress = _send_to_soquete(request, soqueteServer)

        if not destinatarioAddress:
            print("Destinatario nao encontrado")
            return
        soqueteDestinatario = _connect_to_soquete(destinatarioAddress)
        _send_to_soquete(request, soqueteDestinatario)
        return

    soqueteDestinatario = _connect_to_soquete(destinatarioAddress)
    _send_to_soquete(request, soqueteDestinatario)

def _exit(*args):
    global continuar
    continuar = False

def handle_client(soquete):
    conexao, cliente = soquete.accept()
    print('Conectado por: ' + client[1])
    while True:
        message = conexao.recv(1024)
        if not message: break
        data = json.loads(message)
        actions[data["action"]](data, cliente)
    conexao.close()
    print('Coneccao fechada')

actions = {
    "1": _list,
    "2": send,
    "3": _exit
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
soqueteClient.bind(('127.0.0.1', 0))
soqueteClient.listen(5)

print("Cliente  iniciado e aguardando conexões...")

client_thread = threading.Thread(
    target=handle_client,
    args=(soqueteClient,)
)
client_thread.start()

while continuar:
    option = raw_input("Listar (1) | Enviar (2) | Sair (3): \n")
    response = actions[option](client_name)

