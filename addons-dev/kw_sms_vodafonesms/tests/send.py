import requests
import json

url = "https://a2p.vodafone.ua/communication-event/api/communicationManagement/v2/communicationMessage/send"

payload = json.dumps({
  "content": "Привіт, Артеме!\nКонтакти колектора Форварда досі не отримано :)",
  "type": "SMS",
  "receiver": [
    {
      "id": 0,
      "phoneNumber": 380974854153
    },
    {
      "id": 1,
      "phoneNumber": 380930007909
    }
  ],
  "sender": {
    "id": "BANKFORWARD"
  },
  "characteristic": [
    {
      "name": "DISTRIBUTION.ID",
      "value": 5014965
    },
    {
      "name": "VALIDITY.PERIOD",
      "value": "000000120000000R"
    }
  ]
})
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVUb2tlblRpbWUiOjE2OTk2OTI5NzU1NDMsInVzZXJfbmFtZSI6Im9sLWtvdHZ5dHNreWlAZm9yd2FyZC1iYW5rLmNvbSIsInNjb3BlIjpbIm9wZW5pZCJdLCJyb2xlX2tleSI6IlJPTEVfT0JNX0NVU1RPTUVSX01BTkFHRVIiLCJ1c2VyX2tleSI6IjQ0Y2MxNjIxLWMzMjktNGMzMS04Y2JlLWQxZmY1MWIwNWEzOSIsImV4cCI6MTY5OTczNjE3NSwiYWRkaXRpb25hbERldGFpbHMiOnsiY3VzdG9tZXJfcHJvZmlsZV9pZCI6IjQ5OTc2NzQifSwibG9naW5zIjpbeyJ0eXBlS2V5IjoiTE9HSU4uTklDS05BTUUiLCJzdGF0ZUtleSI6bnVsbCwibG9naW4iOiLQsNC60YbRltC-0L3QtdGA0L3QtSDRgtC-0LLQsNGA0LjRgdGC0LLQviBcItCx0LDQvdC6INGE0L7RgNCy0LDRgNC0XCIifSx7InR5cGVLZXkiOiJMT0dJTi5NU0lTRE4iLCJzdGF0ZUtleSI6bnVsbCwibG9naW4iOiIzODA1MDMxMDg3OTUifSx7InR5cGVLZXkiOiJMT0dJTi5FTUFJTCIsInN0YXRlS2V5IjpudWxsLCJsb2dpbiI6Im9sLWtvdHZ5dHNreWlAZm9yd2FyZC1iYW5rLmNvbSJ9XSwiYXV0aG9yaXRpZXMiOlsiUk9MRV9PQk1fQ1VTVE9NRVJfTUFOQUdFUiJdLCJqdGkiOiIyMmU5MTYwNS1lMzVjLTQ1NGItYjQxOS0wYjVlMjZiYzk4Y2YiLCJ0ZW5hbnQiOiJYTSIsImNsaWVudF9pZCI6ImludGVybmFsIn0.VfArZ3tllv8_VmR9jPDp_4wAGzjS3oB7Bp5KPbCfDYwW7VpEx1Ugn8w-kM00UcfPIlZ_YN0LlpykBDfY9qLV9JX4pp5vUjMlQOILBCN7ctZjIfqtLUHPQ01ZVM3vuTxR77cXeO4s-Bpp5q73-xPh66VIGlisRvEjlKLJA9abLo0CqiePMA6HFzXNAGBcpIes1E4ae5F6RSr2LcslZKuWWaambKZ4y9KvnKqmm9KtuTjrVUPKt468jbNuvABelMxn07cBIzZrZGyUUuYBzqV18Rc1s6jONovuo48yJPlOeXGhH4JK_-aKVlvfxfJ8JrjeGcBjz-z_qfq1r9IKWSqf-g',
  'Cookie': 'BIGipServerSF-OBM-30000=3500872876.12405.0000; TS01ee2dd3=01289bfb4ab5022a6f3d9df614ca37977750bfc3c88a9cd1bc36bccfde3c09fc94c2bc5fb37c7bbea0f6db6340db86757c2fcea6c6'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
