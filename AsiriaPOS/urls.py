"""
URL configuration for AsiriaPOS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserClientViewSet
from products.views import ProductViewSet, UnitViewSet, CategoryViewSet
from registry.views import CustomerViewSet, SupplierViewSet, PaymentOptionViewSet, ExpenseCategoryViewSet, ExpenseViewSet
from sales.views import SalesHeaderViewSet, SalesDetailViewSet, ReceiptViewSet
from purchases.views import PurchaseHeaderViewSet, PurchaseDetailViewSet, PaymentViewSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from authentication.views import LoginView, LogoutView
from django.conf import settings


# Swagger Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="AsiriaPOS API",
        default_version='v1',
        description="API documentation for AsiriaPOS",
        terms_of_service="https://www.asiriatech.ke/terms/",
        contact=openapi.Contact(email="support@asiriatech.ke"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r'clients', UserClientViewSet, basename='clients')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'units', UnitViewSet, basename='units')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'salesheaders', SalesHeaderViewSet, basename='salesheaders')
router.register(r'salesdetails', SalesDetailViewSet, basename='salesdetails')
router.register(r'receipts', ReceiptViewSet, basename='receipts')
router.register(r'purchaseheaders', PurchaseHeaderViewSet, basename='purchaseheaders')
router.register(r'purchasedetails', PurchaseDetailViewSet, basename='purchasedetails')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'suppliers', SupplierViewSet, basename='suppliers')
router.register(r'paymentsoptions', PaymentOptionViewSet, basename='paymentsoptions')
router.register(r'expensecategories', ExpenseCategoryViewSet, basename='expensecategories')
router.register(r'expenses', ExpenseViewSet, basename='expenses')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # path('api/auth/', include('authentication.urls')),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Swagger URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]