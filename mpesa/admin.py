from django.contrib import admin
from .models import Mpesa_payment


@admin.register(Mpesa_payment)
class MpesaPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'phone_number', 
        'amount', 
        'status', 
        'account_reference', 
        'mpesa_receipt_number',
        'created_at'
    ]
    
    list_filter = [
        'status', 
        'created_at',
        'transaction_date'
    ]
    
    search_fields = [
        'phone_number', 
        'account_reference', 
        'mpesa_receipt_number',
        'checkout_request_id',
        'merchant_request_id'
    ]
    
    readonly_fields = [
        'checkout_request_id', 
        'merchant_request_id', 
        'mpesa_receipt_number',
        'transaction_date',
        'result_code',
        'result_desc',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'phone_number',
                'amount',
                'account_reference',
                'transaction_desc',
                'status'
            )
        }),
        ('M-Pesa Details', {
            'fields': (
                'checkout_request_id',
                'merchant_request_id',
                'mpesa_receipt_number',
                'transaction_date'
            )
        }),
        ('Result Information', {
            'fields': (
                'result_code',
                'result_desc'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            )
        }),
    )
    
    date_hierarchy = 'created_at'
    
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        # Prevent manual creation of payments through admin
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion only for superusers
        return request.user.is_superuser
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected payments as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} payment(s) marked as completed.')
    mark_as_completed.short_description = "Mark selected as completed"
    
    def mark_as_failed(self, request, queryset):
        """Mark selected payments as failed"""
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} payment(s) marked as failed.')
    mark_as_failed.short_description = "Mark selected as failed"