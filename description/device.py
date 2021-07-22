from xml.etree import cElementTree as etree
from xml.etree.ElementTree import Element
from description import *

def toxml(page: str) -> Element:
    if page:
        return etree.fromstring(page)

class service(XmlParser):
    def parse_item(self, item: Element):
        name = getname(item.tag)
        self.setdefault(name, item.text)

    def __str__(self) -> str:
        i = self.get(SER_SERVICE_ID)
        s = '[>] %s:\n' % (i if i else 'SERVICE (ID unknown)')
        for x in self:
            s += '\t| %s: %s\n' % (x, self[x])
        return s

class device(XmlParser):
    def parse_item(self, item):
        name = getname(item.tag)
        
        if name == NODE_SPEC_VERSION:
            self.setdefault(name, [item[0].text, item[1].text])
        elif name in [NODE_ICON_LIST]:
            self.parseList(item=item)
        elif name == NODE_DEVICE_LIST:
            devices = []
            for d in item.getchildren():
                devices.append(device(d))
            self.setdefault(name, devices)
        elif name == NODE_DEVICE:
            for ch in item.getchildren():
                self.parse_item(ch)
        elif name == NODE_SERVICE_LIST:
            services = []
            for ch in item.getchildren():
                s = service(ch)
                services.append(s)
            self.setdefault(name, services)
        else:
            self.setdefault(name, item.text)

    def parseList(self, item: Element):
        #print("[!] Found an icon-list: implementation needed! (device-class)\n")
        pass
