from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .viewsets import OrderViewSet


router = DefaultRouter()

router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = router.urls
