import multiprocessing as mp
from multiprocessing import Queue, Process
import sys
from datetime import datetime
from logging import ERROR, getLogger

from scapy.config import conf
from scapy.layers.inet import ICMP, IP, TCP
from scapy.sendrecv import send, sr1
from scapy.volatile import RandShort
from time import strftime

getLogger("scapy.runtime").setLevel(ERROR)
try:
    target_ip = input("[*] Enter Target IP address :")
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

SYNACK = 0x12
RSTACK = 0x14


def scan(port):
    try:
        src_port = RandShort()
        syn_pkt = sr1(IP(dst=target_ip) / TCP(sport=src_port, dport=port, flags="S"))
        return_pkt_flag = syn_pkt.getlayer(TCP).flags
        if return_pkt_flag == SYNACK:
            return True
        else:
            return False
        rst_pkt = sr1(IP(dst=target_ip) / TCP(sport=src_port, dport=port, flags="R"))
        send(rst_pkt)
    except KeyboardInterrupt:
        rstpkt = sr1(IP(dst=target_ip) / TCP(sport=src_port, dport=port, flags="R"))
        send(rstpkt)
        print("exit.")
        sys.exit(1)


def check_alive(ip):
    print("[*] Scanning started at " + strftime("%H:%M:%S") + "!\n")
    try:
        sr1(IP(dst=ip) / ICMP())
        print("\n[*] Target found! %s is waking" % target_ip)
    except Exception:
        print("\n[!] Target not found")
        print("[*] Exiting...")
        sys.exit(1)


if __name__ == "__main__":
    results_pool = []
    conf.verb = 0
    start = datetime.now()
    check_alive(target_ip)
    ports = range(int(min_port), int(max_port) + 1)
    for port in ports:
        status = scan(port)
        if status:
            print("Port {} is open.".format(port))
    total_duration = datetime.now() - start

    print("\n[*]%s Scan complete" % target_ip)
    print("[*]Total time duration: " + str(total_duration))
