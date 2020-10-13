from logging import getLogger, ERROR

from scapy.layers.inet import ICMP, IP, TCP
from scapy.sendrecv import sr1

getLogger("scapy.runtime").setLevel(ERROR)
import sys
from datetime import datetime
from time import strftime

try:
    target = input("[*] Enter Target IP address :")
    min_port = input("[*] Enter Min Port Number: ")
    max_port = input("[*] Enter Max Port Number: ")

    try:
        if 0 <= int(min_port) <= int(max_port) and int(max_port) >= 0:
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

ports = range(int(min_port), int(max_port) + 1)
start_clock = datetime.now()
SYNACK = 0x12
RSTACK = 0x14


def checkhost(ip):
    conf.verb = 0
    try:
        sr1(IP(dst=ip) / ICMP())
        print("\n[*] Target is Up, Beginning Scan...")
    except Exception:
        print("\n[!] Couldn't Resolve Target")
        print("[!] Exiting...")
        sys.exit(1)


def scanport(port):
    srcport = RandShort()
    conf.verb = 0
    SYNACKpkt = sr1(IP(dst=target) / TCP(sport=srcport, dport=port, flags="S"))
    pktflags = SYNACKpkt.getlayer(TCP).flags
    if pktflags == SYNACK:
        return True
    else:
        return False

    RSTpkt = IP(dst=target) / TCP(sport=srcport, dport=port, flags="R")
    send(RSTpkt)


checkhost(target)
print("[*] Scanning Started at " + strftime("%H:%M:%S") + "!\n")

for port in ports:
    status = scanport(port)
    if status == True:
        print("Port " + str(port) + ": Open")

stop_clock = datetime.now()
total_time = stop_clock - start_clock
print("\n[*] Scanning Finished:)")
print("[*] Total Scan Duration: " + str(total_time))
