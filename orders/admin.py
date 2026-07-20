from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'store', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'store')
    search_fields = ('user__username', 'store__name')
    inlines = [OrderItemInline]
    readonly_fields = ['total_price']
    fieldsets = (
        (None, {
            'fields': ('user', 'store', 'status')
        }),
        ('Information', {
            'fields': ('created_at', 'updated_at', 'total_price')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'unit_price', 'total_price')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product__name')