from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA256
import socket
from threading import Thread

import sys
import pickle

random_generator = Random.get_random_bytes
key = RSA.generate(2048, random_generator)
public_key = key.publickey()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(("0.0.0.0", 4444))
except socket.error as v:
    print("Binding failed. Error code : " + str(v[0]) + " Message " + v[1])
    sys.exit()

print("Socket bind complete.")


s.listen(2)
print("[+] Listening to the incoming connection on port 4444.")


def clientthread_sendpubkey(client):
    client.send(pickle.dump(public_key))
