import sys
import threading
from datetime import datetime
from logging import ERROR, getLogger
from queue import Queue

import argparse
import netaddr
from scapy.config import conf
from scapy.layers.inet import ICMP, IP, TCP
from scapy.layers.l2 import ARP, ARPingResult, Ether
from scapy.sendrecv import sr1, srp

getLogger("scapy.runtime").setLevel(ERROR)
parser = argparse.ArgumentParser(prog="pingsweep.py")
parser.add_argument(
    "network_cidr", help="network range Specifications (e.g 192.168.1.0/24)"
)
parser.add_argument(
    "-m", "--mode", type=str, required=True, default="i", choices=["i", "a", "s", "arp"]
)
args = parser.parse_args()

try:
    # network_cidr = input("[*]Enter the target (e.g 192.168.1.0/24): ")
    network_cidr = str(args.network_cidr)
    ip_range = netaddr.IPNetwork(network_cidr)
    all_hosts = list(ip_range)
    print("[*] Target network: ", ip_range)
except KeyboardInterrupt:
    print("\n[*] Requested shutdown...")
    print("[*] Bye:)")
    sys.exit(1)

iface = conf.iface
time_out = 3
print_lock = threading.Lock()


class PingType:
    def __init__(self, ip):
        self.ip = ip

    def icmp_ping(self) -> None:
        """
        Generate a packet containing the ICMP header and Confirmation of control messages.
        ip: int
            Figures taken from the worker. Based on this, retrieve the target from "all_host".
        """
        conf.verb = 0
        reply = sr1(
            IP(dst=str(all_hosts[self.ip])) / ICMP(), timeout=time_out, iface=iface
        )
        with print_lock:
            if reply is None:
                print("[*] {} is not running.".format(all_hosts[self.ip]))
            elif (
                int(reply.getlayer(ICMP).type) == 3
                and int(reply.getlayer(ICMP).code in [1, 2, 3, 9, 10, 13])
                and reply is None
            ):
                print("[*] {} is down".format(all_hosts[self.ip]))
            else:
                print("[*] {} is waking".format(all_hosts[self.ip]))

    def syn_ping(self) -> None:
        conf.verb = 0
        SYNACK = 0x12
        RSTACK = 0x14
        reply = sr1(
            IP(dst=str(all_hosts[self.ip])) / TCP(dport=80, flags="S"),
            timeout=time_out,
            iface=iface,
        )
        with print_lock:
            if reply is None:
                pass
            elif int(reply.getlayer(TCP).flags) in [SYNACK, RSTACK]:
                print("[*] {} is waking".format(all_hosts[self.ip]))

    def ack_ping(self) -> None:
        conf.verb = 0
        RST = 0x04
        reply = sr1(
            IP(dst=str(all_hosts[self.ip])) / TCP(dport=80, flags="A"),
            timeout=time_out,
        )
        with print_lock:
            if reply is None:
                pass
            elif int(reply.getlayer(TCP).flags) == RST:
                print("[*] {} is waking.".format(all_hosts[self]))

    def arp_ping(self) -> None:
        conf.verb = 0
        ans, unans = srp(
            Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(all_hosts[self.ip])),
            timeout=time_out,
        )
        with print_lock:
            reply = ARPingResult(ans.res)
            reply.show()


q = Queue()


def threader(mode_flag):
    """

    Extract the task from the queue and assign it to the sweep function.

    """
    if mode_flag == "i":

        while True:
            worker = q.get()
            mode = PingType(worker)
            mode.icmp_ping()
            q.task_done()
    if mode_flag == "s":
        while True:
            worker = q.get()
            mode = PingType(worker)
            mode.syn_ping()
            q.task_done()
    if mode_flag == "a":
        while True:
            worker = q.get()
            mode = PingType(worker)
            mode.ack_ping()
            q.task_done()
    if mode_flag == "arp":
        while True:
            worker = q.get()
            mode = PingType(worker)
            mode.arp_ping()
            q.task_done()


if __name__ == "__main__":
    start_time = datetime.now()
    for x in range(100):
        t = threading.Thread(target=threader, args=(args.mode_flag,))
        t.daemon = True
        t.start()

    # Create as many tasks as the number of hosts and pool them into a queue.(Send tasks to
    # threader)
    for worker in range(len(all_hosts)):
        q.put(worker)

    # block until complete process all task.
    q.join()

    total_duration = datetime.now() - start_time
    print("[*]Total time duration: " + str(total_duration))
