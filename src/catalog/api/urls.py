from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .viewsets import CategoryViewSet, ProductViewSet


router = DefaultRouter()

router.register(r'products', ProductViewSet, basename='products')
router.register(r'categories', CategoryViewSet, basename='categories')

urlpatterns = router.urls
