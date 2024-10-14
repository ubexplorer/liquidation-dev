import requests
import json

url = "https://vkursi-api.azurewebsites.net/api/1.0/organizations/payNaisSign?id=2574044"

payload = ""
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiLQodC10YDQs9GW0LkiLCJlbWFpbCI6IlNlcmhpaS5aYXZhbGtvQGZnLmdvdi51YSIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWVpZGVudGlmaWVyIjoiMjhmN2EyNDQtZTM5NS00ZDgyLTQ3YTktMDhkNmY3MWViNWE3IiwianRpIjoiOWZhZjE5NDYtNDAxNy00M2VkLTg4NWQtMTA2Y2IwZDNhN2QyIiwiZXhwIjoxNzI1NjM2OTQyLCJpc3MiOiJodHRwczovL3ZrdXJzaS5wcm8vIiwiYXVkIjoiaHR0cHM6Ly92a3Vyc2kucHJvLyJ9.PIBoZGkaiarKEapQkW4G9q66XJVvFxDU3SRqL_RhuoM',
  'Content-Type': 'application/json',
  'Cookie': 'TiPMix=20.1075096695279; x-ms-routing-name=self'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
