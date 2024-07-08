import qrcode
from PIL import Image, ImageDraw, ImageFont

qr = qrcode.QRCode(version=1, box_size=10, border=4)
qr.add_data("Your text to encode")
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")

draw = ImageDraw.Draw(img)
font = ImageFont.truetype("DejaVuSans.ttf", 16)  # Adjust font path and size
draw.text((5, img.height - 25), "Text below QR code", font=font, fill="black")

img.save("qrcode_with_text.png")
