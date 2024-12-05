# import json
# import requests
# import schedule
# import time
# from uuid import uuid4
# from django.http import JsonResponse
# from inlet.models import Product, ProductIndex, ProductIndexItem
# from django.views.decorators.csrf import csrf_exempt
# from datetime import datetime

# @csrf_exempt
# def parse_and_store_product_data(data):
#     try:
#         print(data)
#         for item in data:
#             time.sleep(2)
#             if ProductIndex.objects.filter(grn_no=item.get('GrnNo')).exists():
#                 GRN_NO = item.get('GrnNo')
#                 # print(f'[API] Grn ALready Exist Skip : GRN_NO {GRN_NO}')
#             else:

#                 product_index = ProductIndex.objects.create(
#                     supplier_name=item.get('PartyName'),
#                     supplier_gstin=item.get('SupplierGstin'),
#                     gate_inward_No=item.get('GateInwardNo'),
#                     party_name=item.get('PartyName'),
#                     status='unverified',
#                     grn_no=item.get('GrnNo'),
#                     grn_date=datetime.strptime(item.get('GrnDate'), '%d/%m/%Y').date(),
#                     po_no=item.get('PoNo'),
#                     po_date=datetime.strptime(item.get('PoDate'), '%d/%m/%Y').date(),
#                     SubGlAcNo=item.get('SubGlAcNo'),
#                     party_challan_no=item.get('PartyChallanNo'),
#                     party_challan_date=item.get('PartyChallanDate'),
#                     batch_id=uuid4(),
#                 )

#                 for product_item in item['ItemSummary']:
#                     material_code = product_item['MaterialCode']
#                     m_name = product_item['MaterialName']
#                     product, created = Product.objects.get_or_create(
#                         product_id=product_item['MaterialName'],
#                         MaterialCode=str(material_code),
#                         defaults={'name': product_item['MaterialName']}
#                     )
#                     if created:
#                         print(f"[API] Product Created : {m_name}")

#                     # Create ProductIndexItem associated with the existing ProductIndex
#                     product_index_item = ProductIndexItem.objects.create(
#                         UOM=product_item['MaterialUom'],
#                         product_index=product_index,
#                         product=product,
#                         quantity_requested=product_item['ChallanQty'],
#                         quantity_received=product_item['ReceivedQty']
#                     )
#                     time.sleep(0.5)

#         print('[API] : Product Index data parsed and stored successfully')
#     except Exception as e:
#         print(f"GRN API ERROR : {e}")

# # def schedule_parsing(data):
# #     print("GRN API CALL: TIME")
# #     schedule.every(5).seconds.do(parse_and_store_product_data, data)

# #     while True:
# #         schedule.run_pending()
# #         time.sleep(1)

# # Start the scheduling function in a separate thread or process
# # import threading
# # t = threading.Thread(target=schedule_parsing)
# # t.start()


import json
import requests
import schedule
import time
from uuid import uuid4
from django.http import JsonResponse
from inlet.models import Product, ProductIndex, ProductIndexItem
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


@csrf_exempt
def parse_and_store_product_data(data, logger):
    try:
        logger.info("[API] Starting parsing and storing product data...")
        for item in data:
            logger.info(f"[API] Processing item: {item}")
            grn_no = item.get('GrnNo')
            if ProductIndex.objects.filter(grn_no=grn_no).exists():
                logger.info(f'[API] GRN {grn_no} already exists. Skipping...')
            else:
                product_index = create_product_index(item, logger)
                logger.info(f'[API] Created product index: {product_index}')
                for product_item in item['ItemSummary']:
                    create_product_index_item(
                        product_index, product_item, logger)
                logger.info('[API] Call Complete')
        logger.info('[API] GRN data parsed and stored successfully')
    except Exception as e:
        logger.error(
            f"[API] Error while parsing and storing product data: {e}")


def create_product_index(item, logger):
    return ProductIndex.objects.create(
        supplier_name=item.get('PartyName'),
        compny_name=item.get('CompanyShortName'),
        supplier_gstin=item.get('SupplierGstin'),
        gate_inward_No=item.get('GateInwardNo'),
        party_name=item.get('PartyName'),
        status='unverified',
        grn_no=item.get('GrnNo'),
        grn_date=datetime.strptime(item.get('GrnDate'), '%d/%m/%Y').date(),
        po_no=item.get('PoNo'),
        po_date=datetime.strptime(item.get('PoDate'), '%d/%m/%Y').date(),
        SubGlAcNo=item.get('SubGlAcNo'),
        party_challan_no=item.get('PartyChallanNo'),
        party_challan_date=item.get('PartyChallanDate'),
        batch_id=uuid4(),
    )


def create_product_index_item(product_index, product_item, logger):
    material_code = product_item['MaterialCode']
    material_name = product_item['MaterialName']
    material_UOM = product_item['MaterialUom']
    print(material_UOM, material_code)
    is_insert = False

    if product_item.get('StockGroupType') == 102:
        is_insert = True
    if material_code == 0 or not material_code:
        logger.info(f"[API] Wrong Material Code  : {material_code}")
        log_to_file(f"Wrong Material Code  : {material_code}")
    else:
        try:
            # product, created = Product.objects.get_or_create(
            #     product_id=product_item['MaterialName'],
            #     name=product_item['MaterialName'],
            #     # material_UOM=material_UOM,
            #     MaterialCode=str(material_code),
            #     defaults={
            #         'name': product_item['MaterialName'], 'is_insert': is_insert}
            # )
            product = Product.objects.filter(
                MaterialCode=product_item['MaterialCode']).first()
            created = False
            if product == None:
                product = Product.objects.create(
                    product_id=product_item['MaterialName'],
                    name=product_item['MaterialName'],
                    material_UOM=material_UOM,
                    MaterialCode=material_code,
                    is_insert=is_insert
                )
                created = True
                print(product.material_UOM)
            else : 
                product.is_insert = is_insert
                product.save()
            if created:
                logger.info(f"[API] Product Created : {material_name}")
            else:
                logger.info(f"[API] Product already exists: {material_name}")
            print(product.material_UOM)
            product.material_UOM = material_UOM
            product.save()
            print(product.material_UOM)
            if material_UOM == "NOS":
                try:
                    ProductIndexItem.objects.create(
                        UOM=product_item['MaterialUom'],
                        product_index=product_index,
                        product=product,
                        quantity_requested=product_item['ChallanQty'],
                        quantity_received=product_item['ReceivedQty'],
                        recived_weight=0.0,
                        requested_weight=0.0
                    )
                except Exception as e:
                    print(f"[API] Error creating ProductIndexItem: {e}")
            else:
                try:
                    ProductIndexItem.objects.create(
                        UOM=product_item['MaterialUom'],
                        product_index=product_index,
                        product=product,
                        quantity_requested=1,
                        quantity_received=1,
                        requested_weight=product_item['ChallanQty'],
                        recived_weight=product_item['ReceivedQty']
                    )
                except Exception as e:
                    print(f"[API] Error creating ProductIndexItem: {e}")
        except Exception as e:
            print(f"[API] Error creating ProductIndexItem: {e}")
            logger.error(f"[API] Error creating ProductIndexItem: {e}")


def log_to_file(message):
    with open("material_code_errors.txt", "a") as file:
        file.write(message + "\n")
