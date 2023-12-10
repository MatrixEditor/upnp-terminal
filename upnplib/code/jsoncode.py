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
from ..desc import scpd, StateVariable, Action
from . import CodeGenerator

from sys import stdout
from json import dumps

class JsonCode(CodeGenerator):
  def dump_object(self, obj: scpd, **generator_options) -> bool:
    out_stream = generator_options['fp'] if 'fp' in generator_options else stdout

    root = {'StateVariableTable': [], 'ActionList': []}
    for var in obj.svars:
      if not self._global_var(root['StateVariableTable'], obj.svars[var]): 
        return False

    for action_name in obj.actionList:
      if not self._function(root['ActionList'], obj.actionList[action_name]):
        return False

    serialized = dumps(root)
    if out_stream is not None:
      if type(out_stream) == str:
        with open(out_stream, 'w') as resource:
          resource.write(serialized)
      else:
        out_stream.write(serialized)

  def _global_var(self, root: list, variable: StateVariable) -> bool:
    if variable is None: return False

    _desc = {'Name': variable.name, 'Type': variable.typename}
    if variable.allowed_range is not None:
      _desc['AllowedRange'] = {
        "start": variable.allowed_range.start,
        "stop": variable.allowed_range.stop,
        "step": variable.allowed_range.step
      }
    
    if len(variable.allowed_values) != 0:
      _desc['AllowedValues'] = variable.allowed_values
    
    if variable.default is not None:
      _desc['Default'] = variable.default

    _desc['Eventing'] = variable.eventing
    _desc['Multicast'] = variable.is_multicast()
    root.append(_desc)
    return True

  def _function(self, root: list, action: Action) -> bool:
    if not action: return False

    args = []
    for argument in action.in_arguments:
      if type(argument.rst) == str:
        args.append('Ref<%s> %s' % (argument.rst, argument.name))
      else:
        args.append(' '.join([argument.rst.typename, argument.name]))
    
    returns = []
    for argument in action.out_arguments:
      returns.append(argument.name)
    
    _desc = {'name': action.name, 'args': args, 'returns': returns}
    if len(returns) != 0:
      ret_type = action.out_arguments[0].rst.typename
      if len(returns) > 1:
        ret_type = 'tuple'

      _desc['ret_type'] = ret_type
    
    root.append(_desc)
    return True