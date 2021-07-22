import argparse
import sys
import requests

from utils import ssdp, UDP, soap, upnpid
from utils import *
from description import device, scpd
from description import *
from xml.dom import minidom
from string import whitespace

if sys.platform == 'win32':
    SEP = '\\'
else:
    SEP = '/'

# allowed/implemented commands:
# dcov -t/--target TARGET [--st ST] [--print-all] [--scpd] [--on-save] [--url-fuzz]
# ctr -t/--target TARGET -m/--method METHOD -s/--service SERVICE [--arg ARGS] [--schema SCHEMA]
# msearch [-t/--host TARGET] [-p/--port PORT] [--man MAN] [--st ST] [--mx MX] [-o/--out PATH]
# userach [-t/--host TARGET] [-p/--port PORT] [--man MAN] [--st ST] [-o/--out PATH]
# wget URL [-o/--out PATH]
# upnp-uuid [no arguments after command]
msearch_defaults = {
    'host': UDP_MCAST_ADDR,
    'port': UDP_SSDP_PORT,
    'man': ssdp.SSDP_DISCOVER,
    'st': ssdp.SSDP_ALL,
    'mx': 2
}

# The same as 'msearch_defaults' but without
# the 'mx' value. For explaination please 
# refer to the UPnP-Architecture documentation.
usearch_defaults = {
    'host': UDP_MCAST_ADDR,
    'port': UDP_SSDP_PORT,
    'man': ssdp.SSDP_DISCOVER,
    'st': ssdp.SSDP_ALL
}

# Add your own fancy prompt here
prompt='$:UPnP[system]> '

class UPnPArgumentParser(argparse.ArgumentParser):
    def __init__(self,
                 prog=None,
                 usage=None,
                 description=None,
                 epilog=None,
                 parents=[],
                 formatter_class=argparse.HelpFormatter,
                 prefix_chars='-',
                 fromfile_prefix_chars=None,
                 argument_default=None,
                 conflict_handler='error',
                 add_help=True,
                 allow_abbrev=True) -> None:
        super().__init__(prog=prog, usage=usage, description=description, epilog=epilog, parents=parents, formatter_class=formatter_class, prefix_chars=prefix_chars, fromfile_prefix_chars=fromfile_prefix_chars, argument_default=argument_default, conflict_handler=conflict_handler, add_help=add_help, allow_abbrev=allow_abbrev)

    def exit(self, status=0, message=""):
        if message:
            self._print_message(message, sys.stderr)

argpsr_msearch = UPnPArgumentParser('msearch')
argpsr_usearch = UPnPArgumentParser('usearch')
argpsr_notify = UPnPArgumentParser('notify')
argpsr_dcov = UPnPArgumentParser('dcov')
argpsr_ctr = UPnPArgumentParser('ctr')
argpsr_wget = UPnPArgumentParser('wget')

udp_client = UDP.UDPMulticastClient()

#add_... methods below only to add arguments to the parsers.
def add_msearch_arg():
    msearch_args_group = argpsr_msearch.add_argument_group()
    msearch_args_group.add_argument('-t', '--host', help='The Host address the packet will be sent to.', default=ssdp.UDP_MCAST_ADDR, type=str)
    msearch_args_group.add_argument('-p', '--port', help='The target port.', default=ssdp.UDP_SSDP_PORT)
    msearch_args_group.add_argument('--man', help='Defines the scope (namespace) of the packet.', default=ssdp.SSDP_DISCOVER)
    msearch_args_group.add_argument('--st', help='The search target.', type=str, default=ssdp.SSDP_ALL)
    msearch_args_group.add_argument('--mx', help='The maximum wait time in seconds.', default=2, type=int)
    msearch_args_group.add_argument('-o', '--out', help='The path of a file the result will be written in.')

def add_usearch_arg():
    msearch_args_group = argpsr_usearch.add_argument_group()
    msearch_args_group.add_argument('--host', help='The Host address the packet will be sent to.', default=ssdp.UDP_MCAST_ADDR, type=str)
    msearch_args_group.add_argument('-p', '--port', help='The target port.', default=ssdp.UDP_SSDP_PORT)
    msearch_args_group.add_argument('--man', help='Defines the scope (namespace) of the packet.', default=ssdp.SSDP_DISCOVER)
    argpsr_usearch.add_argument('target', help='The target host address.')
    msearch_args_group.add_argument('--st', help='The search target.', type=str)
    msearch_args_group.add_argument('-o', '--out', help='The path of a file the result will be written in.')

def add_notify_arg():
    argpsr_notify.add_argument('location', help='The host-specific url-location/representation.')
    argpsr_notify.add_argument('server', help='The server-service descrition')
    argpsr_notify.add_argument('uuid', help='The host-id or UUID.')
    
    group = argpsr_notify.add_argument_group()
    group.add_argument('-t', '--host', help='The Host address the packet will be sent to.', default=ssdp.UDP_MCAST_ADDR, type=str)
    group.add_argument('-p', '--port', help='The target port.', default=ssdp.UDP_SSDP_PORT)
    group.add_argument('-c', '--cache', help='Specifies the number of seconds the advertisement is valid.', type=int, default=1800)
    group.add_argument('--nt', help='The notification type.', default='upnp:rootdevice')
    group.add_argument('--nts', help='The notification sub-type.', default=ssdp.SSDP_ALIVE)
    group.add_argument('--usn', help='The unique service name.')

def add_ctr_arg():
    argpsr_ctr.add_argument('-t', '--target', help='The target host ip adress and port separated by ":"', required=True)
    argpsr_ctr.add_argument('-m', '--method', help='The method name.', required=True)
    argpsr_ctr.add_argument('-s', '--service', help='The target service name', required=True)
    argpsr_ctr.add_argument('--arg', help='The args for the requested method. (Syntax: value,value2,...')
    argpsr_ctr.add_argument('-o', '--out', help='The output filename in the same directory.')
    argpsr_ctr.add_argument('--schema', help='The upnp-schema provided by the service.', default='schemas-upnp-org')

def add_wget_arg():
    argpsr_wget.description = '''WGET: A small tool for displaying content of websites. For downloading please use DISCOV.'''
    group = argpsr_wget.add_argument_group()
    group.add_argument('-u', '--url', help='The complete website url.', required=True, type=str)
    group.add_argument('-o', '--out', help='The output file where the content could be saved')

def add_dcov_arg():
    group = argpsr_dcov.add_argument_group()
    group.add_argument('-t', '--target', help='The target host ip-adress.', required=True)
    group.add_argument('--st', help='Specifies the search target in the ssdp-packet.', default=ssdp.SSDP_ALL)
    group.add_argument('--print-all', help='Prints detailed information about the specified target.', action='store_true')
    group.add_argument('--on-save', help='Specifies a folder where output should be saved.', action='store_true')
    # maybe path could be added here
    group.add_argument('--scpd', help='Tries to resolve all service descriptions in detail.', action='store_true')
    group.add_argument('--url-fuzz', help='Tries URL-Fuzzing if code 404 is delivered.', action='store_true')

def get_msearch_args():
    n = argparse.Namespace()
    for d in msearch_defaults:
        n.__setattr__(d, msearch_defaults[d])
    return n

def get_usearch_args():
    n = argparse.Namespace()
    for x in usearch_defaults:
        n.__setattr__(x, usearch_defaults[x])
    return n    

# logs an error message (for error codes see 
# __init__.py file) in utils module
def error(msg: int, linebreak=False, args=None):
    if msg and 0 <= msg < len(ERROR_STR):
        if not args:
            print('%s%s' % (ERROR_STR[msg], '\n' if linebreak else ""))
        else:
            print('%s%s' % (ERROR_STR[msg].format(args), '\n' if linebreak else ""))
    else:
        print('%s%s' % (ERROR_STR[E_ERR_UNKNOWN], '\n' if linebreak else ""))

# parses the input from terminal
def let_parse(parser: argparse.ArgumentParser, line) -> argparse.Namespace:
    return parser.parse_args(args=line)

# validates an ip-address by checking the given string
def validate(ip: str):
    try:
        s = ip.split('.')
        if len(s) == 4:
            nums = [int(i) for i in s]
            for n in nums:
                if n > 255 or n < 0:
                    return False
            return True
        else:
            return False
    except:
        return False

def __msearch__(args):
    print("\nMULTICAST-Search with SSDP-packets v0.3.2")
    print("[*] Starting to receive packets (usually takes up to 10sec).")
    
    _host = args.host
    _port = args.port
    _man = args.man
    _st = args.st
    _mx = args.mx

    packets = []; a = []; urls = []
    for raw_data in ssdp.msearch(udp_client, _host, _port, _st, _man, _mx):
        addr = raw_data[1]
        p = ssdp.SSDPPacket(bytes.decode(raw_data[0]), addr[0], addr[1])

        def isknown(address) -> bool:
            for x in a:
                if address[0] == x[0]:
                    return True
            return False

        def islocated(location) -> bool:
            for x in urls:
                if x[1].__eq__(location):
                    return True
            return False

        if not isknown(addr):
            ser = p.get(ssdp.NOTIFY_SERVER)
            if ser:
                a.append((addr[0], ser))
            else:
                a.append((addr[0], ERROR_STR[E_ERR_NOSERVICE]))
        if p.get(ssdp.NOTIFY_LOCATION):
            loc = p.get(ssdp.NOTIFY_LOCATION)
            if loc and not islocated(loc):
                urls.append([addr[0], loc])

        packets.append(p)
    if len(packets) == 0:
        error(E_ERR_NOPACKETS, True)
        return
    print('\n[*] Successfully collected packets: amount: %d' % (len(packets)))

    amount = len(a)
    if amount > 0:
        print("[*] Found some UPnP-Devices: amount: %s" % (amount))
        print("Address        \t\tServer-type\n" + '-'*7 + '\t\t\t' + '-'*11)
        for address in a:
            print('\t\t'.join(address))
    else:
        error(E_ERR_NODEVICES)
    
    print()
    if len(urls) > 0:
        print("[*] Found some URL-representations: amount: %s" % (len(urls)))
        urls.sort()
        print("Address        \t\tURL-location\n%s\t\t\t%s" % ('-'*7, '-'*12))
        for url in urls:
            print('\t\t'.join(url))
    else:
        error(E_ERR_NOURLS)

    try:
        if not args.out:
            return
    except:
        error(IO_ERR_NOUTPUT)
        return

    try:
        import string
        if args.out[0] in string.whitespace:
            args.out = args.out[1:]
        f = open(args.out, 'w')
        f.write("Result of command msearch:\n\n")

        if len(a) > 0:
            f.write("Address        \t\tServer-type\n")
            for address in a:
                f.write('\t\t'.join(address) + "\n")
        if len(urls) > 0:
            f.write("\nAddress        \t\tURL-location\n")
            for u in urls:
                f.write('\t\t'.join(u) + "\n")
        f.write("\nCaptured Packets: (Warning of too much lines)\n")
        for p in packets:
            f.write('%s\n\n' % (p.__str__()))
        f.close()
        print("\n[*] Successfully saved to file.")
    except Exception as e:
        error(IO_ERR_DENIED)

def __usearch__(args):
    print("UNICAST-Search with SSDP-packets v0.3.2")
    print("[*] Making a unicast-search packet. It could take up to 10 sec.")

    _host = args.host
    _port = args.port
    _man = args.man
    _st = args.st
    _target = args.target

    packets = []; urls = []
    for raw_data in ssdp.usearch(udp_client, _host, _port, _man, _st):
        addr = raw_data[1]
        if addr[0] == _target:
            p = ssdp.SSDPPacket(bytes.decode(raw_data[0]), addr[0], addr[1])
            packets.append(p)

            loc = p.get(ssdp.NOTIFY_LOCATION)
            if loc and loc not in urls:
                urls.append(p.get(ssdp.NOTIFY_LOCATION))
    
    if len(packets) == 0:
        error(E_ERR_NOPACKETS, True)
        return

    print('\n[*] Successfully collected packets: amount: %d' % (len(packets)))
    if len(urls) > 0:
        print("[*] Found some URL-representations: amount: %s" % (len(urls)))
        urls.sort()
        print("Address        \tURL-location")
    else:
        error(E_ERR_NOURLS)

    try:
        if not args.out:
            return
    except ValueError:
        error(IO_ERR_NOUTPUT)
        return

    try:
        f = open(args.out, 'w')
        f.write("Result of command usearch:\n\n")

        if len(urls) > 0:
            f.write("Address        \tURL-location")
            for u in urls:
                f.write('%s\n' % (u))
        f.write("\nCaptured Packets:\n")
        for p in packets:
            f.write('%s\n' % (p.__str__()))
        f.close()
        print("[*] Successfully saved to file.\n")
    except:
        error(IO_ERR_DENIED)

def __dcov__(args):
    print("\nStarting UPnP-Discovery on host: %s" % (args.target))

    if not args.target:
        error(E_ERR_NOTARGET, True)
        return

    _target: str = args.target
    # in some test cases there was a whitespace in front
    # of the target-url: ' 127.0.0.1'. So its better to
    # check if there is any whitespace at the beginning  
    if _target[0] in whitespace:
        _target = _target[1:]
    # look at the validate-method for details
    if not validate(_target):
        error(E_ERR_MALFORMEDIP, True, args=[_target])
    
    # standard values for fields:
    # st: ssdp:all
    # print_all: false
    # scpd: false 
    _st = args.st 
    _print_all = args.print_all
    _scpd = args.scpd

    packets = []; urls = []
    def islocated(location) -> bool:
        for x in urls:
            if x.__eq__(location):
                return True
        return False

    print("[*] Collecting packets...")
    # selecting all packets with the target address as source
    # address and tries to resolve any url-location
    for data, addr in ssdp.msearch(udp_client, st=_st):
        # addr[0] = packet.host_address
        # addr[1] = packet.port
        if addr[0] == _target:
            p = ssdp.SSDPPacket(bytes.decode(data, 'utf-8'), addr[0], addr[1])
            packets.append(p)
            # the 'get' methods prevents throwing an error if
            # field isn't stored in that object
            loc = p.get(ssdp.NOTIFY_LOCATION)

            if loc and not islocated(loc):
                urls.append(loc)
            
    del data
    # if no packets are received or no urls are resolved, end process
    if len(packets) == 0:
        error(E_ERR_NOPACKETS, True)
        return
    else:
        print("\n[*] Collected some packets: amount: %d" % (len(packets)))

    if len(urls) == 0:
        error(E_ERR_NOURLS, True)
        return
    else:
        print("[*] Collected some URLs: amount: %d" % (len(urls)))
    
    print("[*] Found some URL-locations: amount: %d" % (len(urls)))
    print("Address\t\t\tURL-location\n%s\t\t\t%s" % ('-'*7, '-'*12))
    devices = []
    for url in urls:
        # trying to get response from the resolved urls
        print('%s\t\t%s' % (_target, url))
        page = requests.get(url=url)
        if not page:
            continue
        try:
            xml = device.toxml(page.text)
            # adding the url to the tuple for following operations
            devices.append((device.device(xml), url))
        except Exception as e:
            print("[!] Error while parsing device. (%s)" % (e))

    if len(devices) == 0:
        error(E_ERR_NODEVICES)
        return

    print("\n[*] Found some embedded devices: amount: %d" % (len(devices)))
    stats = dict()
    services = []
    # this method adds a stat/node from a device to the stats-dictionary
    def dev_add(node: str, dev: device.device):
        if node in stats:
            if not stats[node]:
                stats[node] = [dev.get(node)]
            else:
                if dev.get(node) not in stats[node]:
                    stats[node].append(dev.get(node))
        else:
            stats.setdefault(node, [dev.get(node)])
    # Iterationg through all devices found and adds the nodes given below 
    # to the stats-dictionary. The following nodes are also stored but not
    # accessed in this code:
    #   - DEV_DEVICE_TYPE
    #   - DEV_MODEL_NUMBER
    #   - DEV_UDN
    #   - NODE_ICON_LIST (no implementation yet)  
    for d in devices:
        nodes = [DEV_FRIENDLY_NAME, DEV_MANUFACTURER, DEV_MODEL_DESCRIPTION,
                  DEV_MODEL_NAME, DEV_PRESENTATION_URL]
        if _print_all:
            for i in [DEV_MANUFACTURER_URL, NODE_SPEC_VERSION]:
                nodes.append(i)

        for n in nodes:
            dev_add(n, d[0])
        
        if d[0].get(NODE_SERVICE_LIST):
            for s in d[0].get(NODE_SERVICE_LIST):
                services.append((s, d[1]))
        else:
            print("no service list")

    print("Node\t\t\tValue(s)\n%s\t\t\t%s" % ('-'*4, '-'*8))
    for s in stats:
        print('\t\t'.join([s, str(stats[s])]))

    scpdurls = []
    if len(services) == 0:
        error(E_ERR_NOSERVICE)
        return
    else:
        print("\n[*] Found some services: amount: %d" % (len(services)))
        for s in services:
            ser = s[0]
            base = s[1]
            #removing the last '/' if present
            if base[len(base) - 1] == '/':
                base = base[:-1]
            else:
                # else split everything after 'http://' and 
                # remove the last element (if this element
                # contains a '.')
                e = base[7:].split('/')
                if '.' in e[len(e) - 1]: 
                    base = 'http://%s' % ('/'.join(e[:-1]))

            # formatting the scpd-url:
            # if the node-value of this url doesn't contain
            # a '/' at beginning, this has to be added
            a = ser.get(SER_SCPD_URL)
            if a:
                scpdurl = '%s%s' % (base, a if a[0] == '/' else '/%s' % (a))
                print("[+] type: %s -> scpdURL: %s" % (ser.get(SER_SERVICE_TYPE), scpdurl))
                if scpdurl not in scpdurls:
                    scpdurls.append(scpdurl)
    
    scpds = []
    # This option tries to resolve the service-descriptions and its inbound actions
    # and state-variables. First the resolved urls are proved (read below for code
    # explaination). Next the scpd-object is created (see scpd-class for details) 
    # and last but not least the services found are printed reading-friendly. 
    if _scpd:
        if len(scpdurls) == 0:
            error(E_ERR_NOSERDESCR)
        else:
            print("\n[*] Option 'scpd': loading all service-descriptions")
            print("Status\t\tURL\n%s\t\t%s" % ('-'*6, '-'*3))
            for surl in scpdurls:
                try:
                    # fetching the website, either '.xml', '.cgi' files
                    # or other stuff
                    page = requests.get(surl)
                except:
                    error(E_ERR_WEBAUTH, args=[surl + ':' + str(page.status_code)])
                else:
                    print('%s\t\t%s' % (page.status_code, surl))
                    if str(page.status_code) == '404':
                        if args.url_fuzz:
                            # if a description-page is not located at for example at
                            # http://xx/path_node/description.xml when the base
                            # url is http://xx/path_node/main.xml, then more tries
                            # are made by this code below by taking each additional
                            # path_node away and make a http-request.
                            def fetch_recursive(x):
                                # 'X' is the url without the 'http' tag
                                b = x

                                # first, check if there is a file located in 
                                # the url-path
                                if '.' in b[len(b) - 1]: 
                                    # Then check if there are any path_nodes left . 
                                    # Base length is [address, path_node, file] if
                                    # another request could be made.
                                    if len(b) >= 3:
                                        b[len(b) - 2] = b[len(b) - 1]
                                        b = b[:-1]
                                    else:
                                        # returns None if there isn't any url 
                                        # that can be checked
                                        return None
                                else:
                                    # In this case a '/' is at the end of the url:
                                    # parts: [address, path_node, '']
                                    if len(b) >= 3:
                                        if '' == b[len(b) - 1]:
                                            b = b[:-2]
                                        else:
                                            b[len(b) - 2] = b[len(b) - 1]
                                            b = b[:-1]
                                    else:
                                        return None
                                try:
                                    # make the full request by adding the 'http'
                                    # tag at the beginning
                                    c = 'http://%s' % ('/'.join(b))
                                    p = requests.get(c)
                                except:
                                    return (c, None)
                                else:
                                    # The status code has to 200 or something
                                    # else, but never 404
                                    print('   \t\t[%s -> %s]' % (p.status_code, c))
                                    if p.status_code == 404:
                                        return (c, None)
                                    else:
                                        # if everything went well, the page-text is
                                        # delivered as string
                                        return (c, p.text)

                            # the function below generates all possible urls with
                            # swapping the 'path_nodes' in a given url. 
                            def make_lists(x):
                                # the address and target shouldn't be affected
                                t = x[0]; h = x[len(x) - 1]
                                x = x[1:-1]; z = []
                                if len(x) > 0:
                                    for i in range(0, len(x)):
                                        head = x[i]
                                        r = [head]
                                        for i in range(0, len(x)):
                                            tail = x[i]
                                            if head != tail:
                                                r.append(tail)
                                        c = 'http://%s/%s/%s' % (t, '/'.join(r), h)
                                        if c not in z:
                                            z.append(c)
                                return z
                                    
                            # The real recursive funtion is defined below:
                            # with this code, only services with a positive
                            # url-fetching result are added  
                            def run_rec(x):
                                a = x
                                while True:
                                    d = fetch_recursive(a.split('/'))
                                    if not d:
                                        break
                                    else:
                                        if not d[1]:
                                            # removing the 'http://'-tag
                                            a = d[0][7:]
                                        else:
                                            try:
                                                s = scpd.scpd(device.toxml(d[1]))
                                                scpds.append((s, d[0]))
                                            except:
                                                error(E_ERR_MALFORMEDSCPD)
                                            break
                        
                            a = surl[7:]
                            _urls = make_lists(a.split('/'))
                            for u in _urls:
                                # prevent errors
                                if len(u) != 0:
                                    run_rec(u[7:])
                        else:
                            error(E_ERR_WEB404)
                    else:
                        try:
                            # parsing the xml-document in the scpd-class
                            # and adding it with its url
                            s = scpd.scpd(device.toxml(page.text))
                            scpds.append((s, surl))
                        except:
                            error(E_ERR_MALFORMEDSCPD)

            # We can only print some services if there are some
            if len(scpds) == 0:
                error(E_ERR_NOSERDESCR)
            else:
                # A simple formatting function for printing the methods provided 
                # through a scpd-file. Don't look at the code just look at the 
                # printed result.
                # Format:
                #   [indent] + method_name(param1: type, param2: type):
                #   [indent*2]    return [value1: type, value3: type]
                def format_action(_a: scpd.Action, indent='\t\t'):
                    if _a:
                        param = []
                        out = []
                        if not _a.get(NODE_ARGUMENT_LIST):
                            print('%s+ %s():\n%sreturn None' % (indent, _a.get(NODE_NAME), indent*2))
                        else:
                            for arg in _a.get(NODE_ARGUMENT_LIST):
                                d = arg.get(NODE_DIRECTION) 
                                if d == 'in':
                                    var = ""
                                    if arg.get(NODE_RELATED_VARIABLE):
                                        var = ': ' + arg.get(NODE_RELATED_VARIABLE)
                                    param.append('%s%s' % (arg.get(NODE_NAME), var))
                                else: #'out'
                                    var = ""
                                    if arg.get(NODE_RELATED_VARIABLE):
                                        var = ': ' + arg.get(NODE_RELATED_VARIABLE)
                                    out.append('%s%s' % (arg.get(NODE_NAME), var))
                            
                            param = param if len(param) <= 3 else [param[0], param[1], '...']
                            out = out if len(out) <= 3 else [out[0], out[1], '...'] 
                            if len(out) == 0:
                                out = ['None']

                            if len(out) > 1:
                                print('%s+ %s(%s):\n%sreturn %s' % (indent, _a.get(NODE_NAME), ', '.join(param), indent*2, out[0]))
                            else:
                                print('%s+ %s(%s):\n%sreturn [%s]' % (indent, _a.get(NODE_NAME), ', '.join(param), indent*2, ', '.join(out)))

                # A simple formatter for printing the state-variables in 
                # following syntax:
                #   [indent] + name: value [(default=X)]
                def format_var(_v, indent='\t\t'):
                    try:
                        d = _v[NODE_DEFAULT_VALUE]
                    except:
                        print('%s+ %s: %s' % (indent, _v[NODE_NAME], _v[NODE_DATA_TYPE]))
                    else:
                        print('%s+ %s: %s (default=%s)' % (indent, _v[NODE_NAME], _v[NODE_DATA_TYPE], d))

                print("\n[*] Found some service descriptions: amount: %d" % (len(scpds)))
                # The enumeration was implemented at some earlier testing,
                # just ignore that. 
                for i, sc in enumerate(scpds):
                    s = sc[0]
                    print('Service no.%d: (%s)' % (i, sc[1]))
                    if not s.get(NODE_ACTION_LIST):
                        print("    >> No action list")
                    else:
                        al = s.get(NODE_ACTION_LIST)
                        print("    >> Action-list found:")
                        for a in al:
                            # 'a' is of type action
                            format_action(a, indent=' '*8)
                            print()
                    if not s.get(NODE_STATE_TABLE):
                        print("    >> No state-variables")
                    else:
                        _vars = s.get(NODE_STATE_TABLE)
                        print("    >> State-variables found: (printing all when option is enabled)")
                        if _print_all:
                            for v in _vars:
                                format_var(v, indent=' '*8)
                    print()
                    # The code below will print the SpecVersion node:
                    # for x in s:
                    #     if x not in [NODE_STATE_TABLE, NODE_ACTION_LIST]:
                    #         print("    > %s: %s" % (x, sc[x]))
                    # print()

    _on_save = args.on_save
    if _on_save:
        print("\n[*] Starting to save content on same directory...")

        import os, datetime
        import xml.dom.minidom as md
        curr_dir = os.getcwd()

        now = datetime.datetime.now()
        curr_dir += SEP + _target + '-dcov_saving.' + now.strftime('%d-%m-%Y.%H%M%S')
        os.mkdir(curr_dir)

        # saving scpd-files and descr-files in different directories.
        # So, e.g. .\base\scpd\ and .\base\dscr\
        scpd_dir = curr_dir + SEP + 'scpd'
        dscr_dir = curr_dir + SEP + 'dscr'
        os.mkdir(scpd_dir)
        os.mkdir(dscr_dir)
        os.mkdir(dscr_dir + SEP + 'web')

        def save_xml(url: str, path_base: str):
            try:
                page = requests.get(url=url)
                if page:
                    # There are some places where the url ends with '/',
                    # therefore the second last element should be used
                    # for a filename
                    a = url.split('/')
                    b = ''
                    if len(a[-1]) <= 1:
                        b = a[-2]
                    else:
                        b = a[-1]
                    name = ''.join([path_base, SEP, b])
                    # parsing the page.text with the minidom-parser,
                    # because it supports .toxml() and .toprettyxml()
                    # afterwards
                    doc = md.parseString(page.text)
                    f = open(name, 'w')
                    f.write(doc.toxml())
                    f.close()
            except Exception as e:
                print(str(e))       

        for u in urls:
            save_xml(u, dscr_dir + SEP + 'web')

        #saving the packets, services
        p_file = ''.join([dscr_dir, SEP, 'packets.txt'])
        s_file = ''.join([scpd_dir, SEP, 'services.txt'])
        
        f = open(p_file, 'w')
        for p in packets:
            f.write('%s\n\n' % (p.__str__()))
        f.close()
        f = open(s_file, 'w')
        for s in services:
            f.write('%s\n%s\n\n' % (s[0].__str__(), s[1]))

        #saving scpd's in sub-directories
        for sc, u in scpds:
            name = ''.join([scpd_dir, SEP, u.split('/')[-1]])
            f = open(name + '.txt', 'w')
            f.write('URL: %s\n%s\n' % (u, sc.__str__()))
            f.close()
        
        print("[*] Saving completed!")

def __ctr__(args):
    print("\nStarting UPnP-Control on host: %s" %  (args.target))
    if not args.target:
        error(E_ERR_NOTARGET, True)
        return
    
    _target = args.target
    _method = args.method
    _service = args.service
    _arg = args.arg
    _sch = args.schema

    if not _method:
        error(E_ERR_NOMETHOD, True)
        return
    if not _service:
        error(E_ERR_NOSERVICENAME, True)
        return

    if not _arg:
        _arg = []
    else:
        _arg = [(x.split(':')[0], x.split(':')[1]) for x in _arg.split(',')]

    body_set = soap.soap_body(upnp_schema=_service, action=_method, arguments=_arg, schema_group=_sch)
    header_set = soap.soap_header(_service, _method, _sch)

    print("[*] Working with: %s" % ('http://%s' % (_target)))
    print("[*] Header: %s" % (str(header_set)))

    page = requests.post(url='http://%s' % (_target), headers=header_set, data=body_set)
    try:
        doc = minidom.parseString(page.text)
        print('[*] Response:\n\n%s\n' % (doc.toxml()))
    except:
        error(E_ERR_WEBAUTH, True)

def __wget__(args):
    if not args.url:
        return
    print("\n[*] Working with: '%s'" % (args.url))
    page = requests.get(args.url.replace(' ', ""))

    if not page:
        error(E_ERR_WEB404)
        return

    for k in page.headers:
        print(': '.join([k, page.headers[k]]))

    print('\n%s' % (page.text))
    try:
        if not args.out:
            return
    except:
        error(IO_ERR_NOUTPUT)
        return
    
    try:
        f = open(args.out, 'w')
        f.write(page.text)
        f.close()
        print("\n[*] Successfully saved to file.")
    except:
        error(IO_ERR_DENIED)

def __upnpid__():
    print("\nUPnP-UUID Generator v0.0.0.0.0.1")
    print("[*] UUID: %s" % (upnpid.uuid()))

#TODO
def __auto_search__(args):
    pass

# don't look at the code below here
def _react(line: str):
    if line[0] == 'msearch':
        if len(line) == 1:
            __msearch__(get_msearch_args())
        else:
            args = let_parse(argpsr_msearch, line[1:])
            if line[1] != '-h':
                __msearch__(args=args)
    elif line[0] == 'usearch':
        if len(line) == 0:
            __usearch__(get_usearch_args())
        else:
            if line[1] != '-h':
                args = let_parse(argpsr_usearch, line[1:])
                __usearch__(args=args)
            else:
                let_parse(argpsr_usearch, ['-h'])
    elif line[0] == 'notify':
        args = let_parse(argpsr_notify, line[1:])
    elif line[0] == 'dcov':
        if line[1] == '-h':
            let_parse(argpsr_dcov, ['-h'])
        else:
            args = let_parse(argpsr_dcov, line[1:])
            __dcov__(args)
    elif line[0] == 'ctr':
        if line[1] == '-h':
            let_parse(argpsr_ctr, ['-h'])
        else:
            args = let_parse(argpsr_ctr, line[1:])
            __ctr__(args)
    elif line[0] == 'upnp-uuid':
        __upnpid__()
    elif line[0] == 'exit':
        exit(0)
    elif line[0] == 'wget':
        if line[1] != '-h':
            args = let_parse(argpsr_wget, line[1:])
            __wget__(args=args)
        else:
            let_parse(argpsr_wget, ['-h'])

if __name__ == '__main__':
    # adding the arguments to the parsers when calling
    # those methods
    add_ctr_arg(); add_dcov_arg(); add_msearch_arg()
    add_notify_arg(); add_usearch_arg()
    add_wget_arg()
    print()

    while True:
        # define your own prompt if you want your own one
        # see line 42
        next = input(prompt)

        if not next:
            continue
        
        _react(next.split(' '))
        print()