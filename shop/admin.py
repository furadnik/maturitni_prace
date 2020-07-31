from django.contrib import admin
from .models import Item, Review, Address, Order, OrderStack, Category

# Register your models here.
admin.site.register(Item)
admin.site.register(Review)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderStack)
admin.site.register(Category)