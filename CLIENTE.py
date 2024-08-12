# -*- coding: utf-8 -*-
import socket
import json

host = '127.0.0.1'
porta = 5000
soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
destino = (host, porta)
soquete.connect(destino)
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

def save(name):
    destinatario = raw_input("Digite o destinatario: \n")
    message = raw_input("Digite a mensagem: \n")

    data = {
        "action": "save",
        "name": name,
        "destinatario": destinatario,
        "message": message
    }

    soquete.send(json.dumps(data).encode('utf-8'))

def _exit(*args):
    global continuar
    continuar = False

actions = {
    "1": _list,
    "2": save,
    "3": _exit
}

name = raw_input("Digite seu nome: \n")

while continuar:
    option = raw_input("Listar (1) | Enviar (2) | Sair (3): \n")
    actions[option](name)

soquete.close()
