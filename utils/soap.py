from xml.dom.minidom import Document

def soap_header(upnp_schema: str, action: str, schema_group='schemas-upnp-org') -> str:
    return {
        'User-Agent': 'OS/version, UPnP/1.0, MiniUPnPc/1.5',
        'SOAPAction': '"urn:{0}:{1}:1#{2}"'.format(schema_group, upnp_schema, action),
        'Content-Type': 'text/xml',
        'Connection': 'Close',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        }

def soap_body(upnp_schema: str, action: str, arguments=[], schema_group='schemas-upnp-org'):
    doc = Document()

    env = doc.createElementNS('', 's:Envelope')
    env.setAttribute('xmlns:s', 'http://schemas.xmlsoap.org/soap/envelope/')
    env.setAttribute('s:encodingStyle', 'http://schemas.xmlsoap.org/soap/encoding/')

    body = doc.createElementNS('', 's:Body')
    fn = doc.createElementNS('', f'u:{action}')
    fn.setAttribute('xmlns:u', 'urn:{}:service:{}:1'.format(schema_group, upnp_schema))

    a_list = []

    for k, v in arguments:
        tmp = doc.createElement(k)
        tmp_text = doc.createTextNode(v)
        tmp.appendChild(tmp_text)
        a_list.append(tmp)
    
    for a in a_list:
        fn.appendChild(a)

    body.appendChild(fn)
    env.appendChild(body)
    doc.appendChild(env)
    return doc.toxml()

