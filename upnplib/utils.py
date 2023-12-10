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
import xml.etree.ElementTree as xmltree
import urllib3

def _xmlrelpath(element: xmltree.Element) -> str:
  try:
    return element.tag[element.tag.index('}') + 1:]
  except ValueError:
    return element.tag

def _xmlns(element: xmltree.Element) -> str:
  return _xmlnamespace(element, 'ns')['ns']

def _xmlfind_attr(root: xmltree.Element, tag: str, name: str, default = None,
                  namepaces: dict = None):
  return _xmlfind(root, tag, lambda x: x.get(name, default), default, namepaces)

def _xmlfind(root: xmltree.Element, tag: str, extractor = lambda x: x.text, 
             default = None, namepaces: dict = None):
  if not root: return default
  result = root.find(tag, namepaces)
  if result is None: return default
  else: return extractor(result)

def _xmlnamespace(element: xmltree.Element, key: str) -> dict:
  if element is None: return {}
  name = element.tag
  return {key: name[1:name.index('}')]}

def fuzz_request(url_base) -> urllib3.HTTPResponse:
    base = url_base[7:]
    manager = urllib3.PoolManager()
    for url in spliturls(base):
      while True:
        response = _fetch_req(url, manager)
        if response is not None: return response
        else:
          nodes = url[7:].split('/')
          # first, check if there is a file located in 
          # the url-path  
          if '.' in nodes[-1]:
            # Then check if there are any path_nodes left . 
            # Base length is [address, path_node, file] if
            # another request could be made.
            if len(nodes) >= 3:
              nodes[-2] = nodes[-1]
              nodes = nodes[:-1]
              url = 'http://%s' % ('/'.join(nodes))
              continue
            break
          else:
            # In this case a '/' is at the end of the url:
            # parts: [address, path_node, '']
            if len(nodes) >= 3:
              if '' == nodes[-1]:
                nodes = nodes[:-2]
              else:
                nodes[-2] = nodes[-1]
                nodes = nodes[:-1]
              url = 'http://%s' % ('/'.join(nodes))
              continue
            else: break
  
def _fetch_req(url: str, manager: urllib3.PoolManager) -> urllib3.HTTPResponse:
  try:
    response = manager.request('GET', url)
  except:
    return None
  else:
    if response.status == 200:
      return response

def spliturls(base: str) -> list:
  nodes = base.split('/')
  head = nodes[0]
  tail = nodes[-1]
  nodes = nodes[1:-1]
  urls = []

  urls.append('http://%s/%s' % (head, tail))
  if len(nodes) > 0:
    for i in range(0, len(nodes)):
      head_local = nodes[i]
      current = [head_local]
      for j in range(0, len(nodes)):
        tail_local = nodes[j]
        if head_local != tail_local:
          current.append(tail_local)
      u = 'http://%s/%s/%s' % (head, '/'.join(current), tail)
      if u not in urls:
        urls.append(u)
  return urls