from django.contrib import admin
from .models import Category, Unit, Product, StockMovement, StockAdjustment, StockAlert

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_client', 'description']
    list_filter = ['user_client']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['unit_name', 'user_client', 'description']
    list_filter = ['user_client']
    search_fields = ['unit_name', 'description']
    ordering = ['unit_name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'stock', 'minQuantity', 'price', 'cost', 'stock_value', 'is_low_stock', 'is_out_of_stock']
    list_filter = ['user_client', 'category', 'unit']
    search_fields = ['name', 'sku', 'barcode', 'description']
    ordering = ['name']
    readonly_fields = ['product_id', 'sku', 'barcode', 'created_at', 'updated_at', 'is_low_stock', 'is_out_of_stock', 'stock_value']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_client', 'name', 'category', 'unit', 'description')
        }),
        ('Identification', {
            'fields': ('sku', 'barcode'),
            'classes': ('collapse',)
        }),
        ('Stock & Pricing', {
            'fields': ('stock', 'minQuantity', 'price', 'cost')
        }),
        ('System Information', {
            'fields': ('product_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'previous_stock', 'new_stock', 'reference_number', 'created_by', 'created_at']
    list_filter = ['user_client', 'movement_type', 'created_at']
    search_fields = ['product__name', 'reference_number', 'reason']
    ordering = ['-created_at']
    readonly_fields = ['movement_id', 'previous_stock', 'new_stock', 'created_at']
    
    fieldsets = (
        ('Movement Details', {
            'fields': ('user_client', 'product', 'movement_type', 'quantity')
        }),
        ('Stock Levels', {
            'fields': ('previous_stock', 'new_stock'),
            'classes': ('collapse',)
        }),
        ('Reference Information', {
            'fields': ('reference_number', 'reason')
        }),
        ('System Information', {
            'fields': ('movement_id', 'created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['product', 'adjustment_type', 'quantity_adjusted', 'is_approved', 'created_by', 'created_at']
    list_filter = ['user_client', 'adjustment_type', 'is_approved', 'created_at']
    search_fields = ['product__name', 'reference_number', 'reason']
    ordering = ['-created_at']
    readonly_fields = ['adjustment_id', 'created_at', 'approved_at', 'approved_by']
    
    fieldsets = (
        ('Adjustment Details', {
            'fields': ('user_client', 'product', 'adjustment_type', 'quantity_adjusted')
        }),
        ('Reason & Reference', {
            'fields': ('reason', 'reference_number')
        }),
        ('Approval Information', {
            'fields': ('is_approved', 'approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('adjustment_id', 'created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_adjustments']
    
    def approve_adjustments(self, request, queryset):
        """Approve selected stock adjustments"""
        approved_count = 0
        for adjustment in queryset.filter(is_approved=False):
            adjustment.approve(request.user)
            approved_count += 1
        
        self.message_user(request, f"Successfully approved {approved_count} stock adjustments.")
    approve_adjustments.short_description = "Approve selected stock adjustments"

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'alert_type', 'is_active', 'created_at', 'resolved_at']
    list_filter = ['user_client', 'alert_type', 'is_active', 'created_at']
    search_fields = ['product__name', 'message']
    ordering = ['-created_at']
    readonly_fields = ['alert_id', 'created_at', 'resolved_at', 'resolved_by']
    
    fieldsets = (
        ('Alert Details', {
            'fields': ('user_client', 'product', 'alert_type', 'message')
        }),
        ('Status Information', {
            'fields': ('is_active', 'resolved_by', 'resolved_at')
        }),
        ('System Information', {
            'fields': ('alert_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['resolve_alerts']
    
    def resolve_alerts(self, request, queryset):
        """Resolve selected stock alerts"""
        resolved_count = 0
        for alert in queryset.filter(is_active=True):
            alert.resolve(request.user)
            resolved_count += 1
        
        self.message_user(request, f"Successfully resolved {resolved_count} stock alerts.")
    resolve_alerts.short_description = "Resolve selected stock alerts"
