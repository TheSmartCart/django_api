from django.db import models
from users.models import CustomUser
from stores.models import Product, Store

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_preparation', 'In preparation'),
        ('ready', 'Ready'),
        ('collected', 'Collected'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} - Order #{self.order.id}"
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity
    
    class Meta:
        verbose_name = "Order item"
        verbose_name_plural = "Order items"