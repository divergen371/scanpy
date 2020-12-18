import requests
import sys

domain = sys.argv[1]


file = open(sys.argv[2])

name_list = file.read()
subdomains = name_list.splitlines()

discovered_subdomains = []
for subdomain in subdomains:
    url = f"http://{subdomain}.{domain}"
    try:
        requests.get(url)
    except requests.ConnectionError:
        pass
    else:
        print("[*] Discovered subdomain: {}".format(url))
        discovered_subdomains.append(url)

with open("discovered_subdomains_list.txt", "w") as f:
    for subdomain in discovered_subdomains:
        print(subdomain, file=f)
