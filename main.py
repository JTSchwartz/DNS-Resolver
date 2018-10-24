# main.py
# Jacob Schwartz (schwartzj1)
from math import sqrt
import subprocess
import sys
from threader import Threader
import time
from queue import Queue

global local_dns


def get_local_dns():
    process = subprocess.Popen(["nslookup", "/"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()[0]
    process.kill()
    output = str(output.strip())
    if output.find("#") == -1:
        return output[output.find("Address:  ")+10:output.find("*")]
    else:
        return output[output.find("Address:  ") + 10:output.find("#")]


def batch(count):
    start = time.time()
    ip_queue = Queue()

    try:
        with open("dns-in.txt") as file:
            for line in file:
                ip_queue.put(line)
    except IOError:
        print("File does not exist")
        exit(1)

    thread_count = count
    thread_list = []

    for x in range(thread_count):
        t = Threader(x, ip_queue, local_dns)
        t.start()
        thread_list.append(t)

    for thread in thread_list:
        thread.join()

    end = time.time()


def interactive(args="www.google.com"):
    host = Queue()
    host.put(args)
    thread = Threader(1, host, local_dns)
    thread.start()
    thread.join()

    print("".join(Threader.result))


if __name__ == "__main__":
    local_dns = get_local_dns()

    if len(sys.argv) != 2:
        print("Requires exactly one argument, either number of threads for batch, or ip/hostname for interactive")

    mode = False
    n = 0
    arg = sys.argv[1]

    try:
        n = int(arg)
    except ValueError:
        mode = True

    if mode:
        interactive(arg)
    else:
        batch(n)
