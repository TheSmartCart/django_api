from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Order, OrderItem
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    OrderPatchSerializer,
    StatusUpdateSerializer,
    OrderItemSerializer,
)
from stores.models import Product, Store

ALLOWED_TRANSITIONS = {
    'pending':        ['in_preparation', 'ready', 'cancelled'],
    'in_preparation': ['ready', 'cancelled'],
    'ready':          ['collected', 'cancelled'],
    'collected':      [],
    'cancelled':      ['pending'],
}


class OrderViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'update', 'partial_update'):
            return OrderDetailSerializer
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderListSerializer

    def update(self, request, *args, **kwargs):
        return Response(
            {"error": "PUT method not supported. Use PATCH."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()

        if order.status != 'pending':
            return Response(
                {"error": f"Only orders in 'pending' status can be modified. Current status: '{order.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OrderPatchSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if 'status' in data:
            new_status = data['status']
            possible_transitions = ALLOWED_TRANSITIONS.get(order.status, [])
            if new_status not in possible_transitions:
                return Response(
                    {
                        "error": (
                            f"Transition from '{order.status}' to '{new_status}' is not allowed. "
                            f"Possible transitions: {possible_transitions or 'none'}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            order.status = new_status

        if 'items' in data:
            order.items.all().delete()
            self._create_items(order, data['items'])

        order.save()

        out = OrderDetailSerializer(order, context={'request': request})
        return Response(out.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        store = get_object_or_404(Store, pk=data['store'])

        new_status = data.get('status', 'pending')

        existing_order = Order.objects.filter(
            user=request.user,
            store=store,
            status='pending',
        ).first()

        if existing_order:
            existing_order.status = new_status
            existing_order.save()
            existing_order.items.all().delete()
            self._create_items(existing_order, data['items'])

            out = OrderDetailSerializer(existing_order, context={'request': request})
            return Response(out.data, status=status.HTTP_200_OK)
        else:
            if new_status != 'pending':
                return Response(
                    {"error": "No pending order to modify. An order cannot be created directly with this status."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            last_order = Order.objects.filter(
                user=request.user,
                store=store
            ).order_by('-created_at').first()

            if last_order and last_order.status in ['in_preparation', 'ready']:
                if len(data['items']) == last_order.items.count():
                    out = OrderDetailSerializer(last_order, context={'request': request})
                    return Response(out.data, status=status.HTTP_200_OK)

            order = Order.objects.create(
                user=request.user,
                store=store,
                status='pending',
            )
            self._create_items(order, data['items'])

            out = OrderDetailSerializer(order, context={'request': request})
            return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='update_status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = StatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        current_status = order.status

        possible_transitions = ALLOWED_TRANSITIONS.get(current_status, [])
        if new_status not in possible_transitions:
            return Response(
                {
                    "error": (
                        f"Transition from '{current_status}' to '{new_status}' is not allowed. "
                        f"Possible transitions from '{current_status}': {possible_transitions or 'none'}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status
        order.save()

        out = OrderDetailSerializer(order, context={'request': request})
        return Response(out.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'pending_store/(?P<store_id>\d+)')
    def pending_by_store(self, request, store_id=None):
        order = Order.objects.filter(
            user=request.user,
            store_id=store_id,
            status='pending'
        ).first()

        if not order:
            return Response({"error": "No pending order found for this store."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()

        if order.status == 'collected':
            return Response(
                {"error": "A collected order cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.status == 'cancelled':
            return Response(
                {"error": "This order is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = 'cancelled'
        order.save()

        return Response(
            {"message": "Order successfully cancelled."},
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _create_items(order, items_data):
        store = order.store

        for item_data in items_data:
            identifier = str(item_data['product'])

            product = None

            if identifier.isdigit():
                product = Product.objects.filter(
                    id=int(identifier),
                    stores=store
                ).first()

            if not product:
                product = get_object_or_404(
                    Product,
                    name=identifier,
                    stores=store
                )

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                unit_price=product.price,
            )


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    
    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        serializer.save(unit_price=product.price)