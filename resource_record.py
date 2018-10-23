# resource_record.py
# Jacob Schwartz (schwartzj1)

import re
from socket import htons


class RR:
    rr_type: chr
    id = questions = addRRs = answers = authRRs = flags = 0
    host = question_section = message = ""

    def __init__(self, host, thread_id):
        self.host = host
        self.id = thread_id

    def create_message(self):
        split = self.host.split(".")
        self.message += str(self.id).zfill(4)
        self.message += "01000001000000000000"

        for substring in split:
            self.message += str(hex(len(substring)))[2:].zfill(2)
            self.message += self.to_hex(substring)

        self.message += "000001" if self.rr_type is 'A' else "00000c"
        self.message += "0001"

    @staticmethod
    def to_hex(s):
        lst = []
        for ch in s:
            hv = hex(ord(ch)).replace('0x', '')
            if len(hv) == 1:
                hv = '0' + hv
            lst.append(hv)

        return "".join(lst)


class A(RR):

    def __init__(self, host, thread_id):
        super().__init__(host, thread_id)
        self.rr_type = 'A'
        self.flags = htons(0x100)
        self.create_message()


class PTR(RR):

    def __init__(self, host, thread_id):
        host = self.format_host(host)
        super().__init__(host, thread_id)
        self.rr_type = 'PTR'
        self.flags = htons(256)
        self.create_message()

    @staticmethod
    def format_host(host):
        sections = host.split(".")
        sections.reverse()
        return ".".join(sections) + ".in-addr.arpa"


def determine(host, thread_id):

    if re.search('[a-zA-Z]', host):
        return A(host, thread_id)
    else:
        return PTR(host, thread_id)
