from django.db import models

from accounts.models import User


class ProductCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    quantity = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Product_Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Size(models.Model):
    SIZE_TYPES = (
        ('CL', 'Clothing'),
        ('SH', 'Shoes'),
        ('AC', 'Accessories'),
    )
    name = models.CharField(max_length=20)
    size_type = models.CharField(max_length=2, choices=SIZE_TYPES, default='CL')

    class Meta:
        unique_together = ('name', 'size_type')

    def __str__(self):
        return f"{self.name} ({self.get_size_type_display()})"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey('ProductCategory', on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class ProductItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=50, unique=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    color = models.ForeignKey('Color', on_delete=models.PROTECT, null=True, blank=True)
    size = models.ForeignKey('Size', on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.sku}"


class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_present = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='addresses')
    recipient_name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = 'Shipping Addresses'
        ordering = ['-is_default']

    def __str__(self):
        return f"{self.recipient_name}, {self.city}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping = models.ForeignKey(ShippingAddress, on_delete=models.PROTECT)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, blank=True, null=True)

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def bagtotal(self):
        return self.subtotal + self.shipping.shipping_cost

    @property
    def shipping_cost(self):
        return self.shipping.shipping_cost


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    prod_quant = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.prod_quant * self.product.current_price


class Payment(models.Model):
    STATUS = [
        ('PENDING', 'pending'),
        ('COMPLETED', 'completed'),
    ]

    TYPE = [
        ('CASH', 'cash'),
        ('CREDIT_CARD', 'credit_card')

    ]

    METHOD = [
        ('CREDIT_CARD', 'credit_card'),
        ('PAYME_CARD', 'payme_card'),
        ('PAYPAL_CARD', 'paypal_card'),

    ]

    order = models.OneToOneField("Order", on_delete=models.CASCADE, related_name="payment")

    type = models.CharField(max_length=30, choices=TYPE, default='credit_card')
    method = models.CharField(max_length=30, choices=METHOD, default='paypal_card')
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    last_four = models.CharField(max_length=16)
    exp_date = models.CharField(max_length=10)


class Order(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('S', 'Shipped'),
        ('D', 'Delivered'),
        ('X', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping = models.ForeignKey('ShippingAddress', on_delete=models.PROTECT)
    promo_code = models.ForeignKey('PromoCode', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P', blank=True, null=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_items = models.ForeignKey(ProductItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price_at_purchase

    def __str__(self):
        return f"{self.quantity} × {self.product_items.product.name}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user}'s favorite: {self.product}"


class PaymentCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_four = models.CharField(max_length=4)
    brand = models.CharField(max_length=20, blank=True)
    exp_date = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} ****{self.last_four}"
