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
from typing import Iterator

class CodeGenerator:
  def __init__(self, **kwargs) -> None:
    self._code = []
  
  def append(self, line: str) -> bool:
    """Appends the given code line to the stored code.
    
    Arguments:
      line: str
        The code line to be appended. If this line is None, False will be 
        returned.

    Returns: bool
      True on success, on failure False.
    """
    if not line: return False
    self._code.append(line)
    return True

  def dump_object(self, obj: object, **generator_options) -> bool:
    """Dumps the given object into the code lines.
    
    Arguments:
      obj: object
        The input object - could be everything.
      gnerator_options: dict[str, Any]
        Leaving options for classes that inherit from this base class.

    Returns: bool
      True if the code was successfully generated, False otherwise.
    """
    return False

  @property
  def codemeta(self) -> str:
    """The code lines packed into a list object."""
    return self._code

  def __iter__(self) -> Iterator[str]:
    return iter(self.codemeta)

  def __len__(self) -> int:
    return len(self.codemeta)

  def __iadd__(self, line: str) -> 'CodeGenerator':
    if line: self.append(line)
    return self

  def __repr__(self) -> str:
    return ''.join(self.codemeta)

  def __str__(self) -> str:
    return self.__repr__()

