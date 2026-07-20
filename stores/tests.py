from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from stores.models import Brand, Category, Product, Store

User = get_user_model()

class StoresAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

        self.brand = Brand.objects.create(name='Carrefour', status='active')
        self.store = Store.objects.create(
            name='Carrefour Market',
            address='123 Rue de Paris',
            postal_code='75001',
            city='Paris',
            brand=self.brand,
            status='active'
        )
        self.category = Category.objects.create(name='Grocery', status='active')
        self.category.stores.set([self.store])

        self.product = Product.objects.create(name='Pasta', price=1.50, category=self.category)
        self.product.stores.set([self.store])

    def test_list_brands(self):
        url = reverse('brand-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Carrefour')
        self.assertEqual(len(response.data[0]['stores']), 1)
        self.assertEqual(response.data[0]['stores'][0]['name'], 'Carrefour Market')

    def test_create_brand(self):
        url = reverse('brand-list')
        data = {'name': 'Auchan', 'status': 'active'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Brand.objects.filter(name='Auchan').count(), 1)

    def test_list_categories(self):
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_categories_by_store(self):
        other_brand = Brand.objects.create(name='Leclerc', status='active')
        other_store = Store.objects.create(
            name='Leclerc Centre',
            address='99 Rue Victor Hugo',
            postal_code='33000',
            city='Bordeaux',
            brand=other_brand,
            status='active'
        )
        other_cat = Category.objects.create(name='Bakery')
        other_cat.stores.set([other_store])

        url = reverse('category-list')
        response = self.client.get(f"{url}?store={self.store.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Grocery')

    def test_create_category(self):
        url = reverse('category-list')
        data = {
            'name': 'Fruits & Vegetables',
            'status': 'active'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name='Fruits & Vegetables').exists())

    def test_list_products(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_products(self):
        url = reverse('product-list')
        response = self.client.get(f"{url}?store={self.store.id}&category={self.category.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_product(self):
        url = reverse('product-list')
        data = {
            'name': 'Rice',
            'price': 2.30,
            'category': self.category.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name='Rice').exists())

    def test_list_stores(self):
        url = reverse('store-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_stores(self):
        url = reverse('store-list')
        response = self.client.get(f"{url}?brand={self.brand.id}&city=Paris&status=active")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_store(self):
        url = reverse('store-list')
        data = {
            'name': 'Carrefour Express',
            'address': '456 Rue de Lyon',
            'postal_code': '69002',
            'city': 'Lyon',
            'brand': self.brand.id,
            'status': 'active'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Store.objects.filter(name='Carrefour Express').exists())

    def test_filter_stores_by_postal_code(self):
        url = reverse('store-list')
        response = self.client.get(f"{url}?postal_code=75001")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Carrefour Market')


class StoresModelStrTestCase(TestCase):

    def setUp(self):
        self.brand = Brand.objects.create(name='Leclerc', status='active')
        self.store = Store.objects.create(
            name='Leclerc Lyon',
            address='1 Rue Victor Hugo',
            postal_code='69001',
            city='Lyon',
            brand=self.brand,
            status='active'
        )
        self.category = Category.objects.create(name='Dairy', status='active')
        self.product = Product.objects.create(name='Butter', price=1.80)

    def test_brand_str(self):
        self.assertEqual(str(self.brand), 'Leclerc')

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Butter')

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Dairy')

    def test_store_str(self):
        self.assertEqual(str(self.store), 'Leclerc Lyon - Lyon (Leclerc)')
