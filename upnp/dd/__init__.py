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
    contains all related information for a UPnP-device loaded from 
    the xml-file. Second, the 'service' class defines a sevice 
    located and specified by a device. If this service contains a 
    SCPD-URL node, the next file could get important.

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

from .devicedesc import (
    scpd,
    service,
    device,
    generate_code
)
