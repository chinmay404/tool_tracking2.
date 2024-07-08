import uuid
import qrcode
import svgwrite

def generate_svg(uuid_str, filename):
    dwg = svgwrite.Drawing(filename, profile='tiny')
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uuid_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    for ridx, row in enumerate(img.modules):
        for cidx, color in enumerate(row):
            if color:
                dwg.add(dwg.rect(insert=(cidx, ridx), size=(1, 1), fill='black'))

    dwg.save()

def main():
    try:
        num_uuids = int(input("Enter the number of UUIDs to generate: "))
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    for _ in range(num_uuids):
        new_uuid = str(uuid.uuid4())
        svg_filename = f"qrcode_{new_uuid}.svg"
        generate_svg(new_uuid, svg_filename)
        print(f"QR code generated for UUID: {new_uuid} - Saved as {svg_filename}")

if __name__ == "__main__":
    main()
