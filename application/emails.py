"""
EMAIL NOTIFICATIONS FOR ORDERS
Add this to application/views.py or create a new application/emails.py file
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer after order is created
    
    Args:
        order: Order instance
    """
    subject = f'Order Confirmation - Order #{order.id} - TechHub'
    
    # Email context
    context = {
        'order': order,
        'customer_name': f"{order.first_name} {order.last_name}",
        'order_items': order.items.all(),
        'total': order.get_total_cost(),
    }
    
    # Render HTML email
    html_message = render_to_string('emails/order confirmation.html', context)
    plain_message = strip_tags(html_message)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Order confirmation email sent to {order.email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


def send_payment_received_email(order, mpesa_payment):
    """
    Send payment confirmation email after successful M-Pesa payment
    
    Args:
        order: Order instance
        mpesa_payment: MpesaPayment instance
    """
    subject = f'Payment Received - Order #{order.id} - TechHub'
    
    context = {
        'order': order,
        'customer_name': f"{order.first_name} {order.last_name}",
        'mpesa_receipt': mpesa_payment.mpesa_receipt_number,
        'amount': mpesa_payment.amount,
        'transaction_date': mpesa_payment.transaction_date,
    }
    
    html_message = render_to_string('emails/Payment confirmation.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Payment confirmation email sent to {order.email}")
        return True
    except Exception as e:
        print(f"Failed to send payment email: {str(e)}")
        return False