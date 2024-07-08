import psycopg2
import json
from datetime import datetime


def create_vehicle_instance(conn, cursor, data):
    # Extract data from API response
    vehicle_number = data.get('vehicleNumber')

    # Check if the vehicle already exists in the database
    cursor.execute(
        "SELECT COUNT(*) FROM managment_vehicle WHERE vehicle_number = %s", (vehicle_number,))
    count = cursor.fetchone()[0]

    if count > 0:
        print(
            f"Vehicle with number {vehicle_number} already exists. Skipping insertion.")
        return

    vehicle_make = data.get('vehicleMake')
    vehicle_model = data.get('vehicleModel')
    fuel_type = data.get('fuelType')
    vehicle_year = data.get('vehicleYear')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    last_updated_at = datetime.fromtimestamp(data.get('lastUpdatedAt') / 1000)
    last_status_time = datetime.fromtimestamp(
        data.get('lastStatusTime') / 1000)
    last_acc_on = datetime.fromtimestamp(data.get('lastAccOn') / 1000)
    total_odometer = data.get('totalOdometer')
    current_status = data.get('currentStatus')
    address = data.get('address')
    tag_ids = json.dumps(data.get('tagIds'))
    vehicle_type_value = data.get('vehicleTypeValue')
    on_path = False

    # Insert data into the Vehicle table
    cursor.execute("""
        INSERT INTO managment_vehicle (vehicle_number,on_path, vehicle_make, vehicle_model, fuel_type, vehicle_year, latitude, longitude, last_updated_at, last_status_time, last_acc_on, total_odometer, current_status, address, tag_ids, vehicle_type_value)
        VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (vehicle_number,on_path, vehicle_make, vehicle_model, fuel_type, vehicle_year, latitude, longitude, last_updated_at, last_status_time, last_acc_on, total_odometer, current_status, address, tag_ids, vehicle_type_value))

    print(f"Vehicle with number {vehicle_number} inserted successfully.")

    # Commit the transaction
    conn.commit()


if __name__ == '__main__':
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        dbname="tool_tracking",
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432"
    )
    cur = conn.cursor()
    print("Connected")

    # API response containing vehicle data
    api_response = {
            "totalVehicles": 5,
            "runningVehicles": 0,
            "idleVehicles": 0,
            "parkedVehicles": 4,
            "removedVehicles": 0,
            "inshopVehicles": 0,
            "disconnectedVehicles": 1,
            "unreachableVehicles": 0,
            "immobilisedVehicles": 0,
            "nopowerVehicles": 0,
            "standbyVehicles": 0,
            "batteryDischargedVehicles": 0,
            "utilization": 0.0,
            "alarms": 0,
            "dtc": 0,
            "vehicles": [
                {
                    "accountId": 9492,
                    "vehicleId": 456761,
                    "groupId": 0,
                    "vehicleNumber": "MH09EM0328",
                    "vehicleName": "ORANGE - SPM",
                    "vehicleMake": "TATA",
                    "vehicleModel": "Ace",
                    "fuelType": "Diesel",
                    "vehicleYear": 2017,
                    "driverName": "",
                    "speed": 0.0,
                    "totalFuelConsumption": 0.0,
                    "totalOdometer": 21354.547,
                    "status": "Ignition Off",
                    "latitude": 16.757065,
                    "longitude": 74.2700433,
                    "lastUpdatedAt": 1709639652000,
                    "lastStatusTime": 1709639490000,
                    "mileage": 0.0,
                    "lastAccOn": 1709639252000,
                    "durationEngineOn": 0,
                    "currentStatus": "PARKED",
                    "otherAttributes": {
                        "altitude": "574",
                        "workMode": "5",
                        "tagIds": "24530",
                        "type": "GPS",
                        "di1": "0",
                        "fuelTankCapacity": "42.0",
                        "di4": "0",
                        "operator": "40490",
                        "lac": "5958",
                        "lastGpsValidTime": "1709639480000",
                        "powerStatus": "true",
                        "actualStatus": "Ignition On",
                        "controlVoltage": "3.93",
                        "axisZ": "-32",
                        "sim": "8991102205635000502",
                        "axisY": "121",
                        "gpsStatus": "1",
                        "axisX": "219",
                        "course": "229.0",
                        "serverTime": "1709639485324",
                        "power": "12.717",
                        "countInvalidGps": "0",
                        "ignition": "true",
                        "internalBattery": "83%",
                        "deviceType": "FMB911",
                        "sleepMode": "0",
                        "rssi": "5.0",
                        "motion": "true",
                        "odometer": "21354.547",
                        "sat": "19",
                        "secondsOfInvalidGps": "0",
                        "hdop": "0.6000000000000001",
                        "ct": "1709639657330",
                        "dout1": "0",
                        "tripOdometer": "1.068",
                        "imei": "350544503658414",
                        "io15": "1000",
                        "io181": "8",
                        "cid": "2132",
                        "status": "Ignition On"
                    },
                    "address": "Shiroli Main Road,MIDC,Shiroli,Kolhapur,Maharashtra,India,416122",
                    "driverId": 0,
                    "deviceId": "350544503658414",
                    "eta": 0,
                    "distance": 0,
                    "vehicleTypeValue": "Truck",
                    "tagIds": [
                        24530
                    ],
                    "providerCode": "Fleetx"
                },
                {
                    "accountId": 9492,
                    "vehicleId": 456768,
                    "groupId": 0,
                    "vehicleNumber": "MH09EM9757",
                    "vehicleName": "9757",
                    "vehicleMake": "TATA",
                    "vehicleModel": "Ace",
                    "fuelType": "Diesel",
                    "vehicleYear": 2017,
                    "driverName": "",
                    "speed": 0.0,
                    "totalFuelConsumption": 0.0,
                    "totalOdometer": 52957.871,
                    "status": "Ignition Off",
                    "latitude": 16.7706683,
                    "longitude": 74.2735483,
                    "lastUpdatedAt": 1688472850000,
                    "lastStatusTime": 1688472850000,
                    "mileage": 0.0,
                    "lastAccOn": 1688472560000,
                    "durationEngineOn": 0,
                    "currentStatus": "DISCONNECTED",
                    "otherAttributes": {
                        "altitude": "577",
                        "currentFuelConsumption": "0.0",
                        "workMode": "5",
                        "type": "ALARM",
                        "di1": "0",
                        "fuelTankCapacity": "42.0",
                        "di4": "0",
                        "operator": "40490",
                        "lac": "5958",
                        "valid": "true",
                        "lastGpsValidTime": "1688472817000",
                        "powerStatus": "false",
                        "actualStatus": "Low Voltage",
                        "controlVoltage": "3.326",
                        "axisZ": "450",
                        "sim": "8991102105469677963",
                        "axisY": "881",
                        "gpsStatus": "1",
                        "axisX": "33",
                        "course": "257.0",
                        "io24": "6",
                        "serverTime": "1688472820266",
                        "power": "0.0",
                        "countInvalidGps": "0",
                        "ignition": "true",
                        "internalBattery": "29%",
                        "deviceType": "FMB910",
                        "sleepMode": "0",
                        "rssi": "5.0",
                        "motion": "false",
                        "odometer": "52957.871",
                        "sat": "19",
                        "secondsOfInvalidGps": "0",
                        "lastGpsTime": "1688472850000",
                        "lastStopAddressBookId": "207028",
                        "hdop": "0.4",
                        "ct": "1688472853424",
                        "dout1": "0",
                        "tripOdometer": "0.328",
                        "io15": "1000",
                        "io181": "7",
                        "cid": "6063",
                        "status": "Ignition On"
                    },
                    "address": "MIDC,Shiroli,Kolhapur,Maharashtra,India,416122",
                    "driverId": 0,
                    "deviceId": "354018114402112",
                    "eta": 0,
                    "distance": 0,
                    "vehicleTypeValue": "Truck",
                    "tagIds": [
                        24530
                    ],
                    "providerCode": "Fleetx"
                },
                {
                    "accountId": 9492,
                    "vehicleId": 456795,
                    "groupId": 0,
                    "vehicleNumber": "MH09CU5797",
                    "vehicleName": "5797 GREEN",
                    "vehicleMake": "TATA",
                    "vehicleModel": "Ace",
                    "fuelType": "Diesel",
                    "vehicleYear": 2015,
                    "driverName": "",
                    "speed": 0.0,
                    "totalFuelConsumption": 0.0,
                    "totalOdometer": 14213.213,
                    "status": "Ignition Off",
                    "latitude": 16.7395616,
                    "longitude": 74.2821633,
                    "lastUpdatedAt": 1709639503000,
                    "lastStatusTime": 1709639503000,
                    "mileage": 0.0,
                    "lastAccOn": 1709638682000,
                    "durationEngineOn": 0,
                    "currentStatus": "PARKED",
                    "otherAttributes": {
                        "altitude": "572",
                        "workMode": "5",
                        "tagIds": "24530",
                        "type": "ALARM",
                        "di1": "0",
                        "fuelTankCapacity": "42.0",
                        "di4": "0",
                        "operator": "40490",
                        "lac": "5958",
                        "lastGpsValidTime": "1709639470000",
                        "powerStatus": "true",
                        "actualStatus": "Ignition On",
                        "controlVoltage": "3.981",
                        "axisZ": "-5",
                        "sim": "8991102205616579441",
                        "axisY": "11",
                        "gpsStatus": "1",
                        "axisX": "-33",
                        "course": "143.0",
                        "serverTime": "1709639472177",
                        "power": "12.584",
                        "countInvalidGps": "0",
                        "ignition": "true",
                        "internalBattery": "87%",
                        "deviceType": "FMB910",
                        "sleepMode": "0",
                        "rssi": "5.0",
                        "motion": "false",
                        "odometer": "14213.213",
                        "sat": "18",
                        "secondsOfInvalidGps": "0",
                        "hdop": "0.6000000000000001",
                        "ct": "1709639505089",
                        "dout1": "0",
                        "tripOdometer": "3.283",
                        "imei": "350424062909401",
                        "io15": "1000",
                        "io181": "8",
                        "cid": "51942",
                        "status": "Ignition On"
                    },
                    "address": "Mumbai Highway,Shiroli,Kolhapur,Maharashtra,India,416122",
                    "driverId": 0,
                    "deviceId": "350424062909401",
                    "eta": 0,
                    "distance": 0,
                    "vehicleTypeValue": "Truck",
                    "tagIds": [
                        24530
                    ],
                    "providerCode": "Fleetx"
                },
                {
                    "accountId": 9492,
                    "vehicleId": 456855,
                    "groupId": 0,
                    "vehicleNumber": "MH10AQ9757",
                    "vehicleName": "9757",
                    "vehicleMake": "Market",
                    "vehicleModel": "Truck",
                    "fuelType": "Diesel",
                    "vehicleYear": 2019,
                    "driverName": "",
                    "speed": 0.0,
                    "totalFuelConsumption": 0.0,
                    "totalOdometer": 16398.82,
                    "status": "Ignition Off",
                    "latitude": 16.7708783,
                    "longitude": 74.27386,
                    "lastUpdatedAt": 1709639375000,
                    "lastStatusTime": 1709624229000,
                    "mileage": 0.0,
                    "lastAccOn": 1709624167000,
                    "durationEngineOn": 0,
                    "currentStatus": "PARKED",
                    "otherAttributes": {
                        "altitude": "500",
                        "workMode": "5",
                        "tagIds": "24530",
                        "type": "GPS",
                        "di1": "0",
                        "di4": "0",
                        "operator": "40490",
                        "lac": "5958",
                        "lastGpsValidTime": "1709624197000",
                        "powerStatus": "true",
                        "actualStatus": "Ignition On",
                        "controlVoltage": "3.9650000000000003",
                        "axisZ": "-19",
                        "sim": "8991102205635000858",
                        "axisY": "39",
                        "gpsStatus": "1",
                        "axisX": "4",
                        "course": "113.0",
                        "serverTime": "1709624202279",
                        "power": "12.368",
                        "countInvalidGps": "0",
                        "ignition": "true",
                        "internalBattery": "86%",
                        "deviceType": "FMB911",
                        "sleepMode": "0",
                        "rssi": "5.0",
                        "motion": "false",
                        "odometer": "16398.82",
                        "sat": "19",
                        "secondsOfInvalidGps": "0",
                        "hdop": "0.6000000000000001",
                        "ct": "1709639380425",
                        "dout1": "0",
                        "tripOdometer": "0.0",
                        "io15": "1000",
                        "io181": "10",
                        "cid": "6063",
                        "status": "Ignition On"
                    },
                    "address": "MIDC,Shiroli,Kolhapur,Maharashtra,India,416122",
                    "driverId": 0,
                    "deviceId": "350544508304667",
                    "eta": 0,
                    "distance": 0,
                    "vehicleTypeValue": "Truck",
                    "tagIds": [
                        24530
                    ],
                    "providerCode": "Fleetx"
                },
                {
                    "accountId": 9492,
                    "vehicleId": 456875,
                    "groupId": 0,
                    "vehicleNumber": "MH09EM7057",
                    "vehicleName": "7057",
                    "vehicleMake": "TATA",
                    "vehicleModel": "Ace",
                    "fuelType": "Diesel",
                    "vehicleYear": 2018,
                    "driverName": "",
                    "speed": 0.0,
                    "totalFuelConsumption": 0.0,
                    "totalOdometer": 10048.87,
                    "status": "Ignition Off",
                    "latitude": 16.77064,
                    "longitude": 74.273665,
                    "lastUpdatedAt": 1709639599000,
                    "lastStatusTime": 1709639599000,
                    "mileage": 0.0,
                    "lastAccOn": 1709639581000,
                    "durationEngineOn": 0,
                    "currentStatus": "PARKED",
                    "otherAttributes": {
                        "tagIds": "24530",
                        "type": "ALARM",
                        "fuelTankCapacity": "42.0",
                        "harshSpeed": "false",
                        "liveData": "false",
                        "sleep": "true",
                        "lastGpsValidTime": "1709639594000",
                        "powerStatus": "true",
                        "actualStatus": "Ignition On",
                        "wireTemperature": "0.0",
                        "controlVoltage": "4.1",
                        "sosStatus": "false",
                        "harshBrake": "false",
                        "course": "186.0",
                        "serverTime": "1709639605665",
                        "countInvalidGps": "0",
                        "firmware": "ATL_9.5.6_LE_1.9.5_FLEETX",
                        "ignition": "true",
                        "deviceType": "E101",
                        "lastFirmwareCheckTime": "1709584330541",
                        "rssi": "31",
                        "odometer": "10048.87",
                        "onBoardTempOrDeviceVersion": "33.0",
                        "magVariation": "",
                        "sat": "29",
                        "secondsOfInvalidGps": "0",
                        "lastStopAddressBookId": "207028",
                        "accel": "true",
                        "ct": "1709639611942",
                        "armMode": "false",
                        "tripOdometer": "0.004177236574687615",
                        "acStatus": "false",
                        "imei": "GE11022A2958",
                        "status": "Ignition On"
                    },
                    "address": "MIDC,Shiroli,Kolhapur,Maharashtra,India,416122",
                    "driverId": 0,
                    "deviceId": "868805061740612",
                    "eta": 0,
                    "distance": 0,
                    "vehicleTypeValue": "Truck",
                    "tagIds": [
                        24530
                    ],
                    "providerCode": "Fleetx"
                }
            ],
            "expiry": 0,
            "timezone": "Asia/Kolkata",
            "currency": "INR",
            "fleetType": ""

    }

    # Extract the vehicles from the API response
    vehicles_data = api_response.get('vehicles', [])

    # Create Vehicle instances for each vehicle in the API response
    for vehicle_data in vehicles_data:
        create_vehicle_instance(conn, cur, vehicle_data)

    # Close the cursor and connection
    cur.close()
    conn.close()
