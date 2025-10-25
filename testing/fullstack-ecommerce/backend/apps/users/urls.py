"""Users API URLs."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'profile', views.ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
