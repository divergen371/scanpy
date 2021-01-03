"""
Subdomain scanner.
"""
import requests
import sys

domain = sys.argv[1]
file = sys.argv[2]
output_file_name = sys.argv[3]


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
        with open(self.write, "w") as f:
            for subdomain in self._discovered_subdomains:
                print(subdomain, file=f)

    def discovered_subdomain_nameappend(self, discosub: str) -> None:
        self._discovered_subdomains.append(discosub)


fileIO = FileIO(file, output_file_name)

for subdomain in fileIO.list_opener():
    url = f"http://{subdomain}.{domain}"
    try:
        requests.get(url)
    except requests.ConnectionError:
        pass
    else:
        print("[*] Discovered subdomain: {}".format(url))
        fileIO.discovered_subdomain_nameappend(url)

fileIO.file_writing()
