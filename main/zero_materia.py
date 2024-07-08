
import os
import django
import main


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from inlet.models import Product

def search_products_with_material_code_zero():

    products = Product.objects.filter(MaterialCode=0)
    return products

if __name__ == "__main__":
    products_with_material_code_zero = search_products_with_material_code_zero()
    print("Products with MaterialCode 0:")
    print(products_with_material_code_zero.count())
    for product in products_with_material_code_zero:
        print(f"- {product.name}")
        try:
            product.delete()
        except Exception as e:
            print(e)
            break
        
