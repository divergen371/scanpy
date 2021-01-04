"""
Subdomain scanner.
"""
import requests
from requests import ConnectionError, Timeout
import sys
from threading import Thread, Lock
from queue import Queue


lock = Lock()


class FileIO:
    def __init__(self, read: str, write: str):
        self.read = read
        self.write = write
        self._discovered_subdomains = []

    def list_opener(self) -> list[str]:
        with open(self.read) as read_file:
            name_list = read_file.read()
            subdomains = name_list.splitlines()
            return subdomains

    def file_writing(self):
        self._discovered_subdomains.sort()
        with open(self.write, "w") as f:
            for subdomain in self._discovered_subdomains:
                print(subdomain, file=f)

    def discovered_subdomain_nameappend(self, discosub: str) -> None:
        self._discovered_subdomains.append(discosub)


q = Queue()


def scan_subdomain(domain):
    while True:
        subdomain = q.get()
        url = f"http://{subdomain}.{domain}"
        try:
            requests.get(url, timeout=(3, 10))
        except (ConnectionError, Timeout):
            pass
        else:
            print("[*] Discovered subdomain: {}".format(url))
            with lock:
                fileIO.discovered_subdomain_nameappend(url)
        q.task_done()


if __name__ == "__main__":
    domain = sys.argv[1]
    file = sys.argv[2]
    output_file_name = sys.argv[3]
    fileIO = FileIO(file, output_file_name)

    for subdomain in fileIO.list_opener():
        q.put(subdomain)

    for i in range(10):
        w = Thread(target=scan_subdomain, args=(domain,))
        w.daemon = True
        w.start()

    q.join()

    fileIO.file_writing()
