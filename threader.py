# threader.py
# Jacob Schwartz (schwartzj1)

from threading import *
from udpsocket import *
from resource_record import *
from response_parser import Parser


class Threader(Thread):

    thread_lock = Lock()
    result = []

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
                        print("Invalid IP address")
                        invalid = True
                        break
                if invalid:
                    continue

            connection.create(self.dns_ip)
            response = connection.run(rr.message)

            if response is None:
                print("DNS server timeout")
                continue
            elif "{0:b}".format(int(response[4:8], 16))[12:] == "0010":
                print("No Authoritative DNS server found")
                continue
            elif "{0:b}".format(int(response[4:8], 16))[12:] == "0011":
                print("No DNS entry")
                continue

            parser = Parser(rr.rr_type, response)
            cname, answer = parser.a_first() if rr.rr_type is 'A' else parser.ptr_first()
            print("Answer:".format(host, answer))
            if cname is not None:
                print("{} is aliased to {}".format(host, cname))
                print("{} is {}".format(cname, answer))
            else:
                print("{} is {}".format(host, answer))
