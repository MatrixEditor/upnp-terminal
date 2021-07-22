__doc__ = """
    -------------------- Description - Module --------------------

    When the control point receives information about a device for 
    instance through the multicast-search, it downloads a webpage 
    linked in the LOCATION-section. Within the HTTP-GET request to 
    the device the control point receives more detailed information 
    about the UPnP-device. 
    Now the control point searches for services provided by the 
    device and tries to send HTTP-GET requests to the specified 
    service-URLs.

    [device.py]:
    Here, two main classes are important. First, the 'device' class
    contains al related information for a UPnP-device loaded from 
    the xml-file. Second, the 'service' class defines a sevice 
    located and specified by a device. If this service contains a 
    SCPD-URL node, the next file could get important.

    [scpd.py]:
    The service-description file can be obtained through an url with
    a HTTP-GET request. This file has to be structured in Xml-style
    as defined in UPnP-DeviceArchitecture. In order to move to the 
    next step in UPnP-communication, there are actions described in
    this file. StateVariables are like constants with a value range
    that can be obtained. For more information related to the service
    description, please refer to the UPnP-arch-DeviceArchitecture-
    v2.0.

    [References]:
    | UPnP-arch-DeviceArchitecture-v2.0.pdf
"""

#region device
NODE_ROOT = 'root' 
NODE_SPEC_VERSION = 'specVersion'
NODE_DEVICE = 'device'
NODE_ICON_LIST = 'iconList'
NODE_DEVICE_LIST = 'deviceList'
NODE_SERVICE_LIST = 'serviceList'

# the node-names of a device description below
DEV_DEVICE_TYPE = 'deviceType'
DEV_FRIENDLY_NAME = 'friendlyName'
DEV_MANUFACTURER = 'manufacturer'
DEV_MANUFACTURER_URL = 'manufacturerURL'
DEV_MODEL_DESCRIPTION = 'modelDescription'
DEV_MODEL_NAME = 'modelName'
DEV_MODEL_NUMBER = 'modelNumber'
DEV_MODEL_URL = 'modelURL'
DEV_UDN = 'UDN'
DEV_PRESENTATION_URL = 'presentationURL'

# the node-names of a service description in a 
# device description file
SER_SERVICE_TYPE = 'serviceType'
SER_SERVICE_ID = 'serviceID'
SER_CONTROL_URL = 'controlURL'
SER_EVENT_SUB_URL = 'eventSubURL'
SER_SCPD_URL = 'SCPDURL'

# region scpd
NODE_ACTION_LIST = 'actionList'
NODE_STATE_TABLE = 'serviceStateTable'
NODE_STATE_VAR = 'stateVariable'
NODE_DEFAULT_TYPE = 'defaultType'
NODE_DEFAULT_VALUE = 'defaultValue'
NODE_DATA_TYPE = 'dataType'
NODE_ALLOWED_LIST = 'allowedList'
NODE_ALLOWED_RANGE = 'allowedValueRange'
NODE_STEP = 'step'
NODE_MIN = 'minimum'
NODE_MAX = 'max'
NODE_NAME = 'name'

NODE_ARGUMENT_LIST = 'argumentList'
NODE_DIRECTION = 'direction'
NODE_RELATED_VARIABLE = 'relatedStateVariable'

class XmlParser(dict):
    def __init__(self, child) -> None:
        super().__init__()

        if child:
            # the .iter() method throws an error on my machine
            for item in child.getchildren():
                self.parse_item(item=item)

    #implementation in sub-classes (device, service, action, scpd)
    def parse_item(self, item):
        pass

    def get(self, key: str):
        try:
            return self[key]
        except:
            return None

def getname(child: str) -> str:
    """
    Sometimes the xml-parser puts an extra attribute in the
    tag of an Element (also named namespace). This methods removes 
    this unnessessary string.
    """
    try:
        return child[child.index("}") + 1 :]
    except ValueError:
        return child