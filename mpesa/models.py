from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField



class Mpesa_payment(models.Model):
    """
    M-Pesa Paybill payment linked to Order
    Replaces/enhances existing Payment model
    """
    # Link to existing Order model
    order = models.ForeignKey('application.Order', on_delete=models.CASCADE, related_name='mpesa_payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mpesa_payments')
    
    # Customer details
    phone_number = models.CharField(max_length=15, help_text="Customer's M-Pesa phone number (254XXXXXXXXX)")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Payment amount")
    
    # Account number for Paybill (Order ID based)
    account_reference = models.CharField(
        max_length=12, 
        help_text="Order number shown to customer (e.g., ORD-1234)"
    )
    transaction_desc = models.CharField(max_length=200, default="Order Payment", help_text="Transaction description")
    
    # M-Pesa transaction identifiers
    checkout_request_id = models.CharField(max_length=100, unique=True)
    merchant_request_id = models.CharField(max_length=100)
    mpesa_receipt_number = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="M-Pesa confirmation code (e.g., QGK123ABC4)"
    )
    
    # Transaction status and results
    transaction_date = models.DateTimeField(blank=True, null=True)
    result_code = models.CharField(max_length=10, blank=True, null=True)
    result_desc = models.TextField(blank=True, null=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    status = models.CharField(
        max_length=20, 
        default='pending',
        choices=STATUS_CHOICES
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'M-Pesa Payment'
        verbose_name_plural = 'M-Pesa Payments'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['mpesa_receipt_number']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"Order #{self.order.id} - {self.phone_number} - KES {self.amount} - {self.status}"
    
    @property
    def is_successful(self):
        """Check if payment was successful"""
        return self.status == 'completed' and self.mpesa_receipt_number is not None
    
    def update_order_status(self):
        """Update order status when payment is successful"""
        if self.is_successful:
            self.order.status = 'processing'
            self.order.save()
            
            # Update the old Payment model if it exists
            if hasattr(self.order, 'payment'):
                self.order.payment.status = 'completed'
                self.order.payment.transaction_id = self.mpesa_receipt_number
                self.order.payment.save()
