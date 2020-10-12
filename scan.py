from logging import getLogger, ERROR

getLogger("scapy.runtime").setLevel(ERROR)
from scapy.all import *
import sys
from datetime import datetime
from time import strftime


try:
    target = input("[*] Enter Target IP address :")
    min_port = input("[*] Enter Min Port Number: ")
    max_port = input("[*] Enter Max Port Number: ")

    try:
        if int(min_port) >= 0 and int(max_port) >= 0 and int(max_port) >= int(min_port):
            pass
        else:
            print("\n[!] Invalid Range of Ports")
            print("[!] Exiting...")
            sys.exit(1)
    except Exception:
        print("\n[!] Invalid Range of Ports")
        print("[!] Exiting...")
        sys.exit(1)
except KeyboardInterrupt:
    print("\n[*] User Requested Shutdown...")
    print("[*] Exiting...")
    sys.exit(1)
