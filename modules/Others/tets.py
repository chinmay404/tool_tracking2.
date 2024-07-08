import requests

trasnportlist_url = "http://10.10.1.18:8400/api/matservices/gettranspoterapilis"
grn_url = "http://10.10.1.18:8400/api/matservices/gettoolgrnlist"
saleorder_url = "http://10.10.1.18:8400/api/matservices/gettranspoterapilis"



print('Request Sent')
response = requests.get('http://10.10.1.18:8400/api/matservices/gettranspoterapilist')
if response.status_code == 200:  
    with open('transport_erp.json', 'w') as f:
        f.write(response.text)
    print('Response saved to response.json')
else: 
    print('No Response')
