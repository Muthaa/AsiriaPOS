from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, UnitViewSet, ProductViewSet,
    StockMovementViewSet, StockAdjustmentViewSet, StockAlertViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'units', UnitViewSet)
router.register(r'products', ProductViewSet)
router.register(r'stock-movements', StockMovementViewSet)
router.register(r'stock-adjustments', StockAdjustmentViewSet)
router.register(r'stock-alerts', StockAlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
