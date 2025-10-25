"""Pytest configuration and fixtures."""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product
from apps.orders.models import Order, Cart

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(
        name="Electronics",
        description="Electronic devices"
    )


@pytest.fixture
def product_factory(db, category):
    """Factory for creating test products."""
    def create_product(**kwargs):
        defaults = {
            'name': 'Test Product',
            'sku': 'TEST-001',
            'category': category,
            'description': 'Test product description',
            'price': Decimal('99.99'),
            'stock_quantity': 100,
            'weight': Decimal('1.0')
        }
        defaults.update(kwargs)
        return Product.objects.create(**defaults)
    return create_product


@pytest.fixture
def product(product_factory):
    """Create a single test product."""
    return product_factory()


@pytest.fixture
def cart_factory(db, user):
    """Factory for creating test carts."""
    def create_cart(**kwargs):
        defaults = {'user': user}
        defaults.update(kwargs)
        return Cart.objects.create(**defaults)
    return create_cart


@pytest.fixture
def order_factory(db, user):
    """Factory for creating test orders."""
    def create_order(**kwargs):
        defaults = {
            'user': user,
            'subtotal': Decimal('100.00'),
            'tax': Decimal('10.00'),
            'shipping_cost': Decimal('5.00'),
            'total': Decimal('115.00'),
            'shipping_name': 'Test User',
            'shipping_address_line1': '123 Test St',
            'shipping_city': 'Test City',
            'shipping_state': 'TS',
            'shipping_postal_code': '12345',
            'shipping_country': 'US',
            'payment_method': 'stripe',
        }
        defaults.update(kwargs)
        return Order.objects.create(**defaults)
    return create_order


@pytest.fixture
def api_client():
    """Create a DRF API client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client
