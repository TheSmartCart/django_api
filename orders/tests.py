from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from stores.models import Brand, Product, Store
from orders.models import Order, OrderItem

User = get_user_model()

class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer1', password='password123')
        self.other_user = User.objects.create_user(username='buyer2', password='password123')

        self.client.force_authenticate(user=self.user)

        self.brand = Brand.objects.create(name='Monoprix', status='active')
        self.store = Store.objects.create(
            name='Monoprix Paris',
            address='10 Rue des Halles',
            postal_code='75001',
            city='Paris',
            brand=self.brand,
            status='active'
        )
        self.product_pasta = Product.objects.create(
            name='Pasta Coquillettes',
            price=1.20,
        )
        self.product_pasta.stores.set([self.store])

        self.product_sauce = Product.objects.create(
            name='Tomato Sauce',
            price=2.50,
        )
        self.product_sauce.stores.set([self.store])

    def test_list_orders_only_returns_own_orders(self):
        cmd_user = Order.objects.create(user=self.user, store=self.store, status='pending')
        cmd_other = Order.objects.create(user=self.other_user, store=self.store, status='pending')

        url = reverse('orders-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], cmd_user.id)

    def test_create_new_order_pending_success(self):
        url = reverse('orders-list')
        data = {
            'store': self.store.id,
            'status': 'pending',
            'items': [
                {'product': self.product_pasta.id, 'quantity': 3},
                {'product': self.product_sauce.id, 'quantity': 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(len(response.data['items']), 2)

        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.store, self.store)
        self.assertEqual(order.items.count(), 2)

        self.assertEqual(float(response.data['total_price']), 6.10)

    def test_create_order_modifies_existing_pending(self):
        existing_cmd = Order.objects.create(user=self.user, store=self.store, status='pending')
        OrderItem.objects.create(order=existing_cmd, product=self.product_pasta, quantity=10, unit_price=1.20)

        url = reverse('orders-list')
        data = {
            'store': self.store.id,
            'status': 'pending',
            'items': [
                {'product': self.product_sauce.id, 'quantity': 2}
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], existing_cmd.id)

        existing_cmd.refresh_from_db()
        self.assertEqual(existing_cmd.items.count(), 1)
        self.assertEqual(existing_cmd.items.first().product, self.product_sauce)
        self.assertEqual(existing_cmd.items.first().quantity, 2)

    def test_create_order_non_pending_no_existing_fails(self):
        url = reverse('orders-list')
        data = {
            'store': self.store.id,
            'status': 'in_preparation',
            'items': [
                {'product': self.product_pasta.id, 'quantity': 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_create_order_returns_existing_when_preparation_or_ready_with_same_items(self):
        existing_cmd = Order.objects.create(user=self.user, store=self.store, status='in_preparation')
        OrderItem.objects.create(order=existing_cmd, product=self.product_pasta, quantity=2, unit_price=1.20)

        url = reverse('orders-list')
        data = {
            'store': self.store.id,
            'status': 'pending',
            'items': [
                {'product': self.product_pasta.id, 'quantity': 2}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], existing_cmd.id)
        self.assertEqual(response.data['status'], 'in_preparation')

    def test_put_method_not_allowed(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='pending')
        url = reverse('orders-detail', kwargs={'pk': cmd.id})
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_order_only_allowed_for_pending(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='ready')
        url = reverse('orders-detail', kwargs={'pk': cmd.id})
        data = {'status': 'collected'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only orders in 'pending'", response.data['error'])

    def test_patch_order_invalid_transition_fails(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='pending')
        url = reverse('orders-detail', kwargs={'pk': cmd.id})
        data = {'status': 'collected'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Transition from', response.data['error'])

    def test_patch_order_valid_transition_and_items_recreated(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='pending')
        OrderItem.objects.create(order=cmd, product=self.product_pasta, quantity=1, unit_price=1.20)

        url = reverse('orders-detail', kwargs={'pk': cmd.id})
        data = {
            'status': 'in_preparation',
            'items': [
                {'product': self.product_sauce.id, 'quantity': 5}
            ]
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'in_preparation')
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['product']['id'], self.product_sauce.id)

        cmd.refresh_from_db()
        self.assertEqual(cmd.status, 'in_preparation')
        self.assertEqual(cmd.items.count(), 1)
        self.assertEqual(cmd.items.first().product, self.product_sauce)

    def test_update_status_success(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='pending')
        url = reverse('orders-update-status', kwargs={'pk': cmd.id})

        response = self.client.patch(url, {'status': 'in_preparation'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'in_preparation')

        cmd.refresh_from_db()
        self.assertEqual(cmd.status, 'in_preparation')

    def test_update_status_invalid_transition_fails(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='ready')
        url = reverse('orders-update-status', kwargs={'pk': cmd.id})

        response = self.client.patch(url, {'status': 'in_preparation'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Transition from', response.data['error'])

    def test_pending_by_store_success(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='pending')
        url = reverse('orders-pending-by-store', kwargs={'store_id': self.store.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], cmd.id)

    def test_pending_by_store_not_found(self):
        url = reverse('orders-pending-by-store', kwargs={'store_id': self.store.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_order_via_delete_success(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='pending')
        url = reverse('orders-detail', kwargs={'pk': cmd.id})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Order successfully cancelled.')

        cmd.refresh_from_db()
        self.assertEqual(cmd.status, 'cancelled')

    def test_cancel_already_cancelled_fails(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='cancelled')
        url = reverse('orders-detail', kwargs={'pk': cmd.id})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already cancelled', response.data['error'])

    def test_cancel_collected_fails(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='collected')
        url = reverse('orders-detail', kwargs={'pk': cmd.id})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('collected order cannot be cancelled', response.data['error'])

    def test_retrieve_order_uses_detail_serializer(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='pending')
        url = reverse('orders-detail', kwargs={'pk': cmd.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('updated_at', response.data)

    def test_create_item_by_name_not_found_returns_404(self):
        url = reverse('orders-list')
        data = {
            'store': self.store.id,
            'status': 'pending',
            'items': [
                {'product': 'Nonexistent Product', 'quantity': 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_item_viewset_perform_create(self):
        from orders.views import OrderItemViewSet
        from unittest.mock import MagicMock

        cmd = Order.objects.create(user=self.user, store=self.store, status='pending')

        viewset = OrderItemViewSet()
        mock_serializer = MagicMock()
        mock_serializer.validated_data = {
            'product': self.product_pasta,
            'quantity': 2,
            'order': cmd,
        }
        viewset.perform_create(mock_serializer)
        mock_serializer.save.assert_called_once_with(unit_price=self.product_pasta.price)


    def test_get_serializer_class_for_create(self):
        from orders.views import OrderViewSet
        from orders.serializers import OrderCreateSerializer
        viewset = OrderViewSet()
        viewset.action = 'create'
        self.assertEqual(viewset.get_serializer_class(), OrderCreateSerializer)


class OrdersModelStrTestCase(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='struser', password='pass123')
        from stores.models import Brand, Store, Product
        self.brand = Brand.objects.create(name='TestBrand', status='active')
        self.store = Store.objects.create(
            name='TestStore',
            address='1 Rue Test',
            postal_code='00000',
            city='TestCity',
            brand=self.brand,
            status='active'
        )
        self.product = Product.objects.create(name='TestProduct', price=9.99)
        self.product.stores.set([self.store])

    def test_order_str(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='pending')
        self.assertIn('struser', str(cmd))

    def test_order_item_str(self):
        cmd = Order.objects.create(user=self.user, store=self.store, status='pending')
        item = OrderItem.objects.create(order=cmd, product=self.product, quantity=3, unit_price=9.99)
        self.assertIn('TestProduct', str(item))
        self.assertIn('3', str(item))
