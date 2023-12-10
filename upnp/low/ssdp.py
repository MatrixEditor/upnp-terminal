from string import whitespace
from requests import get

UDP_MCAST_ADDR = '239.255.255.250'
UDP_SSDP_PORT = 1900

# region SSDP
SSDP_HEAD_NOTIFY = 'NOTIFY'
SSDP_HEAD_MSEARCH = 'M-SEARCH'
SSDP_HTTP = 'HTTP/1.1'

SSDP_ALIVE = 'ssdp:alive'
SSDP_BYE = 'ssdp:byebye'
SSDP_UPDATE = 'ssdp:update'
SSDP_ALL = 'ssdp:all'
SSDP_DISCOVER = 'ssdp:discover'

SSDP_TTL = 2  # page 31 l.24

# region NOTIFY
# These fields are required in a NOTIFY-Packet
NOTIFY_HOST = 'HOST'
NOTIFY_CACHE_CONTROL = 'CACHE-CONTROL'
NOTIFY_LOCATION = 'LOCATION'
NOTIFY_NT = 'NT'
NOTIFY_NTS = 'NTS'  # either 'ssdp:alive' or 'ssdp:byebye' (rare 'ssdp:update')
NOTIFY_SERVER = 'SERVER'
NOTIFY_USN = 'USN'

# didn't see those types of fields in captured packets
# also required (read page 29-30)
NOTIFY_BOOTID = 'BOOTID.UPNP.ORG'
NOTIFY_CONFIGID = 'CONFIGID.UPNP.ORG'

# allowed fields below
NOTIFY_SEARCHPORT = 'SEARCHPORT.UPNP.ORG'
NOTIFY_SECURELOCATION = 'SECURELOCATION.UPNP.ORG'

# required field in ssdp:update-NOTIFY message
NOTIFY_NEXTBOOTID = 'NEXTBOOTID.UPNP.ORG'

# region SEARCH
# These fields are required in a SEARCH-Packet
SEARCH_HOST = NOTIFY_HOST
SEARCH_MAN = 'MAN'  # always with double quotes, e.g. "ssdp:discover"
SEARCH_MX = 'MX'
SEARCH_ST = 'ST'  # refer to page 36 for more information

# didn't see this field, but it should be required
SEARCH_CPFN = 'CPFN.UPNP.ORG'

# allowed fields below
SEARCH_USER_AGENT = 'USER-AGENT'
SEARCH_TCPPORT = 'TCPPORT.UPNP.ORG'
SEARCH_CPUUID = 'CPUUID.UPNP.ORG'


def escapeCLRF(data: str) -> list:
    if not data:
        return
    else:
        return data.replace("\r", "").split("\n")


def malformed(header: str) -> bool:
    if SSDP_HEAD_NOTIFY in header or SSDP_HEAD_MSEARCH in header:
        return False
    elif SSDP_HTTP in header:
        return False
    else:
        return True


class SSDPHeader(object):
    def __init__(self, head: str) -> None:
        super().__init__()

        if '\r' in head:
            head = head.replace('\r', "")
        elif '\n' in head:
            head = head.replace("\n", "")

        parts = head.split(" ")
        if len(parts) >= 3:
            self.start = parts[0]
            self.spec = parts[1]
            self.end = parts[2]
        else:
            print("[!] Reading an empty header.")
            self.start = 'None'  # be printable and throw no error
            self.spec = 'None'
            self.end = 'None'

    def __str__(self) -> str:
        return ' '.join([self.start, self.spec, self.end])


class SSDPPacket(object):
    def __init__(self, data: str, host, port) -> None:
        super().__init__()

        self.fields = None
        self.header = None
        self.host = host
        self.port = port
        self.load(data)

    def load(self, data: str):
        if not data:
            self.header = None
            self.fields = None
            print("[!] Loading malformed packet. (It's null)")
            return

        message = escapeCLRF(data=data)
        if malformed(message[0]):
            self.header = None
            self.fields = None
            print("[!] Loading malformed packet. Maybe it's not SSDP %s" % (message[0]))
            return
        self.header = SSDPHeader(message[0])

        # Now remove the header for iterating purposes
        message = message[1:]
        self.fields = dict()
        for field in message:
            if not field:
                continue
            else:
                i = field.index(':')

                # this prevents getting errors when searching fields
                fname = field[:i].upper()
                fvalue = field[i + 1:]
                if fvalue:
                    if fvalue[0] in whitespace:  # escape whitespace at start
                        fvalue = fvalue[1:]
                self.fields.setdefault(fname, fvalue)

    def show(self):
        indent = ' ' * 4

        print("[>] SSDP-Packet (Host: %s | Port: %s) (Header: %s)" % (self.host, self.port,
                                                                      self.header.__str__() if self.header != None else 'None'))
        if self.fields == None:
            print("%s[*] No message fields" % (indent))
        else:
            for k in self.fields:
                print("%s| %s: %s" % (indent, k, self.fields[k]))
        print()

    def head(self) -> SSDPHeader:
        return self.header

    def get(self, attr: str) -> object:
        try:
            return self.fields[attr]
        except:
            return None

    def __str__(self) -> str:
        repr = ""
        indent = ' ' * 4

        repr += "[>] SSDP-Packet (Host: %s | Port: %s) (Header: %s)" % (self.host, self.port,
                                                                        self.header.__str__() if self.header != None else 'None')
        if self.fields == None:
            repr += "\n%s[*] No message fields" % (indent)
        else:
            for k in self.fields:
                repr += "\n%s| %s: %s" % (indent, k, self.fields[k])
        return repr


def locate(packet: SSDPPacket):
    if packet.head():

        if packet.head().start in [SSDP_HEAD_NOTIFY, SSDP_HTTP]:
            # [Location] - a url for more information
            location = packet.fields[NOTIFY_LOCATION]

            if location:
                # requests HTTP-get
                page = get(location)

                if not page:
                    print("[!] No web-page found")
                else:
                    return (page.headers, page.text)
            else:
                print("[!] No location found")


def searchpayload(host=UDP_MCAST_ADDR, port=UDP_SSDP_PORT, man=SSDP_DISCOVER, st=SSDP_ALL, mx=2):
    payload = None
    if mx:
        payload = (
            "{} * {}\r\n"
            "HOST: {}:{}\r\n"
            "ST: {}\r\n"
            'MAN: "{}"\r\n'
            "MX: {}\r\n\r\n"
        ).format(SSDP_HEAD_MSEARCH, SSDP_HTTP, host, port, st, man, mx)
    else:
        payload = (
            "{} * {}\r\n"
            "HOST: {}:{}\r\n"
            'MAN: "{}"\r\n'
            "ST: {}\r\n\r\n"
        ).format(SSDP_HEAD_MSEARCH, SSDP_HTTP, host, port, man, st)
    return payload.encode("UTF-8")


def notifypayload(location, server, uuid, host=UDP_MCAST_ADDR, port=UDP_SSDP_PORT, cache=1800, nt='upnp:rootdevice',
                  nts=SSDP_ALIVE, usn='upnp:rootdevice'):
    payload = (
        "{} * {}"
        "HOST: {}:{}"
        "CACHE-CONTROL: max-age={}"
        "LOCATION: {}"
        "NT: {}"
        "NTS: {}"
        "SERVER: {}"
        "USN: {}"
    ).format(host, port, cache, location, nt, nts, f'uuid:{uuid}:{server}', f'uuid:{uuid}:{usn}')
    return payload.encode("UTF-8")


# 'urn:schemas-upnp-org:device:InternetGatewayDevice:1'
def msearch(client, host=UDP_MCAST_ADDR, port=UDP_SSDP_PORT, st=SSDP_ALL, man=SSDP_DISCOVER, mx=2) -> list:
    '''
    Default implementation for multicast-search via SSDP
    '''
    data = searchpayload(host=host, port=port, man=man, st=st, mx=mx)
    if client and data:
        client.bsend(data)
        return [x for x in client.recv()]


def usearch(client, host=UDP_MCAST_ADDR, port=UDP_SSDP_PORT, man=SSDP_DISCOVER, st=SSDP_ALL) -> list:
    '''
    Default implementation for unicast-search via SSDP
    '''
    data = searchpayload(host=host, port=port, man=man, st=st, mx=None)
    if client and data:
        client.bsend(data)
        return [x for x in client.recv()]


def notify(client, location, uuid, server, host=UDP_MCAST_ADDR, port=UDP_SSDP_PORT, cache=1800, nt='upnp:rootdevice',
           nts=SSDP_ALIVE, usn='upnp:rootdevice'):
    data = notifypayload(host=host, port=port, location=location,
                         nt=nt, nts=nts, uuid=uuid, usn=usn, server=server)
    if client and data:
        client.bsend(data)
        return [x for x in client.recv()]
