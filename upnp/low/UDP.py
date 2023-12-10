import struct
import socket

UDP_MCAST_ADDR = '239.255.255.250'
UDP_SSDP_PORT = 1900

IPV4_MCAST_IP = UDP_MCAST_ADDR
IPV6_MCAST_IP = 'ff02::c'

SO_BINDTODEVICE = getattr(socket, "SO_BINDTODEVICE", 25)

class UDPMulticastClient(object):
    '''
    This UDP-Multicast client is based upon the documentation of 
    'ssdpy' (link below). This client only needs the send() and
    receive functions.    
    
    >>> https://ssdpy.readthedocs.io/en/latest/index.html
    '''

    def __init__(self, port=UDP_SSDP_PORT, ttl=2, address=None, iface=None) -> None:
        super().__init__()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(10)

        ttl = struct.pack('b', ttl) #pack the Time To Live to bytes
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

        self._address = (UDP_MCAST_ADDR, port)
        if address is not None:
            self.sock.bind((address, 0))
        if iface is not None:
            self.sock.setsockopt(socket.SOL_SOCKET, SO_BINDTODEVICE, iface)
        
    def bsend(self, msg) -> int:
        return self.sock.sendto(msg, self._address)

    def bsendto(self, msg, _addr) -> int:
        return self.sock.sendto(msg, _addr)

    def recv(self):
        try:
            while True:
                data = self.sock.recvfrom(1024)
                yield data
        except socket.timeout:
            pass
        return

class UDPMulticastListener(object):
    def __init__(self, proto='ipv4', port=1900, address=None) -> None:
        super().__init__()

        self.stopped = False

        if proto not in ('ipv4', 'ipv6'):
            raise ValueError("Invalid proto - expected one of {}".format(('ipv4', 'ipv6')))

        if proto == 'ipv4':
            self._af_type = socket.AF_INET
            self._broadcast_ip = IPV4_MCAST_IP
            self._address = (self._broadcast_ip, port)
            bind_address = "0.0.0.0"
        elif proto == "ipv6":
            self._af_type = socket.AF_INET6
            self._broadcast_ip = IPV6_MCAST_IP
            self._address = (self._broadcast_ip, port, 0, 0)
            bind_address = "::"

        self.sock = socket.socket(self._af_type, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if proto == 'ipv4':
            mreq = socket.inet_aton(self._broadcast_ip)
            if address is not None:
                mreq += socket.inet_aton(address)
            else:
                mreq += struct.pack(b"@I", socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq,)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1) 
        elif proto == "ipv6":
            mreq = socket.inet_pton(socket.AF_INET6, self._broadcast_ip)
            mreq += socket.inet_pton(socket.AF_INET6, "::")
            self.sock.setsockopt(
                socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq,
            )
            self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, 1)
        self.sock.bind((bind_address, port))

    def on_recv(self, data, addr):
        pass

    def bsend(self, msg) -> int:
        self.sock.sendto(msg, self._address)

    def listen(self, prn=on_recv):
        try:
            while not self.stopped:
                data, address = self.sock.recvfrom(1024)
                prn(data, address)
        except Exception:
            self.sock.close()
            raise
        finally:
            self.sock.close()