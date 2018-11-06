# udpsocket.py
# Jacob Schwartz (schwartzj1)

import binascii
import time
from socket import *


class UDPSocket:

    def __init__(self):
        self.sock = None
        self.host = ""
        self.dns = None

    def create(self, dns_ip):
        self.dns = (dns_ip, 53)

        try:
            self.sock = socket(AF_INET, SOCK_DGRAM)
        except error:
            print("Socket Generation Error: {}".format(error))

    def run(self, message, count=1):
        receive = None
        start = end = 0
        try:
            self.sock.settimeout(5)
            start = time.time()
            self.sock.sendto(binascii.unhexlify(message), self.dns)
            receive, _ = self.sock.recvfrom(4096)
            end = time.time()
            receive = binascii.hexlify(receive).decode("utf-8")
        except timeout:
            if count <= 3:
                count += 1
                self.run(message, count)
            else:
                return None, count, 0
        except error:
            print("Socket Error: {}".format(error))
        finally:
            self.close_socket()
            return receive, count, end - start

    def close_socket(self):
        self.sock.close()
