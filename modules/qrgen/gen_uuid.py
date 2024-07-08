import uuid
import hashlib
from datetime import datetime




def generate_uuids(num_uuids):
    for _ in range(num_uuids):
            uuid_str = str(uuid.uuid4())
            sha1_hash = hashlib.sha1(uuid_str.encode()).hexdigest()
            current_year = datetime.now().year
            financial_year = str((current_year - 1))[-2:] + str(current_year)[-2:]
            id = sha1_hash[:12] + financial_year
            print(id)



if __name__ == "__main__":
    # Get user input for the number of UUIDs to generate
    try:
        num_uuids = int(input("Enter the number of UUIDs to generate: "))
    except ValueError:
        print("Please enter a valid number.")
        exit()
    generate_uuids(num_uuids)
