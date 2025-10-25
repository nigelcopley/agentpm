"""Analytics API URLs."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'metrics', views.MetricsViewSet, basename='metrics')

urlpatterns = [
    path('', include(router.urls)),
]
