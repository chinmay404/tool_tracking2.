import requests

def get_live_location(vehicle_number):
    url = f"https://api.fleetx.io/api/v1/analytics/live/byNumber/{vehicle_number}"
    headers = {
        "Authorization": "Bearer bbb342c4-c2a6-43fa-9475-0f8151eb1e7d"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None  # or raise an exception or handle the error accordingly

if __name__ == "__main__":
    vehicle_number = "MH10AQ9757"
    live_location_data = get_live_location(vehicle_number)
    if live_location_data:
        print("Live Location Data:")
        print(live_location_data)
    else:
        print("Failed to fetch live location data.")
