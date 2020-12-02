from datetime import datetime
import threading
import sys
import re
from logging import ERROR, getLogger
from queue import Queue
from scapy.layers.inet import IP, ICMP, TCP
from scapy.sendrecv import sr, sr1

import netaddr
from scapy.volatile import RandShort

getLogger("scapy.runtime").setLevel(ERROR)
try:
    network_cidr = input("[*]Enter the target (e.g 192.168.1.0/24): ")
    # regexp = re.fullmatch(
    #     "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$",
    #     network_cidr,
    # )
    ip_range = netaddr.IPNetwork(network_cidr)
    all_hosts = list(ip_range)
    print("[*] Target network: ", ip_range)
except KeyboardInterrupt:
    print("\n[*] Requested shutdown...")
    print("[*] Bye:)")
    sys.exit(1)

iface = "enp0s25"
time_out = 3
waking_host = []
print_lock = threading.Lock()


def icmp_sweep(ip: int):
    """
    Generate a packet containing the ICMP header and Confirmation of control messages.
    ip: int
        Figures taken from the worker. Based on this, retrieve the target from "all_host".
    """
    reply = sr1(
        IP(dst=str(all_hosts[ip])) / ICMP(), timeout=time_out, iface=iface, verbose=0
    )
    with print_lock:
        if reply is None:
            print("[*] {} is not running.".format(all_hosts[ip]))
        elif (
            int(reply.getlayer(ICMP).type) == 3
            and int(reply.getlayer(ICMP).code in [1, 2, 3, 9, 10, 13])
            and reply is None
        ):
            print("[*] {} is down".format(all_hosts[ip]))
        else:
            print("[*] {} is waking".format(all_hosts[ip]))
            waking_host.append(all_hosts[ip])


def syn_sweep(ip):
    SYNACK = 0x12
    RSTACK = 0x14
    reply = sr1(
        IP(dst=str(all_hosts[ip])) / TCP(dport=80, flags="S"),
        timeout=time_out,
        # iface=iface,
        verbose=0,
    )
    with print_lock:
        if reply is None:
            print("[*] {} is not running.".format(all_hosts[ip]))
        elif int(reply.getlayer(TCP).flags) in [SYNACK, RSTACK]:
            print("[*] {} is waking".format(all_hosts[ip]))
            waking_host.append(all_hosts[ip])
        else:
            print("[*] {} is state unknown.")


def ack_sweep(ip):
    RST = 0x04
    reply = sr1(
        IP(dst=str(all_hosts[ip])) / TCP(dport=80, flags="A"),
        timeout=time_out,
        verbose=0,
    )
    with print_lock:
        if reply is None:
            print("[*] {} is not running.".format(all_hosts[ip]))
        elif int(reply.getlayer(TCP).flags) == RST:
            print("[*] {} is waking.".format(all_hosts[ip]))
            waking_host.append(all_hosts[ip])
        else:
            print("[*] {} is state unknown.")


q = Queue()


def threader():
    """

    Extract the task from the queue and assign it to the sweep function.

    """
    while True:
        worker = q.get()
        # icmp_sweep(worker)
        ack_sweep(worker)
        # syn_sweep(worker)
        q.task_done()


if __name__ == "__main__":
    start_time = datetime.now()
    for x in range(100):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()

    # Create as many tasks as the number of hosts and pool them into a queue.(Send tasks to threader)
    for worker in range(len(all_hosts)):
        q.put(worker)

    # block until complete process all task.
    q.join()

    total_duration = datetime.now() - start_time
    print("[*] number of waking host {}".format(len(waking_host)))
    print("[*]Total time duration: " + str(total_duration))
