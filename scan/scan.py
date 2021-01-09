"""
Multi threaded port scanner with scapy.
"""
import sys
from datetime import datetime
from logging import ERROR, getLogger
import threading
from queue import Queue

from scapy.config import conf
from scapy.layers.inet import ICMP, IP, TCP
from scapy.sendrecv import send, sr1
from scapy.volatile import RandShort
from time import strftime

getLogger("scapy.runtime").setLevel(ERROR)

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

SYNACK = 0x12
RSTACK = 0x14
lock = threading.Lock()


def scan(dst_port: int):
    try:
        src_port = RandShort()
        syn_pkt = sr1(
            IP(dst=target_ip) / TCP(dport=dst_port, flags="S"),
            timeout=2,
        )
        rst_pkt = IP(dst=target_ip) / TCP(sport=src_port, dport=dst_port, flags="R")
        with lock:
            if syn_pkt is None:
                print(f"Port {dst_port} is filtered")
                return None
            return_pkt_flag = syn_pkt.getlayer(TCP).flags
            if return_pkt_flag == SYNACK:
                print(f"Port {dst_port} is open")
                send(rst_pkt)
                return True
            else:
                send(rst_pkt)
                return False

    except KeyboardInterrupt:
        src_port = RandShort()
        rst_pkt = IP(dst=target_ip) / TCP(sport=src_port, dport=dst_port, flags="R")
        send(rst_pkt)
        print("exit.")
        sys.exit(1)


def check_alive(ip: str) -> None:
    print("[*] Scanning started at " + strftime("%H:%M:%S") + "!\n")
    try:
        sr1(IP(dst=ip) / ICMP())
        print(f"\n[*] Target found! {ip} is waking")
    except Exception:
        print("\n[!] Target not found")
        print("[*] Exiting...")
        sys.exit(1)


def threader():
    while True:
        worker = q.get()
        scan(worker)
        q.task_done()


if __name__ == "__main__":
    q = Queue()
    conf.verb = 0
    start_time = datetime.now()
    check_alive(target_ip)
    ports = range(int(min_port), int(max_port) + 1)

    for x in range(100):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()

    for worker in ports:
        q.put(worker)

    q.join()
    total_duration = datetime.now() - start_time

    print("\n[*]%s Scan complete" % target_ip)
    print("[*]Total time duration: " + str(total_duration))
