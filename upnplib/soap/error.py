# MIT License
# 
# Copyright (c) 2022 MatrixEditor
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from . import Fault

SOAP_ERROR = {
  401: """No action by that name at this service.""",  
  402: """
  Could be any of the following: not enough in args, args in the wrong
  order, one or more in args are of the wrong data type. Additionally,
  the UPnP Certification Test Tool shall return the following warning
  message if there are too many in args: ‘Sending too many in args is
  not recommended and may cause unexpected results.’""",  
  403: """(This code has been deprecated.)""",  
  501: """Is allowed to be returned if current state of service prevents invoking
  that action.""",  
  600: """The argument value is invalid""",  
  601: """An argument value is less than the minimum or more than the
  maximum value of the allowed value range, or is not in the allowed
  value list.""",  
  602: """The requested action is optional and is not implemented by the device.""",  
  603: """The device does not have sufficient memory available to complete the
  action. This is allowed to be a temporary condition; the control point
  is allowed to choose to retry the unmodified request again later and it
  is expected to succeed if memory is available.""",  
  604: """The device has encountered an error condition which it cannot resolve
  itself and required human intervention such as a reset or power cycle.
  See the device display or documentation for further guidance.""",  
  605: """A string argument is too long for the device to handle properly."""
}

def parse_fault(fault: Fault) -> tuple: # tuple[int, str, str]
  if not fault: return (0, None, None)
  global SOAP_ERROR

  if fault.error_code in SOAP_ERROR:
    return (fault.error_code, fault.error_descr, SOAP_ERROR[fault.error_code])
  else:
    if 613 <= fault.error_code <= 699:
      (fault.error_code, fault.error_descr, 
      'Common action errors. Defined by UPnP Forum Technical Committee.')
    elif 700 <= fault.error_code <= 799:
      (fault.error_code, fault.error_descr, 
      'Action-specific errors defined by UPnP Forum working committee.')
    elif 800 <= fault.error_code <= 899:
      (fault.error_code, fault.error_descr, 
      'Action-specific errors for non-standard actions. Defined by UPnP vendor.')
    else:
      (fault.error_code, fault.error_descr, 
      'These ErrorCodes are reserved for UPnP DeviceSecurity.')