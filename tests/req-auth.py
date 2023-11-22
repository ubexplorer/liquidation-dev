# source: https://stackoverflow.com/a/57325050/10504918

import os
import requests
import logging
from requests.auth import HTTPBasicAuth
import base64

_logger = logging.getLogger(__name__)

username = "380503108795"
password = "Omega_1970"

credentials = ('%s:%s' % (username, password))
# encoded_credentials = base64.b64encode(credentials.encode('utf-8'))
encoded_credentials = base64.b64encode(credentials.encode('ascii'))
basic = encoded_credentials.decode("ascii")
print(basic)


# url = 'https://httpbin.org/basic-auth/user/pass'
url = "https://a2p.vodafone.ua/uaa/oauth/token?grant_type=password&username={username}&password={password}".format(username=username, password=password)
headers = {'Content-Type': 'application/json'}
basic = HTTPBasicAuth(username, password)
# Basic aW50ZXJuYWw6aW50ZXJuYWw=
# Basic aW50ZXJuYWw6aW50ZXJuYWw=
# Basic MzgwNTAzMTA4Nzk1Ok9tZWdhXzE5NzA=
# MzgwNTAzMTA4Nzk1Ok9tZWdhXzE5NzA=
# MzgwNTAzMTA4Nzk1Ok9tZWdhXzE5NzA=

session = requests.Session()
session.auth = (username, password)

auth = session.post(url=url, headers=headers)
print(auth.request.headers)
print(auth.json())

# response = session.get('http://' + hostname + '/rest/applications')

# {
#     'User-Agent': 'python-requests/2.21.0', 
#     'Accept-Encoding': 'gzip, deflate', 
#     'Accept': '*/*', 
#     'Connection': 'keep-alive', 
#     'Content-Type': 'application/json', 
#     'Content-Length': '0', 
#     'Authorization': 'Basic MzgwNTAzMTA4Nzk1Ok9tZWdhXzE5NzA='
#     }
# r = requests.post(url=url, headers=headers, auth=basic)
# print(r.request.headers)
# print(r.json())


# s = requests.Session()
# # Get environment variables
# http_proxy = os.getenv('http_proxy')
# https_proxy = os.environ.get('https_proxy')
# PATH = os.environ.get('PATH')
# print('https_proxy: {0}, http_proxy: {1}.'.format(https_proxy, http_proxy))
# print('PATH: {0}.'.format(PATH))
# s.proxies = {
#     'http': http_proxy,
#     'https': https_proxy,
# }

# method = 'GET'
# url = 'http://httpbin.org/ip'
# req = requests.Request(method=method, url=url)
# preppered = s.prepare_request(req)
# resp = s.send(request=preppered)
# resp.raise_for_status()
# response = resp.json()

# # resp = requests.get('http://httpbin.org/ip')
# # resp = requests.get('https://api.ipify.org?format=json')
# log.debug(resp.headers)
# log.debug(resp.text)
