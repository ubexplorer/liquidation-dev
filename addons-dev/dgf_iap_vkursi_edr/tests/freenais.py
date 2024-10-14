import requests
import json

url = "https://vkursi-api.azurewebsites.net/api/1.0/organizations/freenais?code=09807856"

payload = ""
headers = {
  'Authorization': 'Bearer {{token}}'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

