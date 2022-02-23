from random import choice

HEX_DIGIT = '0123456789abcdefABCDEF'

def hexoctet() -> str:
    return '%s%s' % (choice(HEX_DIGIT), choice(HEX_DIGIT))

def hexoctets(amount: int) -> str:
    r = ""
    for i in range(amount):
        r = r + str(hexoctet())
    return r

def uuid() -> str:
    """
    This method creates a universal UUID which is representing a 128-bit number. Specifications
    about the format can be seen on page 22 in the UPnP-Device-Architecture V2.0 document.

    [QUOTE]: (UPnP-arch-DeviceArchitecture-v2.0.pdf/ page.22 | 1.1.4 UUID format and recommended generation algorithms)
        ' UUIDs are 128-bit numbers that shall be formatted as specified by the following grammar
         (taken from [1]):
            UUID = 4 * <hexOctet> "-" 2 * <hexOctet> "-"   2 * <hexOctet> "-" 2 * <hexOctet> "-" 6 * <hexOctet>
            hexOctet = <hexDigit> <hexDigit>
            hexDigit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "a" | "b" | "c"
                        | "d" | "e" | "f" | "A" |"B" | "C" | "D" | "E" | "F"
        '
    """
    return "-".join([hexoctets(4), hexoctets(2), hexoctets(2), hexoctets(2), hexoctets(2), hexoctets(6)])