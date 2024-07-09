import requests

print('Request Sent')
data = requests.get('http://10.10.1.18:8400/api/matservices/gettoolgrnlist')
if data:
	print(data)
else : 
	print('No Response')
