# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Master,ProductIndex



# @receiver(post_save, sender=ProductIndexItem)
# def update_product_index_status(sender, instance, created, **kwargs):
#     if not created:  # Only update if the instance is not newly created
#         product_index = instance.product_index
#         all_items_unactive_count_zero = product_index.productindexitem_set.filter(
#             unactive_count=0
#         ).count() == product_index.productindexitem_set.count()
#         product_index.is_complete = all_items_unactive_count_zero
#         if all_items_unactive_count_zero:
#             product_index.status = 'complete'
#         product_index.save()