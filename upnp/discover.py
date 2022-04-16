import requests

import upnp
from xml.etree import cElementTree

def get_scpd_url(url, _service) -> str:
    tmp_url = url[7:].split('/')[:-1]
    
    x = _service.get(upnp.dd.devicedesc.SER_SCPD_URL)
    if not x:
        return None
    
    tmp_x = x.split("/")
    for t in tmp_x:
        if len(t) > 0 and t not in tmp_url:
            tmp_url.append(t)

    scpd_url = "http://" + '/'.join(tmp_url)
    return scpd_url

class DCovImpl(upnp.UModule):
    def __init__(self, uid):
        super().__init__(uid, "upnp.lookup.dcov")

    def execute(self, client, db=None, arguments=None):
        if not db:
            raise Exception("(upnp.discover) [ERROR] -c- : argument parsing not implemented")

        data = db.query("msearch")
        devices = []
        for host, url in data['urls']:
            # trying to get response from the resolved urls
            resp = requests.get(url)

            if not resp:
                continue

            xml_desc = cElementTree.fromstring(resp.text)
            xml_dev = upnp.device(xml_desc)
            if 'deviceList' in xml_dev:
                __add_dev__(xml_dev, devices, url, host)
            devices.append((url, xml_dev, host))

        if len(devices) == 0:
            print("(upnp.discover) [ERROR] -c- : no device specified")

        full_desc = []
        for url, device_desc, host in devices:
            serv_list = device_desc.get(upnp.dd.devicedesc.NODE_SERVICE_LIST)
            

            if not serv_list:
                serv_list = []

            for _service in serv_list:
                s = upnp.uobject("service", (url, _service))
                d = upnp.uobject("device", (host, device_desc))
                
                scpd__url = get_scpd_url(url, _service)
                for scpd__url0 in upnp.url_fuzz(scpd__url):    
                    if not scpd__url0:
                        sc = upnp.uobject("scpd", (scpd__url0, {}))
                        full_desc.append((d, s, sc))
                    else:
                        scpd__xml = scpd__url0[1]

                        _scpd = upnp.scpd(cElementTree.fromstring(scpd__xml))
                        sc = upnp.uobject("scpd", (scpd__url0[0], _scpd))
                        full_desc.append((d, s, sc))

        obj = upnp.uobject("dcov", full_desc)
        db.pack(obj)

def __add_dev__(xml_dev, devices, url, host):
    if 'deviceList' in xml_dev:
        for __device in xml_dev['deviceList']:
            if 'deviceList' in xml_dev:
                __add_dev__(__device, devices, url, host)
            else:
                devices.append((url, __device, host))
