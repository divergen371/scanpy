# from colorama import init
from datetime import datetime
from time import strftime
import threading
from queue import Queue
from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import sr

import netaddr

# init()
print_lock = threading.Lock()

network_cidr = input("Enter the target (e.g 192.168.1.0/24)")

start_time = datetime.now()

ip_range = netaddr.IPNetwork(network_cidr)

all_hosts = list(ip_range)


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
    ans, unans = sr(IP(dst=all_hosts[ip]) / ICMP())


q = Queue()


def threader():
    """
    # create new task and
    # holding tasks till the end of works
    """
    while True:
        worker = q.get()
        sweep(worker)
        q.task_done()


for x in range(100):
    t = threading.Thread(target=threader)
    t.daemon = True
    t.start()


for worker in range(len(all_hosts)):
    q.put(worker)


q.join()

total_duration = datetime.now() - start_time

print("[*]Total time duration: " + str(total_duration))
