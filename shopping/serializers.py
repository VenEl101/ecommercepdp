from rest_framework import serializers
from .models import Product, ProductCategory, ProductItem, Cart, CartItem, OrderItem, Order, ShippingAddress, PromoCode, Favorite, PaymentCard
from accounts.models import User


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('name', 'description', 'quantity')





class ProductListSerializer(serializers.ModelSerializer):
    category = ProductCategory()
    
    class Meta:
        model = Product
        fields = ('id', 'category', 'name', 'description', 'base_price')
    


class ProductVariantSerializer(serializers.ModelSerializer):
    color = serializers.StringRelatedField()
    size = serializers.StringRelatedField()
    product = serializers.StringRelatedField()

    class Meta:
        model = ProductItem
        fields = ('id', 'product', 'sku', 'current_price', 'original_price', 'color', 'size', 'stock_quantity', 'is_available')


class ProductDetailSerializer(ProductListSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    in_stock = serializers.BooleanField(source='has_stock', read_only=True)
    
    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + (
            'description', 'variants', 'in_stock', 'updated_at'
        )



class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'



    


class PromoCodeSerializers(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    product = serializers.StringRelatedField()
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'prod_quant', 'subtotal')

    def get_subtotal(self, obj):
        return obj.subtotal
    

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    bagtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    shipping_cost = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'subtotal', 'shipping_cost', 'bagtotal')

    def get_shipping_cost(self, obj):
        return obj.shipping.shipping_cost




class OrderItemSerializer(serializers.ModelSerializer):
    product_items = ProductVariantSerializer()
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_items', 'quantity', 'price_at_purchase', 'subtotal']
    
    def get_subtotal(self, obj):
        return obj.subtotal


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping = ShippingAddressSerializer()
    
    class Meta:
        model = Order
        fields = [
            'id', 'shipping', 'items', 'promo_code', 'total_price',
            
        ]
    
    def get_subtotal(self, obj):
        return obj.subtotal
    
    def get_discount_amount(self, obj):
        return obj.discount_amount
    


class AddItemSerializer(serializers.Serializer):

    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        if not ProductItem.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist")
        return value


class ReduceItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists:
            raise serializers.ValidationError('Product does not exits')
        return value
    

# class RemoveItemSerializer(serializers.Serializer):
#     product_id = serializers.IntegerField()
    

#     def validate(self, value):
#         if

class FavouriteSerializer(serializers.ModelSerializer):
    
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'product', 'created_at')

    


class UserInfoSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'profile_picture')



class CardDetailSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = PaymentCard
        fields = ['id', 'user', 'last_four', 'brand', 'exp_month', 'exp_year', 'is_default']
        read_only_fields = ['user', 'created_at']
    



    



