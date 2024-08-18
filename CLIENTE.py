# -*- coding: utf-8 -*-
import socket
import json

host = '127.0.0.1'
portaServer = 5000
soqueteServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
destino = (host, portaServer)
soqueteServer.connect(destino)
continuar = True

clients_registered = []

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

    data = {
        "action": "send",
        "name": name,
        "destinatario": destinatario,
        "message": message
    }

    destinatario = [client for client in clients_registered if client == destinatario]

    if destinatario:
        soqueteDestinatario = connectSoqueteDestinatario(destinatario)
        soqueteDestinatario.send(json.dumps(data).encode('utf-8'))
    else:
        request = {
            "action": "get_client",
            "client_name": destinatario
        }

        soqueteServer.send(json.dumps(request).encode('utf-8'))
        response = soqueteServer.recv(1024)
        destinatario = json.loads(response)
        if len(destinatario) == 0:
            print("Cliente nao encontrado")
            return
        soqueteDestinatario = connectSoqueteDestinatario(destinatario)
        soqueteDestinatario.send(json.dumps(data).encode('utf-8'))

def _exit(*args):
    global continuar
    continuar = False

actions = {
    "1": _list,
    "2": send,
    "3": _exit
}

name = raw_input("Digite seu nome: \n")

while continuar:
    option = raw_input("Listar (1) | Enviar (2) | Sair (3): \n")
    response = actions[option](name)
    if not response:
        _exit()

soqueteServer.close()
