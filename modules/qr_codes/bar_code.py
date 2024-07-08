import uuid
from barcode import Code128
from barcode.writer import ImageWriter
from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage
import os

def generate_barcode(uuid_str_list, excel_filename, image_folder):
    wb = Workbook()
    ws = wb.active

    for uuid_str in uuid_str_list:
        barcode = Code128(uuid_str, writer=ImageWriter())
        barcode_path = os.path.join(image_folder, f"{uuid_str}.png")
        barcode.save(barcode_path)
        img = ExcelImage(barcode_path)
        ws.add_image(img, f"A{uuid_str_list.index(uuid_str) + 2}")  # +2 to leave space for header
    
    excel_path = os.path.join(image_folder, excel_filename)
    wb.save(excel_path)
    print(f'All barcodes created and saved to "{excel_path}"')

if __name__ == "__main__":
    uuid_str_list = []
    for i in range(1, 11):
        uuid_str = str(uuid.uuid4()).replace("-", "")
        uuid_str_list.append(uuid_str)
    
    excel_filename = "barcodes.xlsx"
    image_folder = "barcode_images"
    os.makedirs(image_folder, exist_ok=True)  # Create the image folder if it doesn't exist
    generate_barcode(uuid_str_list, excel_filename, image_folder)
