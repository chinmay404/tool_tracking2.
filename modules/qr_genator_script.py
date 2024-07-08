import qrcode
import uuid

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

# Create a QR code image
img = qr.make_image(fill_color="black", back_color="white")

# Save the QR code image to a file
img.save("random_uuid_qr.png")

# Print the UUID
print("Random UUID (UUID4):", random_uuid)