# response_parser.py
# Jacob Schwartz (schwartzj1)


class Parser:

    def __init__(self, msg_type, string):
        self.msg_type = msg_type
        self.msg = string

    def a_first(self):
        ip = list()
        index = self.msg.find("c0")
        opcode = self.msg[index + 7: index + 8]
        index += 22
        loc = index

        if opcode == "5":
            cname = list()

            if int(self.msg[index + 2: index + 4], 16) == 192:  # Tests for compressed names
                index = (int(self.msg[index + 4: index + 6], 16)) * 2

                while int(self.msg[index: index + 2], 16) != 0:
                    length = int(self.msg[index: index + 2], 16)
                    index += 2
                    section = list()

                    for x in range(index, index + (length * 2), 2):
                        section.append(chr(int(self.msg[x:x + 2], 16)))

                    index += 2 * (len(section))
                    cname.append("".join(section))
            else:
                index += 2
                while int(self.msg[index: index + 2], 16) != 0:
                    length = int(self.msg[index: index + 2], 16)
                    index += 2
                    section = list()

                    for x in range(index, index + (length * 2), 2):
                        section.append(chr(int(self.msg[x:x + 2], 16)))

                    index += 2 * (len(section))
                    cname.append("".join(section))

            loc = self.msg.find("00010001")
            loc = self.msg[loc + 1:].find("00010001") + loc + 19
            # print(loc)
            length = int(self.msg[loc:loc + 2], 16)
            # print(length)
            loc += 2

            for x in range(loc, loc + (length * 2), 2):
                ip.append(str(int(self.msg[x:x + 2], 16)))

            return ".".join(cname), ".".join(ip)
        else:
            length = int(self.msg[index:index + 2], 16)
            index += 2

            for x in range(index, index + (length * 2), 2):
                ip.append(str(int(self.msg[x:x + 2], 16)))

            return None, ".".join(ip)

    def ptr_first(self):
        address = list()
        index = self.msg.find("c0") + 24

        while int(self.msg[index: index + 2], 16) != 0:
            length = int(self.msg[index: index + 2], 16)
            index += 2
            section = list()

            for x in range(index, index + (length * 2), 2):
                section.append(chr(int(self.msg[x:x + 2], 16)))

            index += 2 * (len(section))
            address.append("".join(section))

        return None, ".".join(address)
