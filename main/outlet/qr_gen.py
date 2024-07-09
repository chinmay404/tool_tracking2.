import uuid
import qrcode
from io import BytesIO
from qrcode.image.styledpil import StyledPilImage
from PIL import Image, ImageDraw, ImageFont
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer
import json
import base64
import os
from django.conf import settings


MEDIA_ROOT = settings.MEDIA_ROOT


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logo_filename = 'hariom_logo.jpg'
logo_path = os.path.join(BASE_DIR, 'static', 'managment', 'outlet', 'src', logo_filename)

def generate_multi_uuid_qr(uuids, bill_no):
    data = {"bill_no": bill_no, "uuids": uuids}
    combined_string = json.dumps(data)
    print(f"QR DATA : \n{combined_string}")
    encoded_data = base64.b64encode(combined_string.encode()).decode()
    img_data = generate_qr_code(encoded_data, logo_path, dotted_style=True)
    return img_data

def generate_qr_code(encoded_data,dotted_style, logo_path=logo_path , version=5, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_H,
                     border=4, fill_color="black", back_color="white" ,grn_no=None, size=None):
    print(f"FUNCTION SIZE : {size}")
    logo = Image.open(logo_path)
    print(encoded_data)
    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(encoded_data)
    qr.make(fit=True)
    if dotted_style:
        qr_img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=CircleModuleDrawer()
        )
        logo = logo.convert("L")
    else:
        qr_img = qr.make_image(fill_color=fill_color, back_color=back_color)
    logo = logo.resize((qr_img.size[0] // 3, qr_img.size[1] // 3))
    pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
    qr_img.paste(logo, pos)
    if size:
        size = int(size)
        qr_img = qr_img.resize((size, size))

    img_data = BytesIO()
    qr_img.save(img_data, format="PNG")
    return img_data





def single_qr(uuid, logo=True, dotted_style=True, grn_no=None, size=None):
    print(f"QR SIZE : {size}")
    if dotted_style:
        img_data = generate_qr_code(uuid, dotted_style=True)
    elif grn_no:
        img_data = generate_qr_code(uuid, dotted_style=False, grn_no=grn_no)
    elif size is not None:
        print(f"SINGLE_QR SIZE : {size}")
        img_data = generate_qr_code(uuid, dotted_style=False, grn_no=grn_no, size=size)
    else:
        img_data = generate_qr_code(uuid, dotted_style=False)
    img_data.seek(0)
    img_bytes = img_data.read()
    return img_bytes

def generate_qr_code_grn(encoded_data,grn_no, logo_path, dotted_style, version=1, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_H,
                     border=4, fill_color="black", back_color="white", size=None):
    grn_suffix = str(grn_no)[-6:]
    print(grn_suffix)
    encoded_data_with_grn = encoded_data 
    print(f"FUNCTION SIZE : {size}")
    print(f"encoded_data_with_grn : {encoded_data_with_grn}")
    logo = Image.open(logo_path)
    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(encoded_data_with_grn)
    qr.make(fit=True)
    if dotted_style:
        qr_img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=CircleModuleDrawer()
        )
        logo = logo.convert("L")
    else:
        qr_img = qr.make_image(fill_color=fill_color, back_color=back_color)
    logo = logo.resize((qr_img.size[0] // 3, qr_img.size[1] // 3))
    pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
    qr_img.paste(logo, pos)

    # Add GRN suffix text below the QR code
    draw = ImageDraw.Draw(qr_img)
    font = ImageFont.truetype("UbuntuMono-B.ttf", 40)  # You may need to change the font and size
    suffix_text = f"GRN :- {grn_suffix}"
    bbox = draw.textbbox((0, 0), suffix_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_margin = 14  # Adjust the space between text and QR code bottom border
    text_position = ((qr_img.size[0] - text_width) // 2, qr_img.size[1] - text_height - text_margin)
    draw.text(text_position, suffix_text, fill=fill_color, font=font)

    if size:
        size = int(size)
        qr_img = qr_img.resize((size, size))

    # Save the image to the specified directory
    save_path = os.path.join(MEDIA_ROOT, 'qr_code.png')
    qr_img.save(save_path)


    # Return the image data if needed
    img_data = BytesIO()
    qr_img.save(img_data, format="PNG")
    return img_data


def single_qr_grn(uuid, logo=True, dotted_style=True, grn_no=None, size=None):
    print(f"QR SIZE : {size}")
    if dotted_style:
        img_data = generate_qr_code(uuid, logo_path, dotted_style=True, grn_no=grn_no)
    elif grn_no:
        img_data = generate_qr_code(uuid, logo_path, dotted_style=False, grn_no=grn_no)
    elif size is not None:
        print(f"SINGLE_QR SIZE : {size}")
        img_data = generate_qr_code(uuid, logo_path, dotted_style=False, grn_no=grn_no, size=size)
    else:
        img_data = generate_qr_code(uuid, logo_path, dotted_style=False, grn_no=grn_no)
    img_data.seek(0)
    img_bytes = img_data.read()
    return img_bytes


def single_qr_main(uuid,grn_no,logo=True,dotted_style=True,size=None):
    print(f"SINGLE_QR SIZE : {size}")
    img_data = generate_qr_code_grn(uuid,grn_no, logo_path, dotted_style=False, size=size)
    img_data.seek(0)
    img_bytes = img_data.read()
    return img_bytes





