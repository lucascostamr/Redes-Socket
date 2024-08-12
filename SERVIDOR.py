# -*- coding: utf-8 -*-
import socket
import json
import threading

host = '127.0.0.1'
porta = 5000

messages = []
lock = threading.Lock()

def save(data):
    with lock:
        messages.append(data)
        print('Mensagem salva: {}'.format(data))

def _list(data):
    with lock:
        filtered_messages = [msg for msg in messages if msg["destinatario"] == data["name"]]
        conexao.send(json.dumps(filtered_messages).encode('utf-8'))
        print('Cliente {} Recebida: {}'.format(cliente[0], messages))

actions = {
    "save": save,
    "list": _list
}

def handle_client(conexao, cliente):
    print('Conectado por', cliente)
    while True:
        message = conexao.recv(1024)
        if not message: break
        data = json.loads(message)
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
