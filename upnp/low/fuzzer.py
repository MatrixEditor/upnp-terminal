import requests

DO_DEBUG = False

# The real funtion is defined below:
# with this code, only services with a positive
# url-fetching result are added  
def run_rec(x):
    a = x
    while True:
        d = fetch_rec(a.split('/'))
        if not d:
            break
        else:
            if not d[1]:
                # removing the 'http://'-tag
                a = d[0][7:]
            else:
                try:
                    yield d
                except:
                    if DO_DEBUG:
                        print("\n(upnp.fuzzer) [ERROR] --r : malformed url")
                break

# the function below generates all possible urls with
# swapping the 'path_nodes' in a given url. 
def make_lists(x):
    # the address and target shouldn't be affected
    t = x[0]; h = x[len(x) - 1]
    x = x[1:-1]; z = []
    if len(x) > 0:
        for i in range(0, len(x)):
            head = x[i]
            r = [head]
            for i in range(0, len(x)):
                tail = x[i]
                if head != tail:
                    r.append(tail)
            c = 'http://%s/%s/%s' % (t, '/'.join(r), h)
            if c not in z:
                z.append(c)
    else:
        z.append('http://%s/%s' % (t ,h))
    return z

def do_fetch(b):
  try:
      # make the full request by adding the 'http'
      # tag at the beginning
      c = 'http://%s' % ('/'.join(b))
      p = requests.get(c)
  except:
      return (c, None)
  else:
      # The status code has to 200 or something
      # else, but never 404
      if DO_DEBUG:
          print('   \t\t[%s -> %s]' % (p.status_code, c))
      if p.status_code == 404:
          return (c, None)
      else:
          # if everything went well, the page-text is
          # delivered as string
          return (c, p.text)

def fetch_rec(x):
  z = do_fetch(b=x)
  if not z[1]:
      # 'X' is the url without the 'http' tag
      b = z[0][7:].split('/')

      # first, check if there is a file located in 
      # the url-path
      if '.' in b[len(b) - 1]: 
          # Then check if there are any path_nodes left . 
          # Base length is [address, path_node, file] if
          # another request could be made.
          if len(b) >= 3:
              b[len(b) - 2] = b[len(b) - 1]
              b = b[:-1]
          else:
              return None
      else:
          # In this case a '/' is at the end of the url:
          # parts: [address, path_node, '']
          if len(b) >= 3:
              if '' == b[len(b) - 1]:
                  b = b[:-2]
              else:
                  b[len(b) - 2] = b[len(b) - 1]
                  b = b[:-1]
          else:
              return None
      return do_fetch(b=b)
  else:
      return z

def url_fuzz(url_base):
  """ 
  if a description-page is not located at for example at
  http://xx/path_node/description.xml when the base
  url is http://xx/path_node/main.xml, then more tries
  are made by this code below by taking each additional
  path_node away and make a http-request. 
  """
  if not url_base:
    return [None]
  
  a = url_base[7:]
  _urls = make_lists(a.split('/'))
  _ = []
  for u in _urls:
      # prevent errors
      if len(u) != 0:
          for x in run_rec(u[7:]):
            _.append(x)
  return _
