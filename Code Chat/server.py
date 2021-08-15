import socket
import threading
from tkinter import *

frame = Tk()
frame.title("Server Listener")
frame.geometry("+600+200")
frame.resizable(False, False)

PORT = 80
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"
clients, names = [], []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)


def startChat():
    print("[Working] Server is working no {}".format(SERVER))
    server.listen()
    print("[Listening] Server is listening...")

    while True:
        conn, addr = server.accept()
        conn.send("NAME".encode(FORMAT))

        name = conn.recv(1024).decode(FORMAT)

        names.append(name)
        clients.append(conn)

        print("Name is : {}".format(name))

        broadcastMessage(f"{name} has joined the chat!".encode(FORMAT))

        conn.send("Connection successful!".encode(FORMAT))

        thread = threading.Thread(target=handle, args=(conn, addr))
        thread.start()

        print("Active connections {}".format(threading.activeCount()-1))


def handle(conn, addr):
    print(f"New connection {addr}")
    connected = True
    while connected:
        message = conn.recv(1024)
        broadcastMessage(message)
    conn.close()


def broadcastMessage(message):
    for client in clients:
        client.send(message)



startChat()
