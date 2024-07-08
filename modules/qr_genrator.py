import tkinter as tk
import qrcode
import uuid
import zipfile
import datetime
from PIL import Image

class QRCodeGenerator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("QR Code Generator")

        self.num_qr_codes_label = tk.Label(self.window, text="Number of QR codes to generate:")
        self.num_qr_codes_entry = tk.Entry(self.window)
        
        self.size_label = tk.Label(self.window, text="QR Code size:")
        self.size_entry = tk.Entry(self.window)

        self.generate_button = tk.Button(self.window, text="Generate", command=self.generate_qr_codes)

        self.num_qr_codes_label.pack()
        self.num_qr_codes_entry.pack()
        self.size_label.pack()
        self.size_entry.pack()
        self.generate_button.pack()

        self.window.mainloop()

    def generate_qr_codes(self):
        # Get the number of QR codes to generate
        num_qr_codes = int(self.num_qr_codes_entry.get())

        # Get the QR code size
        size = int(self.size_entry.get())

        # Generate the QR codes
        qr_codes = []
        for i in range(num_qr_codes):
            # Generate a random UUID (UUID4)
            random_uuid = str(uuid.uuid4())

            # Create a QR code instance with the UUID as the data
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(random_uuid)
            qr.make(fit=True)

            # Create a QR code image with the specified size
            img = qr.make_image(fill_color="black", back_color="white").resize((size, size))

            # Save the QR code image to a file
            img.save(f"random_uuid_qr_{random_uuid}.png")

            # Add the QR code to the list
            qr_codes.append(random_uuid)

        # Create a zip file containing all of the QR code images
        zip_filename = f"{datetime.date.today()}_{num_qr_codes}.zip"
        with zipfile.ZipFile(zip_filename, "w") as zip_file:
            for qr_code in qr_codes:
                zip_file.write(f"random_uuid_qr_{qr_code}.png", arcname=f"{qr_code}.png")

        # Close the zip file
        zip_file.close()

        # Print a message to the user
        print(f"QR code images saved to zip file: {zip_filename}")

if __name__ == "__main__":
    qrcode_generator = QRCodeGenerator()
