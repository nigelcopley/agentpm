"""Analytics and business intelligence models."""

from django.db import models
from django.utils import timezone


class ProductView(models.Model):
    """Track product page views for analytics."""

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='views'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.created_at}"


class SalesMetrics(models.Model):
    """Daily sales metrics aggregation."""

    date = models.DateField(unique=True, default=timezone.now)
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items_sold = models.IntegerField(default=0)
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    new_customers = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Sales metrics'

    def __str__(self):
        return f"Sales metrics for {self.date}"
