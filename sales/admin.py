from django.contrib import admin
from .models import SalesHeader, SalesDetail, Receipt, CashSession, SalesPayment

@admin.register(CashSession)
class CashSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user_client', 'opened_by', 'status', 'opening_float', 'closing_total', 'opened_at', 'closed_at']
    list_filter = ['status', 'opened_at']
    search_fields = ['session_id']

@admin.register(SalesPayment)
class SalesPaymentAdmin(admin.ModelAdmin):
    list_display = ['sales_payment_id', 'sales_header', 'method', 'amount', 'session', 'created_at']
    list_filter = ['method', 'created_at']
    search_fields = ['sales_payment_id', 'reference']
