from django.contrib.auth.models import User
from django.test import TestCase

from apps.products.models import Category, Currency, Product


class StorefrontTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Currency.objects.create(code="USD", symbol="$", rate="1", is_default=True)
        category = Category.objects.create(name="Electronics", slug="electronics")
        cls.product = Product.objects.create(
            name="Test Widget",
            slug="test-widget",
            sku="SKU-TESTWIDGET",
            category=category,
            price="19.90",
            stock=10,
            is_active=True,
            is_featured=True,
        )

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Widget")

    def test_product_list_and_detail(self):
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Widget")

        response = self.client.get("/products/test-widget/")
        self.assertEqual(response.status_code, 200)

    def test_cart_and_checkout_flow(self):
        self.client.post(f"/cart/add/{self.product.id}/", {"quantity": 2})

        response = self.client.get("/cart/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Widget")

        response = self.client.post(
            "/orders/checkout/",
            {
                "full_name": "Test Buyer",
                "email": "buyer@example.com",
                "phone": "+1 555 0100",
                "country": "United States",
                "address": "123 Main St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "notes": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/orders/confirmation/"))

        # Stock was decremented.
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

    def test_register_and_order_history(self):
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "Str0ngPass!123",
                "password2": "Str0ngPass!123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="testuser").exists())

        response = self.client.get("/orders/history/")
        self.assertEqual(response.status_code, 200)
