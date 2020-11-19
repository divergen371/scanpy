from datetime import datetime
import threading
from queue import Queue
from scapy.layers.inet import IP, ICMP, TCP
from scapy.sendrecv import sr, sr1

import netaddr
from scapy.volatile import RandShort

print_lock = threading.Lock()

network_cidr = input("Enter the target (e.g 192.168.1.0/24)")

start_time = datetime.now()

ip_range = netaddr.IPNetwork(network_cidr)

all_hosts = list(ip_range)

iface = "enp0s25"
time_out = 3
waking_host = []
print("[*] Target network: ", ip_range)


def icmp_sweep(ip):
    """
    Generate a packet containing the ICMP header and Confirmation of control messages.

    """
    reply = sr1(
        IP(dst=str(all_hosts[ip])) / ICMP(), timeout=time_out, iface=iface, verbose=0
    )
    with print_lock:
        if reply is None:
            print("[*] {} is not exist.".format(all_hosts[ip]))
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
    src_port = RandShort()
    reply = sr1(
        IP(dst=all_hosts[ip]) / TCP(sport=src_port, dport=80, flags="S"),
        timeout=time_out,
        iface=iface,
    )


q = Queue()


def threader():
    """

    Extract the task from the queue and assign it to the sweep function.

    """
    while True:
        worker = q.get()
        icmp_sweep(worker)
        q.task_done()


if __name__ == "__main__":
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
