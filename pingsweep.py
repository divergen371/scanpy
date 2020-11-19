# from colorama import init
from datetime import datetime
from time import strftime
import threading
from queue import Queue
from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import sr, sr1

import netaddr

# init()
print_lock = threading.Lock()

network_cidr = input("Enter the target (e.g 192.168.1.0/24)")

start_time = datetime.now()

ip_range = netaddr.IPNetwork(network_cidr)

all_hosts = list(ip_range)

iface = "enp0s25"
time_out = 3
waking_host = []
print("[*] Target network: ", ip_range)


# def sweep(ip):
#     output = subprocess.Popen(
#         ["ping", "-n", "1", "-w", "150", str(all_hosts[ip])],
#         stdout=subprocess.PIPE,
#     ).communicate()[0]
#
#     with print_lock:
#         print("\033[93m", end="")
#         if "Reply" in output.decode("utf-8"):
#             print(str(all_hosts[ip]), "033[32m" + "was awake.")
#         elif "Destination host unreachable" in output.decode("utf-8"):
#             # print unreachable
#             pass
#         elif "Request timed out" in output.decode("utf-8"):
#             # print timeout
#             pass
#         else:
#             print("UNKNOWN", end="")


def sweep(ip):
    """
    Generate a packet containing the ICMP header and Confirmation of control messages.

    """
    reply = sr1(
        IP(dst=all_hosts[ip]) / ICMP(), timeout=time_out, iface=iface, verbose=0
    )
    with print_lock:
        if int(reply.getlayer(ICMP).type) == 3 and int(
            reply.getlayer(ICMP).code in [1, 2, 3, 9, 10, 13]
        ):
            print("[*] {} is down".format(all_hosts[ip]))
        # elif int(
        #     reply.getlayer(ICMP) == 3
        #     and int(reply.getlayer(ICMP).code) in [1, 2, 3, 9, 10, 13]
        # ):
        #     print("[*] {} is ignore ICMP".format(all_hosts[ip]))
        else:
            print("[*] {} is waking".format(all_hosts[ip]))
            waking_host.append(all_hosts[ip])


q = Queue()


def threader():
    """

    Extract the task from the queue and assign it to the sweep function.

    """
    while True:
        worker = q.get()
        sweep(worker)
        q.task_done()


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
