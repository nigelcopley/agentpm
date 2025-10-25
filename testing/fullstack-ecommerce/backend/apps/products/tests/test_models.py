"""Tests for product models."""

import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from apps.products.models import Category, Product, ProductImage


@pytest.mark.django_db
class TestCategoryModel:
    """Test Category model."""

    def test_category_creation(self):
        """Test creating a category."""
        category = Category.objects.create(
            name="Electronics",
            description="Electronic devices and accessories"
        )
        assert category.name == "Electronics"
        assert category.slug == "electronics"
        assert category.is_active is True

    def test_category_hierarchy(self):
        """Test parent-child category relationships."""
        parent = Category.objects.create(name="Electronics")
        child = Category.objects.create(
            name="Smartphones",
            parent=parent
        )

        assert child.parent == parent
        assert child in parent.children.all()

    def test_category_str_method(self):
        """Test category string representation."""
        category = Category.objects.create(name="Electronics")
        assert str(category) == "Electronics"


@pytest.mark.django_db
class TestProductModel:
    """Test Product model."""

    def test_product_creation(self, product_factory):
        """Test creating a product."""
        product = product_factory(
            name="iPhone 15",
            price=Decimal("999.99"),
            sku="IPHONE15-001"
        )
        assert product.name == "iPhone 15"
        assert product.slug == "iphone-15"
        assert product.price == Decimal("999.99")

    def test_product_on_sale(self, product_factory):
        """Test on sale property."""
        product = product_factory(
            price=Decimal("799.99"),
            compare_at_price=Decimal("999.99")
        )
        assert product.is_on_sale is True
        assert product.discount_percentage == 20

    def test_product_not_on_sale(self, product_factory):
        """Test product not on sale."""
        product = product_factory(price=Decimal("999.99"))
        assert product.is_on_sale is False
        assert product.discount_percentage == 0

    def test_product_validation(self, product_factory):
        """Test product price validation."""
        with pytest.raises(ValidationError):
            product = product_factory(price=Decimal("-10.00"))
            product.full_clean()


@pytest.mark.django_db
class TestProductImage:
    """Test ProductImage model."""

    def test_image_ordering(self, product_factory):
        """Test image position ordering."""
        product = product_factory()

        img1 = ProductImage.objects.create(
            product=product,
            image="test1.jpg",
            position=1
        )
        img2 = ProductImage.objects.create(
            product=product,
            image="test2.jpg",
            position=0
        )

        images = list(product.images.all())
        assert images[0] == img2  # position 0 comes first
        assert images[1] == img1  # position 1 comes second
