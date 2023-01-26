# source: https://stackoverflow.com/a/57325050/10504918

import os
import requests
import logging
from http.client import HTTPConnection  # py3

log = logging.getLogger('urllib3')
log.setLevel(logging.DEBUG)

# logging from urllib3 to console
stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
log.addHandler(stream)

# print statements from `http.client.HTTPConnection` to console/stdout
HTTPConnection.debuglevel = 1

s = requests.Session()
# Get environment variables
http_proxy = os.getenv('http_proxy')
https_proxy = os.environ.get('https_proxy')
PATH = os.environ.get('PATH')
print('https_proxy: {0}, http_proxy: {1}.'.format(https_proxy, http_proxy))
print('PATH: {0}.'.format(PATH))
s.proxies = {
    'http': http_proxy,
    'https': https_proxy,
}

method = 'GET'
url = 'http://httpbin.org/ip'
req = requests.Request(method=method, url=url)
preppered = s.prepare_request(req)
resp = s.send(request=preppered)
resp.raise_for_status()
response = resp.json()

# resp = requests.get('http://httpbin.org/ip')
# resp = requests.get('https://api.ipify.org?format=json')
log.debug(resp.headers)
log.debug(resp.text)
