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
__doc__ = """A pseudocode generator.

The code parts are defined as follows:

1. global variables:
--------------------
  
  <VAR_TYPE> := 1*CHAR
  <VAR_NAME> := ['A_ARG_TYPE' | 'X_' ] 1*CHAR
  <VALUE>    := 1*CHAR
  <VALUES>   := ['@default(' VALUE ')']
  <RANGE>    := ['@range(start=' VALUE ', stop=' VALUE 'step=' 
                VALUE ')']
  <ALLOWED>  := ['@allowed(' 1*VALUE ')']
  <GLOBAL>   := VALUES RANGE ALLOWED 'define' ['eventing' ['(multicast)']] 
                VAR_NAME 'as' VAR_TYPE

  Examples:
  --------

    define eventing ClockUpdateID as ui4
    define eventing(mutlicast) SinkProtocolInfo as string


2. action functions:
--------------------

  <FUNC_NAME> := 1*CHAR
  <PARAMS>    := VAR_TYPE ' ' VAR_NAME
  <RETURNS>   := 'return ' 1*('var' VAR_NAME) 
  <FUNC_BODY> := '->' ['tuple' | VAR_TYPE] ':' RETURNS
  <FUNCTION>  := ['void'] 'def' FUN_NAME '(' [PARAMS] ')' (FUNC_BODY | ';')

  Examples:
  --------

    void def ConnectionComplete(i4 connectionid);

    def GetCurrentConnectionIDs() -> string: 
      return varCurrentConnectionIDs

Inline comments are allowed with the '#' and block comments can be done with
the '/** */'.
"""

from ..desc import scpd, StateVariable, Action, Argument
from . import CodeGenerator

class PseudoCode(CodeGenerator):
  def dump_object(self, obj: scpd, **generator_options) -> bool:
    out_file = generator_options['fp'] if 'fp' in generator_options else None
    is_stdout = generator_options['sysout'] if 'sysout' in generator_options else False

    for var in obj.svars:
      if not self._global_var(obj.svars[var]): 
        return False
    
    self += '\n'
    for action_name in obj.actionList:
      if not self._function(obj.actionList[action_name]):
        return False
    
    if is_stdout: print(repr(self))
    if out_file is not None:
      with open(out_file, 'w') as resource:
        resource.write(repr(self))
    
  def _global_var(self, variable: StateVariable) -> bool:
    if variable is None: return False

    range_desc = ''
    if variable.allowed_range is not None:
      range_desc = '@range(start=%d, stop=%d, step=%d)\n' % (
        variable.allowed_range.start, variable.allowed_range.stop,
        variable.allowed_range.step
      )
    
    allowed = ''
    if len(variable.allowed_values) != 0:
      allowed = '@allowed(%s)\n' % (', '.join(variable.allowed_values))
    
    default = ''
    if variable.default is not None:
      default = '@default(%s)\n' % variable.default

    eventing = ''
    if variable.eventing:
      eventing = ' eventing'
      if variable.is_multicast():
        eventing = '%s(multicast)' % eventing
    
    signature = 'define%s %s as %s\n\n' % (eventing, variable.name, variable.typename)
    self += ''.join([default, range_desc, allowed, signature])
    return True

  def _function(self, action: Action) -> bool:
    if not action: return False

    args = []
    for argument in action.in_arguments:
      if type(argument.rst) == str:
        args.append('Ref<%s> %s' % (argument.rst, argument.name))
      else:
        args.append(' '.join([argument.rst.typename, argument.name]))
    
    returns = []
    for argument in action.out_arguments:
      returns.append('var%s' % argument.name)
    
    if len(returns) == 0:
      self += 'void def %s(%s);\n\n' % (action.name, ', '.join(args))
    else:
      ret_type = action.out_arguments[0].rst.typename
      if len(returns) > 1:
        ret_type = 'tuple'

      signature = 'def %s(%s) -> %s:' % (action.name, ', '.join(args), ret_type)
      self += '%s\n\treturn %s\n\n' % (signature, ', '.join(returns)) 
    return True
  