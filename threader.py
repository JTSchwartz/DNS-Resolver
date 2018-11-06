# threader.py
# Jacob Schwartz (schwartzj1)

from threading import *
import time
from udpsocket import *
from resource_record import *
from response_parser import Parser


class Threader(Thread):

    time_delays = list()
    thread_lock = Lock()
    successful = [0]
    no_dns = [0]
    no_auth = [0]
    dns_timeout = [0]
    retx = [0]
    send_count = [0,0,0]
    full_response = list()

    def __init__(self, thread_id, shared_queue, dns_ip):
        Thread.__init__(self)
        self.id = thread_id
        self.host_list = shared_queue
        self.dns_ip = dns_ip

    def run(self):
        connection = UDPSocket()

        while not self.host_list.empty():

            host = self.host_list.get()
            rr = determine(host, self.id)

            if rr.rr_type is 'PTR':
                split = host.split(".")
                invalid = False
                for x in split:
                    if int(x) > 255:
                        self.full_response.append("Invalid IP address\n")
                        invalid = True
                        break
                if invalid:
                    continue

            connection.create(self.dns_ip)
            response, attempts, delay = connection.run(rr.message)
            self.update_counts(attempts)

            if response is None:
                self.full_response.append("DNS server timeout\n")
                self.thread_lock.acquire()
                self.dns_timeout[0] += 1
                self.retx[0] += attempts
                self.thread_lock.release()
                continue
            elif "{0:b}".format(int(response[4:8], 16))[12:] == "0010":
                self.full_response.append("No Authoritative DNS server found\n")
                self.thread_lock.acquire()
                self.no_auth[0] += 1
                self.retx[0] += attempts
                self.thread_lock.release()
                continue
            elif "{0:b}".format(int(response[4:8], 16))[12:] == "0011":
                self.full_response.append("No DNS entry\n")
                self.thread_lock.acquire()
                self.no_dns[0] += 1
                self.retx[0] += attempts
                self.thread_lock.release()
                continue

            self.time_delays.append(delay)
            parser = Parser(rr.rr_type, response)
            cname, answer = parser.a_first() if rr.rr_type is 'A' else parser.ptr_first()
            if cname is not None:
                self.full_response.append("Answer:\n{} is aliased to {}\n{} is {}".format(host, cname, cname, answer))
            else:
                self.full_response.append("Answer:\n{} is {}\n".format(host, answer))

            self.thread_lock.acquire()
            self.successful[0] += 1
            self.retx[0] += attempts
            self.thread_lock.release()

    def update_counts(self, num):
        self.send_count[num - 1] += 1
