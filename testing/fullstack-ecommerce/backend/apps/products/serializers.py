"""Product API serializers."""

from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductReview


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories."""

    children = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(
        source='products.count',
        read_only=True
    )

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'parent', 'description',
            'image', 'is_active', 'children', 'product_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(
                obj.children.filter(is_active=True),
                many=True
            ).data
        return []


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'position']


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for product reviews."""

    user_name = serializers.CharField(
        source='user.get_full_name',
        read_only=True
    )

    class Meta:
        model = ProductReview
        fields = [
            'id', 'user', 'user_name', 'rating', 'title',
            'comment', 'is_verified_purchase', 'created_at'
        ]
        read_only_fields = ['user', 'is_verified_purchase', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings."""

    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'category_name',
            'price', 'compare_at_price', 'is_on_sale',
            'discount_percentage', 'primary_image',
            'average_rating', 'is_featured'
        ]

    def get_primary_image(self, obj):
        image = obj.images.first()
        if image:
            return ProductImageSerializer(image).data
        return None

    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(
                models.Avg('rating')
            )['rating__avg'], 1)
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product view."""

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(
        many=True,
        read_only=True,
        source='reviews.approved'
    )
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(
        source='reviews.approved.count',
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'category', 'category_id',
            'description', 'price', 'compare_at_price', 'is_on_sale',
            'discount_percentage', 'stock_quantity', 'weight',
            'is_active', 'is_featured', 'images', 'reviews',
            'average_rating', 'review_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        return ProductListSerializer().get_average_rating(obj)

    def validate_price(self, value):
        """Ensure price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate(self, data):
        """Cross-field validation."""
        if 'compare_at_price' in data and 'price' in data:
            if data['compare_at_price'] and data['compare_at_price'] <= data['price']:
                raise serializers.ValidationError(
                    "Compare at price must be greater than selling price."
                )
        return data
