from django.contrib import admin

from .models import TransferRequest, Order, Order_Item, OrderStatusTimestamp

# Register your models here.
admin.site.register(TransferRequest)
admin.site.register(Order)
admin.site.register(Order_Item)
admin.site.register(OrderStatusTimestamp)