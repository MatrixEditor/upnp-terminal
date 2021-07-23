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

# define UDP_MCAST
UDP_MCAST_ADDR = '239.255.255.250'
UDP_SSDP_PORT = 1900

IPV4_MCAST_IP = UDP_MCAST_ADDR
IPV6_MCAST_IP = 'ff02::c'

# error codes defined in UPnP-Architecture v2.0 below
# see page 82
INVALID_ACTION = 401
INVALID_ARGS = 402
DEPRECATED = 403
ACTION_FAILED = 501
ARG_VALUE_INVALID = 600
ARG_VALUE_OUTOFRANGE = 601
NOT_IMPLEMENTED = 602 # Optional Action Not Implemented
OUT_OF_MEMORY = 603
INTERVENTION_REQUIRED = 604
ARG_TOO_LONG = 605
DEV_SECURITY = [606, 612]
COMMON_ACTION_ERRORS = [613, 699]
ACTION_ERRORS = [700, 899]

#errors below
E_ERR_UNKNOWN = 0
E_ERR_NOSERVICE = 1
E_ERR_NOPACKETS = 2
E_ERR_NODEVICES = 3
E_ERR_NOURLS = 4
IO_ERR_NOUTPUT = 5
IO_ERR_DENIED = 6
E_ERR_WEB404 = 7
E_ERR_NOTARGET = 8
E_ERR_MALFORMEDIP = 9
E_ERR_NOSERDESCR = 10
E_ERR_WEBAUTH = 11
E_ERR_MALFORMEDSCPD = 12
E_ERR_NOMETHOD = 13
E_ERR_NOSERVICENAME = 14
E_ERR_MALFORMEDDEV = 15

ERROR_STR = [
    '[!] Unknown error occured.',
    '[!] Warning: No specific UPnP-Service(s) found.',
    '[!] No packets received!',
    '[!] No devices found!',
    '[!] No URL-representations found!',
    '[!] No output-file declared. Session won\'t be saved.',
    '[!] Could not open the output-file!',
    '[!] Website not found: 404',
    '[!] No target specified!',
    '[!] IP-Address malformed! ({0})',
    '[!] No service-descritpion(s) found!',
    '[!] Warning: exception while fetching a website (maybe it requires authorization). url: {}',
    '[!] Malformed service-descritpion loaded!',
    '[!] No method is specified!',
    '[!] Please specify the service-name!',
    '[!] Malformed device description skipped.'
]