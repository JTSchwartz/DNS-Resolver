# main.py
# Jacob Schwartz (schwartzj1)

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
                ip_queue.put(line[:line.find("\t")])
    except IOError:
        print("File does not exist")
        exit(1)

    entries = ip_queue.qsize()
    print("Starting batch mode with", count, "threads")
    print("Reading input file... found", entries, "entries\n...")

    thread_count = count
    thread_list = []

    for x in range(thread_count):
        t = Threader(x, ip_queue, local_dns)
        t.start()
        thread_list.append(t)

    for thread in thread_list:
        thread.join()

    end = time.time()
    print("Completed", entries, "queries")
    print("\tSuccessful: {0:.2f}%".format((Threader.successful[0]/entries) * 100))
    print("\tNo DNS {0:.2f}%".format((Threader.no_dns[0]/entries) * 100))
    print("\tNo Auth DNS Server: {0:.2f}%".format((Threader.no_auth[0]/entries) * 100))
    print("\tAverage Attempts: {0:.2f}".format(Threader.retx[0]/entries))
    print("\tRuntime: {0:.2f} seconds".format(end - start))
    print("Writing output file... finished with {} entries".format(len(Threader.full_response)))

    output = open("dns-out.txt", "w")
    output.write("\n".join(Threader.full_response))


def interactive(args="www.google.com"):
    host = Queue()
    host.put(args)
    thread = Threader(1, host, local_dns)
    thread.start()
    thread.join()

    print("\n".join(Threader.full_response))


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
