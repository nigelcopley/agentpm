"""Product API views."""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg

from .models import Category, Product, ProductReview
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductReviewSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for product categories."""

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Get all products in category."""
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            is_active=True
        )
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for products with search and filtering."""

    queryset = Product.objects.filter(is_active=True).select_related(
        'category'
    ).prefetch_related('images', 'reviews')
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'name']
    lookup_field = 'slug'

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        """Apply dynamic filters from query params."""
        queryset = super().get_queryset()

        # Price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # On sale filter
        on_sale = self.request.query_params.get('on_sale')
        if on_sale == 'true':
            queryset = queryset.filter(
                compare_at_price__isnull=False,
                compare_at_price__gt=models.F('price')
            )

        # In stock filter
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)

        return queryset

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        """Get all approved reviews for a product."""
        product = self.get_object()
        reviews = product.reviews.filter(is_approved=True)
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_review(self, request, slug=None):
        """Add a review for a product."""
        product = self.get_object()
        serializer = ProductReviewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                product=product,
                user=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products."""
        products = self.get_queryset().filter(is_featured=True)[:10]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced product search."""
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'Search query required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        products = self.get_queryset().filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

        serializer = ProductListSerializer(products, many=True)
        return Response({
            'query': query,
            'count': products.count(),
            'results': serializer.data
        })
