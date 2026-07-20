from rest_framework import serializers
from .models import Order, OrderItem
from stores.models import Store, Product


class ProductOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image']


class StoreOrderSerializer(serializers.ModelSerializer):
    brand_name = serializers.ReadOnlyField(source='brand.name')

    class Meta:
        model = Store
        fields = ['id', 'name', 'brand_name', 'address', 'postal_code', 'city']


class OrderItemInputSerializer(serializers.Serializer):
    product = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductOrderSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


class OrderListSerializer(serializers.ModelSerializer):
    store = StoreOrderSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status', 'store', 'items', 'total_price']

class OrderDetailSerializer(serializers.ModelSerializer):
    store = StoreOrderSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'created_at', 'updated_at', 'status', 'store', 'items', 'total_price']


class OrderCreateSerializer(serializers.Serializer):
    store = serializers.IntegerField()
    items = OrderItemInputSerializer(many=True)
    status = serializers.ChoiceField(
        choices=['pending', 'in_preparation', 'ready', 'collected', 'cancelled'],
        default='pending'
    )


class StatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=['pending', 'in_preparation', 'ready', 'collected', 'cancelled']
    )


class OrderPatchSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True, required=False)
    status = serializers.ChoiceField(
        choices=['pending', 'in_preparation', 'ready', 'collected', 'cancelled'],
        required=False,
    )