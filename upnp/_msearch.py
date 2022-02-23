import upnp


class MSearchImpl(upnp.UModule):
  def __init__(self, uid) -> None:
    super().__init__(uid, "upnp.lookup.msearch")

  def execute(self, client, db=None, arguments=None):
    # argument parsing is not implemented yet

    packets, urls, hosts = self.collect(client)
    if len(packets) == 0:
      print("(upnp.msearch._msearch) [WARNING] -c- : no packets received")
    else:
      print('\n[*] Successfully collected packets: amount: %d' % (len(packets)))

    amount = len(hosts)
    if amount > 0:
      print("[*] Found some UPnP-Devices: amount: %s" % amount)
      # print("Address        \t\tServer-type\n" + '-' * 7 + '\t\t\t' + '-' * 11)
      # for address in hosts:
      # print('\t\t'.join(address))
    else:
      print("(upnp.msearch._msearch) [WARNING] -c- : no services found")

    if len(urls) > 0:
      print("[*] Found some URL-representations: amount: %s" % (len(urls)))
      # urls.sort()
      # print("Address        \t\tURL-location\n%s\t\t\t%s" % ('-' * 7, '-' * 12))
      # for url in urls:
      # print('\t\t'.join(url))
    else:
      print("(upnp.msearch._msearch) [WARNING] -c- : no urls found")

    if not db:
      return None

    obj = upnp.uobject("msearch", {"packets": packets, "urls": urls, "hosts": hosts})
    db.pack(obj)

  def collect(self, cl) -> tuple:
    packets = []
    urls = []
    hosts = []

    for raw_bytes in upnp.msearch(client=cl):
      socket_address = raw_bytes[1]
      packet = upnp.SSDPPacket(bytes.decode(raw_bytes[0]), socket_address[0], socket_address[1])
      location = packet.get(upnp.low.ssdp.NOTIFY_LOCATION)
      serv = packet.get(upnp.low.ssdp.NOTIFY_SERVER)

      if location and not upnp.__is_located__(location, urls, lambda x, y: y[1].__eq__(x)):
        urls.append((socket_address[0], location))

      if not upnp.__is_located__(socket_address, hosts, lambda x, y: x[0] == y[0]):
        if not serv:
          serv = '[!] Warning: No specific UPnP-Service(s) found.'
        hosts.append((socket_address[0], serv))

      packets.append(packet)
    return packets, urls, hosts
