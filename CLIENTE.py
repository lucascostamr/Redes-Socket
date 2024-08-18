# -*- coding: utf-8 -*-
import socket
import json

host = '127.0.0.1'
portaServer = 5000
soqueteServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soqueteClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
origem = (host, porta)
soquete.bind(origem)
soquete.listen(5)

soqueteServer.connect((host, portaServer))
continuar = True

def _list(name):
    data = {
        "action": "list",
        "name": name
    }

    soquete.send(json.dumps(data).encode('utf-8'))
    response = soquete.recv(1024)
    messages = json.loads(response)

    print("\nMensagens recebidas:")
    for msg in messages:
        print("De {}: {}".format(msg["name"], msg["message"]))

def send(name):
    destinatario = raw_input("Digite o destinatario: \n")
    message = raw_input("Digite a mensagem: \n")

    data = {
        "action": "send",
        "name": name,
        "destinatario": destinatario,
        "message": message
    }

    soqueteServer.send(json.dumps(data).encode('utf-8'))
    response = soqueteServer.recv(1024)
    client_dest = json.loads(response)
    soqueteClient.connect((host, client_dest["port"]))
    soqueteClient.close()

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
    actions[option](name)

soquete.close()
