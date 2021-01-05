"""
Subdomain scanner.
"""
import argparse
import requests
from requests import ConnectionError, Timeout
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

    def discovered_subdomain_append(self, discosub: str) -> None:
        self._discovered_subdomains.append(discosub)


q = Queue()


def scan_subdomain(target_domain: str, user_agent: str, read_timeout: int) -> None:
    while True:
        sub_domain = q.get()
        url = f"http://{sub_domain}.{target_domain}"
        try:
            header = {"User_Agent": user_agent}
            requests.get(url, timeout=(3, read_timeout), headers=header)
        except (ConnectionError, Timeout):
            pass
        else:
            print("[*] Discovered subdomain: {}".format(url))
            with lock:
                fileIO.discovered_subdomain_append(url)
        q.task_done()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="subdomain scan script")
    parser.add_argument(
        "-d",
        dest="domain",
        help="The domain name for which you want to investigate subdomains. (Please specify without protocol.)",
        required=True,
    )
    parser.add_argument(
        "-w",
        dest="wordlist",
        help="Specify the file that contains the subdomain candidates.",
    )
    parser.add_argument(
        "-o",
        dest="outputfile",
        help="The name of the file to save the discovered subdomain names.",
    )
    parser.add_argument(
        "-t",
        dest="threads",
        help="Number of threads to use for subdomain scanning.(default 10)",
        default=10,
        type=int,
    )
    parser.add_argument(
        "-u",
        dest="useragent",
        help="""Specification of user agent.\n
                (default user agent: Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0)
        """,
        default="Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0",
    )
    parser.add_argument(
        "-T",
        dest="readtimeout",
        help="Server response latency(default 10s).",
        default=30,
        type=int,
    )
    args = parser.parse_args()
    domain = args.domain
    file = args.wordlist
    output_file_name = args.outputfile
    thread_num = args.threads
    useragent = args.useragent
    readtimeout = args.readtimeout
    fileIO = FileIO(file, output_file_name)

    for subdomain in fileIO.list_opener():
        q.put(subdomain)

    for i in range(thread_num):
        w = Thread(
            target=scan_subdomain,
            args=(
                domain,
                useragent,
                readtimeout,
            ),
        )
        w.daemon = True
        w.start()

    q.join()

    fileIO.file_writing()
