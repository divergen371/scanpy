import socket
import ssl
import sys


BUFSIZE = 4096
target_ip = "127.0.0.1"
target_port = 8000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((target_ip, target_port))
# s = ssl.wrap_socket(
#     s,
#     keyfile=None,
#     certfile=None,
#     server_side=False,
#     cert_reqs=ssl.CERT_NONE,
#     ssl_version=ssl.PROTOCOL_TLSv1_2,
# )


while True:
    s.send(b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n")

    res = s.recv(BUFSIZE)
    print(res)
    if len(res) < BUFSIZE:
        break
