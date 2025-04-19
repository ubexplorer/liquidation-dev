import requests
import json

url = "https://a2p.vodafone.ua/uaa/oauth/token?grant_type=password&username=380503108795&password=Omega_1970"

payload = {}
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Basic aW50ZXJuYWw6aW50ZXJuYWw=',
  'Cookie': 'BIGipServerSF-OBM-30000=3500872876.12405.0000; TS01ee2dd3=01289bfb4afd38573405602c00d5b7249a499224358a865a8b14dacd778fa49f9f1d4993fa38d5dafd3b75260c7b01ded5e7a00ab2'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
