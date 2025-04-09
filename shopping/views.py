from django.shortcuts import render
from rest_framework import viewsets, generics, status
from django.db import transaction
from rest_framework.permissions import IsAuthenticated

from .models import Product, ProductItem, Cart, CartItem, Order, OrderItem, Favorite, ShippingAddress, PaymentCard, ProductCategory
from accounts.models import User
from .serializers import CartSerializer, OrderSerializer, ProductListSerializer, ProductDetailSerializer, AddItemSerializer, FavouriteSerializer, ShippingAddressSerializer, UserInfoSerializer, CardDetailSerializer, ReduceItemSerializer, ProductCategorySerializer
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework import filters
from rest_framework.views import APIView


class ProductsView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]



class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'id'


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductCategorySerializer

    def get_queryset(self):
        return ProductCategory.objects.all()



class CategoryProductsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductListSerializer


    category = 1

    def get_queryset(self):   
        return Product.objects.filter(category=self.category)


class ClothesCategory(CategoryProductsViewSet):
    category_id = 1



class CartViewSet(viewsets.ModelViewSet):
    
    serializer_class = CartSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    


    @action(detail=True, methods=['post'], url_path='add-item')
    def add_item(self, request, pk=None):
        cart = self.get_object()
        serializer = AddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                product_id = serializer.validated_data['product_id']
                quantity = serializer.validated_data['quantity']

                
                product = ProductItem.objects.get(id=product_id)
                
                if quantity <= 0:
                    raise ValidationError({"quantity": "Must be positive number"})

                if product.stock_quantity < quantity:
                    raise ValidationError(
                        {"stock": f"Only {product.stock_quantity} available"},
                        code=status.HTTP_400_BAD_REQUEST
                    )

                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'prod_quant': quantity}
                )

                if not created:
                    cart_item.prod_quant += quantity
                    cart_item.save()

                product.stock_quantity -= quantity
                product.save()

                return Response({
                    "status": "success",
                    "data": {
                        "item_id": cart_item.id,
                        "quantity": cart_item.prod_quant,
                        "subtotal": cart_item.subtotal,
                        "cart_total": cart.bagtotal
                    }
                }, status=status.HTTP_200_OK)

        except ProductItem.DoesNotExist:
            raise NotFound(detail="Product not found")

    @action(detail=True, methods=['post'], url_path='remove-item')
    def reduce_item(self, request, pk=None):
        cart = self.get_object()
        serializer = ReduceItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                product_id = serializer.validated_data['product_id']
                quantity = serializer.validated_data['quantity']

                if quantity <= 0:
                    raise ValidationError({"quantity": "Must be positive number"})

               
                product = ProductItem.objects.get(id=product_id)
                cart_item = CartItem.objects.get(
                    cart=cart, 
                    product=product
                )

                if quantity > cart_item.prod_quant:
                    quantity = cart_item.prod_quant  

                
                cart_item.prod_quant -= quantity
                if cart_item.prod_quant <= 0:
                    cart_item.delete()
                else:
                    cart_item.save()

                
                product.stock_quantity += quantity
                product.save()

                return Response({
                    "status": "success",
                    "data": {
                        "removed_quantity": quantity,
                        "remaining_quantity": max(0, cart_item.prod_quant) if cart_item.prod_quant > 0 else 0,
                        "cart_total": cart.bagtotal
                    }
                }, status=status.HTTP_200_OK)

        except (ProductItem.DoesNotExist, CartItem.DoesNotExist):
            raise NotFound(detail="Product not found in cart")
        except Exception as e:
            raise ValidationError(detail=str(e))

        
    
        
    
    
    @action(detail=True, methods=['get', 'post'])
    def checkout(self, request, pk=None):
        cart = self.get_object()
    
        if not cart.items.exists():
            return Response(
                {'detail': 'Your cart is empty'},
                status=400 
            )

        try:
        
            with transaction.atomic():
            
                order = Order.objects.create(
                    user=request.user,
                    shipping=cart.shipping,
                    promo_code=cart.promo_code,
                    status='P',
                    shipping_cost=cart.shipping_cost,
                    total_price=cart.bagtotal
                )

            
                order_items = []
                for cart_item in cart.items.all():
                
                    if cart_item.product.stock_quantity < cart_item.prod_quant:
                        raise Exception(f"Not enough stock for {cart_item.product.name}")
                
                    order_item = OrderItem.objects.create(
                        order=order,
                        product_items=cart_item.product,
                        quantity=cart_item.prod_quant,
                        price_at_purchase=cart_item.product.current_price,
                    )
                    order_items.append(order_item)
                
                
                    cart_item.product.stock_quantity -= cart_item.prod_quant
                    cart_item.product.save()

            
                cart.items.all().delete()

                serializer = OrderSerializer(order)

                return Response(
                    {
                        "success": True,
                        "order": serializer.data,
                        "message": "Order successfully created!"
                    },
                    status=201  
                )
            
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "detail": f"An error occurred during checkout: {str(e)}"
                },
                status=400  
            )
        
    







class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = OrderSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


    



class FavoritesViewSet(viewsets.ModelViewSet):
    serializer_class = FavouriteSerializer


    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    


class ShippingViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingAddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    

    



class PersonalDetailViewSet(viewsets.ModelViewSet):
    serializer_class = UserInfoSerializer


    def get_queryset(self):
        return User.objects.filter(email=self.request.user)
    




class CardDetailViewSet(viewsets.ModelViewSet):

    serializer_class = CardDetailSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return PaymentCard.objects.filter(user=self.request.user)

    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



# class PaymentView(APIView):
#     def post(self, request)

