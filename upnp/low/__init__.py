__doc__ = """
    -------------------- UTILS - Module --------------------
    There are three files containing useful and important 
    classes and funtions/methods. A brief explaination of 
    every file follows:

    [UDP.py]:
    This file contains an imlpementation of a udp-client 
    sending and receiving messages from the udp-broadcast.
    A useful and more detailed documentation on how this 
    client work can be found at ssdpy.readthedocs.io. Here
    the client only implements the send() and receive()
    function.

    [ssdp.py]:
    In this file multiple constants of UPnP-SSDP messages
    are defined and a class to represent the Header of 
    those packages and a class to load all data from such
    a SSDP-Packet. Furthermore, there are standard-imple-
    mentations for sending SSDP-MSEARCH and SSDP-USEARCH
    packets (USEARCH is almost equal to MSEARCH). In 
    order to get an url for a specific device, the locate
    method is recommended.

    [upnpid]:
    As defined in the UPnP-Device-Architecture, the uuid
    used to identify devices is generated through a spe-
    cific algorithm. One simple version is implemented 
    in this file.

    [References]:
    | https://ssdpy.readthedocs.io/en/latest/index.html
    | UPnP-arch-DeviceArchitecture-v2.0
"""

from .UDP import (
    UDPMulticastClient, UDPMulticastListener
)

from .ssdp import (
    searchpayload,
    notifypayload,
    msearch,
    notify,
    SSDPHeader,
    SSDPPacket
)

from .soap import (
    soap_body,
    soap_header
)

from .fuzzer import (
    url_fuzz
)

from .hostaddress import (
    pprint_info
)
