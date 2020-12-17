import multiprocessing as mp
from multiprocessing import Queue
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
        rst_pkt = sr1(IP(dst=target_ip) / TCP(sport=src_port, dport=port, flags="R"))
        return_pkt_flag = syn_pkt.getlayer(TCP).flags
        if return_pkt_flag == SYNACK:
            print("[*] Port" + str(port) + " :Open")
            send(rst_pkt)
            return True
        else:
            send(rst_pkt)
            return False
    except KeyboardInterrupt:
        rstpkt = sr1(IP(dst=target_ip) / TCP(sport=src_port, dport=port, flags="R"))
        send(rstpkt)


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
    pool = mp.Pool(processes=mp.cpu_count() * 10)
    results = pool.apply_async(scan, args=ports)
    results_pool.append(results)
    print(results)
    total_duration = datetime.now() - start
    print("\n[*]%s Scan complete" % target_ip)
    print("[*]Total time duration: " + str(total_duration))
