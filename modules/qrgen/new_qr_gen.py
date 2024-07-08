import uuid
import qrcode
import os

def generate_qr_codes(num_uuids, output_folder, box_size=1):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for _ in range(num_uuids):
        generated_uuid = str(uuid.uuid4())

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,  
            border=4,
        )
        qr.add_data(generated_uuid)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")

        qr_filename = f"{generated_uuid}.jpeg"
        qr_filepath = os.path.join(output_folder, qr_filename)
        qr_img.save(qr_filepath)

if __name__ == "__main__":
    try:
        num_uuids = int(input("Enter the number of UUIDs to generate: "))
    except ValueError:
        print("Please enter a valid number.")
        exit()
    output_folder = input("Enter the output folder path (default is 'output'): ") or "/home/sirius/Public/Tool_Tracking/qrgen"
    try:
        box_size = int(input("Enter the box size for QR codes (default is 1): ") or 1)
    except ValueError:
        print("Please enter a valid number for box size.")
        exit()
    generate_qr_codes(num_uuids, output_folder, box_size)

    print(f"{num_uuids} QR codes generated and stored in {output_folder}.")
