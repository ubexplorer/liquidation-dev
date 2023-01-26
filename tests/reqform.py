# source: https://stackoverflow.com/a/57325050/10504918

# import os
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


method = 'POST'
url = 'https://ovsb.ics.gov.ua/view/vgsu/bank_content.php'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Referer': 'https://ovsb.ics.gov.ua/view/vgsu/bankrut.php',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'X-Requested-With': 'XMLHttpRequest'
}

i = 0
payload = {
    'sEcho': 0,
    'iColumns': 9,
    'sColumns': '',
    'iDisplayStart': i,
    'iDisplayLength': 10,
    'mDataProp_0': 0,
    'mDataProp_1': 1,
    'mDataProp_2': 2,
    'mDataProp_3': 3,
    'mDataProp_4': 4,
    'mDataProp_5': 5,
    'mDataProp_6': 6,
    'mDataProp_7': 7,
    'mDataProp_8': 8,
    'sSearch': '',
    'bRegex': False,
    'sSearch_0': '',
    'bRegex_0': False,
    'bSearchable_0': True,
    'sSearch_1': '',
    'bRegex_1': False,
    'bSearchable_1': True,
    'sSearch_2': '',
    'bRegex_2': False,
    'bSearchable_2': True,
    'sSearch_3': '',
    'bRegex_3': False,
    'bSearchable_3': True,
    'sSearch_4': '',
    'bRegex_4': False,
    'bSearchable_4': True,
    'sSearch_5': '',
    'bRegex_5': False,
    'bSearchable_5': True,
    'sSearch_6': '',
    'bRegex_6': False,
    'bSearchable_6': True,
    'sSearch_7': '',
    'bRegex_7': False,
    'bSearchable_7': False,
    'sSearch_8': '',
    'bRegex_8': False,
    'bSearchable_8': False,
    'code': '',
    'regdate': '~',
    'sSearch_3': '',
    'sSearch_4': '',
    'q_ver': 'arbitr',
    'pdate': '~',
    'aucdate': '~',
    'aucplace': '',
    'ptype': 0,
    'pkind': 0,
    'price': '~',
    'ckind': ''
}

# req = requests.request(method=method, url=url, headers=headers, data=payload)
# preppered = s.prepare_request(req)
# resp = s.send(request=preppered)
# resp.raise_for_status()
# response = resp.json()

# resp = requests.get('http://httpbin.org/ip')
# resp = requests.get('https://api.ipify.org?format=json')
resp = requests.request(method=method, url=url, headers=headers, data=payload, verify=False)
responce = resp.json()
responce['iTotalDisplayRecords']
len(responce['aaData'])
log.debug(resp.status_code)

log.debug("iTotalDisplayRecords: {}".format(responce['iTotalDisplayRecords']))
log.debug("aaData count: {}".format(len(responce['aaData'])))
