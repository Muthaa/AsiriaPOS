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
from products.views import ProductViewSet, UnitViewSet, CategoryViewSet, StockMovementViewSet, StockAdjustmentViewSet, StockAlertViewSet, LocationViewSet, ProductLocationStockViewSet, StockTransferViewSet
from registry.views import CustomerViewSet, SupplierViewSet, PaymentOptionViewSet, ExpenseCategoryViewSet, ExpenseViewSet, AnonymousIdentifyAPIView, AnonymousProfileViewSet
from sales.views import SalesHeaderViewSet, SalesDetailViewSet, ReceiptViewSet, CashSessionViewSet, SalesPaymentViewSet, SalesReturnViewSet, SalesRefundViewSet, SalesReservationViewSet
from purchases.views import (
    PurchaseHeaderViewSet, PurchaseDetailViewSet, PaymentViewSet,
    PurchaseOrderHeaderViewSet, PurchaseOrderDetailViewSet, GRNHeaderViewSet, GRNDetailViewSet,
    PurchaseOrderCreateAPIView, PurchaseOrderConvertAPIView, PurchaseGenerateGRNAPIView,
    PurchaseOrderRetrieveHeaderAPIView, PurchaseOrderRetrieveFullAPIView,
    PurchaseRetrieveHeaderAPIView, PurchaseRetrieveFullAPIView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from authentication.views import LoginView, CustomLogoutView, CustomTokenObtainPairView, CustomTokenRefreshView
from django.conf import settings

# from wagtail import urls as wagtail_urls
# from wagtail.admin import urls as wagtailadmin_urls
# from wagtail.documents import urls as wagtaildocs_urls

from sales_views.views import TodaysSalesTotalAPIView, CheckoutInitializeAPIView, ReceiptLinkAPIView, ReceiptLinkByTokenAPIView

class CustomSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.security = [{"Bearer": []}]
        schema.securityDefinitions = {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...\""
            }
        }
        return schema

router = DefaultRouter()
router.register(r'clients', UserClientViewSet, basename='clients')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'units', UnitViewSet, basename='units')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movements')
router.register(r'stock-adjustments', StockAdjustmentViewSet, basename='stock-adjustments')
router.register(r'stock-alerts', StockAlertViewSet, basename='stock-alerts')
router.register(r'locations', LocationViewSet, basename='locations')
router.register(r'location-stocks', ProductLocationStockViewSet, basename='location-stocks')
router.register(r'stock-transfers', StockTransferViewSet, basename='stock-transfers')
router.register(r'salesheaders', SalesHeaderViewSet, basename='salesheaders')
router.register(r'salesdetails', SalesDetailViewSet, basename='salesdetails')
router.register(r'receipts', ReceiptViewSet, basename='receipts')
router.register(r'cash-sessions', CashSessionViewSet, basename='cash-sessions')
router.register(r'sales-payments', SalesPaymentViewSet, basename='sales-payments')
router.register(r'sales-returns', SalesReturnViewSet, basename='sales-returns')
router.register(r'sales-refunds', SalesRefundViewSet, basename='sales-refunds')
router.register(r'sales-reservations', SalesReservationViewSet, basename='sales-reservations')
router.register(r'purchaseheaders', PurchaseHeaderViewSet, basename='purchaseheaders')
router.register(r'purchasedetails', PurchaseDetailViewSet, basename='purchasedetails')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'poheaders', PurchaseOrderHeaderViewSet, basename='poheaders')
router.register(r'podeltails', PurchaseOrderDetailViewSet, basename='podetails')
router.register(r'grnheaders', GRNHeaderViewSet, basename='grnheaders')
router.register(r'grndetails', GRNDetailViewSet, basename='grndetails')
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'suppliers', SupplierViewSet, basename='suppliers')
router.register(r'paymentsoptions', PaymentOptionViewSet, basename='paymentsoptions')
router.register(r'expensecategories', ExpenseCategoryViewSet, basename='expensecategories')
router.register(r'expenses', ExpenseViewSet, basename='expenses')
router.register(r'anonymousprofiles', AnonymousProfileViewSet, basename='anonymousprofiles')

# Swagger Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="AsiriaPOS API",
        default_version='v1',
        description="""API documentation for AsiriaPOS.""",
        terms_of_service="https://www.asiriatech.ke/terms/",
        contact=openapi.Contact(email="support@asiriatech.ke"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],
    generator_class=CustomSchemaGenerator,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # path('api/auth/', include('authentication.urls')),

    # JWT authentication endpoints (official login/logout for API)
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/logout/', CustomLogoutView.as_view(), name='token_logout'),
    path('api/sales/today/', TodaysSalesTotalAPIView.as_view(), name='todays-sales'),
    path('api/checkout/initialize/', CheckoutInitializeAPIView.as_view(), name='checkout-initialize'),
    path('api/receipt/link/', ReceiptLinkAPIView.as_view(), name='receipt-link'),
    path('api/receipt/link-token/', ReceiptLinkByTokenAPIView.as_view(), name='receipt-link-token'),
    # Purchases flow endpoints
    path('api/purchase-orders/create/', PurchaseOrderCreateAPIView.as_view(), name='po-create'),
    path('api/purchase-orders/<uuid:po_header_id>/convert-to-purchase/', PurchaseOrderConvertAPIView.as_view(), name='po-convert'),
    path('api/purchase-orders/<uuid:po_header_id>/header/', PurchaseOrderRetrieveHeaderAPIView.as_view(), name='po-get-header'),
    path('api/purchase-orders/<uuid:po_header_id>/full/', PurchaseOrderRetrieveFullAPIView.as_view(), name='po-get-full'),
    path('api/purchases/<uuid:purchase_header_id>/generate-grn/', PurchaseGenerateGRNAPIView.as_view(), name='purchase-generate-grn'),
    path('api/purchases/<uuid:purchase_header_id>/header/', PurchaseRetrieveHeaderAPIView.as_view(), name='purchase-get-header'),
    path('api/purchases/<uuid:purchase_header_id>/full/', PurchaseRetrieveFullAPIView.as_view(), name='purchase-get-full'),
    path('api/anonymousprofiles/<uuid:anonymous_id>/identify/', AnonymousIdentifyAPIView.as_view(), name='anonymous-identify'),
    
    # Swagger URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    

    # # Wagtail Urls
    # # path('/', include(wagtailadmin_urls)),
    # path('cms/', include(wagtailadmin_urls)),
    # path('documents/', include(wagtaildocs_urls)),
    # path('', include(wagtail_urls)),  # homepage + wagtail-managed pages

    # path('login/', LoginView.as_view(), name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    
]