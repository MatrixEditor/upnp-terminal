# upnp-terminal

To use this code you have to install python requests and download this repository. With 'py terminal.py' you can start the program.

## dcov

The UPnP-Disocery command searches for the given target device (via ip-address) and extracts all relevant information about it. The syntax is as follows:

> dcov -t/--target TARGET [--st ST] [--print-all] [--scpd] [--url-fuzz] [--on-save]

The *--print-all* argument indicates that every detail that is gathered should be printed and with *--on-save* a folder with several files and information is created in the same directory. If you enable the search for service descriptions (do that with with *--scpd*) it is recommended to also enable url-fuzzing with *--url-fuzz*. To understand why this option should be enabled see code line **185**.

As a result, all possible methods that can be invoked through you are printed and all stored state-variables are given. Possible output (at the end):

    [...]
    Service no.2: (http://<IP-ADDRESS>:8080/RenderingControl/scpd.xml)
        >> Action-list found:
            + GetMute(InstanceID: A_ARG_TYPE_InstanceID, Channel: A_ARG_TYPE_Channel):
                    return [CurrentMute: Mute]

            + GetVolume(InstanceID: A_ARG_TYPE_InstanceID, Channel: A_ARG_TYPE_Channel):
                    return [CurrentVolume: Volume]
    [...]

If you want to know what meaning these values have, refer to code at lines 628 ff.

## ctr

The control command tries to invoke a method given by input at the specified host and prints the result of that action. Syntax:

> ctr -t/--target TARGET_URL -m/--method METHOD_NAME -s/--service SERVICE_NAME [--arg ARGS] [-o/--out PATH]

The result is of type 'xml' and it's recommended to save files in xml-style. The Error-Codes are defined in the *__init__.py* file in the *utils* module and described in UPnP-Device-Architecture V2 on page 82.

## msearch

This command is probably the most useful one among the defined commands because here the network is scanned of possible UPnP-devices and its representation URLs. Syntax:

> msearch [-t/--host TARGET] [-p/--port PORT] [--man MAN] [--st ST] [--mx MX] [-o/--out PATH]

Some of the arguments are described in the *ssdp.py* file, but to get a better understanding refer to the UPnP-Device-Architecture paper. 

Possible output for 'msearch' (only typing command is enough for the system):

    [...]
    Address                 Server-type
    -------                 -----------
    192...                  Linux/3.8.8, UPnP/1.0, Portable SDK for UPnP devices/1.6.19
    192...                  Linux/3.14.43+ UPnP/1.0 GUPnP/1.0.5
    192...                  FOS/1.0 UPnP/1.0 Jupiter/6.5

    [*] Found some URL-representations: amount: 12
    Address                 URL-location
    -------                 ------------
    192...                  http://<IP-ADDRESS>:8080/dd.xml
    [...]

Please do not use the *usearch* command.

## wget

A simple command to fetch and download web-urls (and to save it in a separate file). 
Syntax:

> wget URL [-o/--out PATH]

## upnp-uuid

Just type the command name and get a fully quialified UUID which is used by devices to identify themselves.

## ls

The 'list' command lists all possible methods that can be invooked through the *ctr* command and prints them in a very kind format, so you can copy and invoke them.
Syntax:

> ls -t/--target TARGET_ADDRESS [-s/--service SERVICE_NAME] [-o/--out PATH]

Possible output from 'ls -t 127.0.0.1':

    [...]
    [*] Found some commands:
        (>) ctr -t 127.0.0.1:8091/AVTransport/Control -m GetMediaInfo -s AVTransport --arg InstanceID:VALUE

        (>) ctr -t 127.0.0.1:8091/AVTransport/Control -m GetMediaInfo_Ext -s AVTransport --arg InstanceID:VALUE

        (>) ctr -t 127.0.0.1:8091/AVTransport/Control -m GetTransportInfo -s AVTransport --arg InstanceID:VALUE

        (>) ctr -t 127.0.0.1:8091/AVTransport/Control -m GetPositionInfo -s AVTransport --arg InstanceID:VALUE
    [...]
