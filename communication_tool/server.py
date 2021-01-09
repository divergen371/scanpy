import socket
from threading import Thread
from datetime import datetime
from colorama import init, Fore

init()
GREEN = Fore.GREEN
RED = Fore.RED
RESET = Fore.RESET
BLUE = Fore.BLUE

BUF_SIZE = 1024
BIND_IP = "0.0.0.0"
BIND_PORT = 8000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((BIND_IP, BIND_PORT))

server.listen(5)
print(f"[*] Listening on {BIND_IP} {BIND_PORT}")


def client_handler(client_socket):
    request = client_socket.recv(BUF_SIZE)
    print(f"{GREEN}[*] Received:\n{request.decode('utf-8')} {'-'*24}{RESET}")
    now = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
    html = """<!DOCTYPE html><html lang="ja><body><p>Test Server</p></body></html>"""
    header = f"""HTTP/1.0 200 OK\r\nDate: {now}\r\nServer:TestHTTPServer\r\nContent-Type: \
text/html; charset=utf-8\r\n\r\n """

    if request.startswith(b"HEAD"):
        client_socket.send(header.encode("utf-8"))
    elif request.startswith(b"GET"):
        res = header[:-2] + f"Content-Length: {len(html)}\r\n" + "\r\n" + html
        client_socket.send(res.encode("utf-8"))


while True:
    client, addr = server.accept()
    print(f"{GREEN}[*] Accepted connection from: {addr[0]}:{addr[1]}")
    handler = Thread(target=client_handler, args=[client])
    handler.start()
