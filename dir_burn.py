"""
Directory and file bruteforce script from black hat python.
"""
import sys
import requests
from threading import Thread
from queue import Queue

threads = 10
target = sys.argv[1]
wordlist = sys.argv[2]
resume_state = None
user_agent = "Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0"


def wordlist_builder(wordlist) -> Queue:
    words = Queue()
    resume = False
    with open(wordlist, "r", encoding="utf-8") as reading:
        lines = reading.readlines()
        for word in lines:
            if resume_state is not None:
                if resume:
                    words.put(word.rstrip())
                else:
                    if word == resume_state:
                        resume = True
                        print(f"Resuming wordlist from: {resume_state}")
            words.put(word.rstrip())
    return words


def bruter(word_queue, extentions=None):
    while not word_queue.empty():
        attempt = word_queue.get()
        attempt_list = []
        if "." not in attempt:
            attempt_list.append(f"/{attempt}/")
        else:
            attempt_list.append(f"/{attempt}")

        if extentions:
            for extention in extentions:
                attempt_list.append(f"/{attempt}{extention}")

        for brute in attempt_list:
            url = f"{target}{brute}"
            try:
                headers = {"User_Agent": user_agent}
                r = requests.get(url, headers=headers)
                if r.status_code != 404:
                    print(f"[{r.status_code}] => {url}")
            except:
                print(f"! {r.status_code} => {url}")
                pass


def main():
    word_queue = wordlist_builder(wordlist)
    extentions = [".php", ".bak", ".orig", ".inc"]

    print("[*] Start...")
    for i in range(threads):
        t = Thread(target=bruter, args=[word_queue, extentions])
        t.daemon = True
        t.start()


if __name__ == "__main__":
    main()
