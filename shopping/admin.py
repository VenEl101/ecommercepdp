from django.contrib import admin

from django.contrib import admin

from .models import * 

admin.site.register([Product, 
                     ProductItem, 
                     PromoCode, 
                     ShippingAddress, 
                     Cart, 
                     CartItem, 
                     Order, 
                     OrderItem, 
                     Payment, 
                     ProductCategory, 
                     Color, 
                     Size,
                     PaymentCard
                     
                     
                     ])
