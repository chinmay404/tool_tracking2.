import requests
import json

def get_master_data(uuid):
    url = f'http://your-domain/api/masters/{uuid}/'
    response = requests.get(url)
    
    if response.status_code == 200:
        master_data = response.json()
        return master_data
    elif response.status_code == 404:
        print("Master not found.")
        return None
    else:
        print("Failed to retrieve master data.")
        return None

def store_master_data_in_json(master_data, filename):
    if master_data:
        with open(filename, 'w') as json_file:
            json.dump(master_data, json_file, indent=4)
        print(f"Master data stored in {filename} successfully.")
    else:
        print("No master data to store.")

# Example usage
uuid = 'f7c71dda0de42324'
master_data = get_master_data(uuid)
if master_data:
    store_master_data_in_json(master_data, 'master_data.json')
