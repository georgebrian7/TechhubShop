
import uuid
from django.contrib.auth import authenticate, login, logout

from django.shortcuts import render, redirect, get_object_or_404
# from .models import Cart, CartItem, Category, Order, OrderItem, Payment, Product, User,UserProfile
from application.forms import CategoryAdminForm, CategoryForm, CheckoutForm, ProductAdminForm, ProductForm, SignUpForm, UserProfileForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from django.db.models import Sum, Avg, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime
from .utils import MpesaAPI
from .models import Mpesa_payment
from application.models import Order, Payment
import json
from application.emails import send_payment_received_email

@login_required
def initiate_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if hasattr(order, 'payment') and order.payment.status == 'completed':
        messages.warning(request, 'This order has already been paid for.')
        return redirect('order_detail', order_id=order.id)

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')

        if not phone_number:
            messages.error(request, 'Please provide your M-Pesa phone number.')
            return redirect('mpesa:payment_form', order_id=order.id)

        # ✅ Format phone number
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif not phone_number.startswith('254'):
            phone_number = '254' + phone_number

        # ✅ For Buy Goods — AccountReference is NOT important
        account_reference = "BUYGOODS"

        try:
            mpesa = MpesaAPI()

            response = mpesa.stk_push(
                phone_number=phone_number,
                amount=int(order.get_total_cost()),
                account_reference=account_reference,
                transaction_desc=f"Order {order.id}"
            )

            if response.get('ResponseCode') == '0':
                mpesa_payment = Mpesa_payment.objects.create(
                    order=order,
                    user=request.user,
                    phone_number=phone_number,
                    amount=order.get_total_cost(),
                    account_reference=account_reference,
                    transaction_desc=f"Order {order.id}",
                    checkout_request_id=response.get('CheckoutRequestID'),
                    merchant_request_id=response.get('MerchantRequestID'),
                    status='pending'
                )

                messages.success(
                    request,
                    'STK Push sent. Enter M-Pesa PIN to complete payment.'
                )

                return redirect(
                    'mpesa:payment_status',
                    checkout_request_id=mpesa_payment.checkout_request_id
                )
            else:
                messages.error(
                    request,
                    f"Payment failed: {response.get('errorMessage', 'Unknown error')}"
                )
                return redirect('mpesa:payment_form', order_id=order.id)

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('mpesa:payment_form', order_id=order.id)

    return redirect('mpesa:payment_form', order_id=order.id)


@login_required
def payment_form(request, order_id):
    """Display M-Pesa payment form for an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order already paid
    if hasattr(order, 'payment') and order.payment.status == 'completed':
        messages.info(request, 'This order has already been paid for.')
        return redirect('order_detail', order_id=order.id)
    
    # Get or create user profile phone number
    user_phone = ""
    if hasattr(request.user, 'userprofile_set') and request.user.userprofile_set.exists():
        user_phone = request.user.userprofile_set.first().phone_number
    
    return render(request, 'Payment form.html', {
        'order': order,
        'total': order.get_total_cost(),
        'account_reference': f"ORD-{order.id}",
        'user_phone': user_phone
    })


@csrf_exempt
@require_http_methods(["POST"])
def mpesa_callback(request):
    """Handle M-Pesa callback"""
    try:
        data = json.loads(request.body)
        
        # Extract callback data
        stk_callback = data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        
        # Find the payment record
        payment = Mpesa_payment.objects.get(checkout_request_id=checkout_request_id)
        payment.result_code = str(result_code)
        payment.result_desc = result_desc
        
        if result_code == 0:
            # Successful payment
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            
            for item in callback_metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    payment.mpesa_receipt_number = item.get('Value')
                elif item.get('Name') == 'TransactionDate':
                    trans_date = str(item.get('Value'))
                    payment.transaction_date = datetime.strptime(trans_date, '%Y%m%d%H%M%S')
            
            payment.status = 'completed'
            payment.save()
            
            # Update order status and old Payment model
            payment.update_order_status()
            send_payment_received_email(payment.order, payment)
        else:
            payment.status = 'failed'
            payment.save()
        
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
    
    except Mpesa_payment.DoesNotExist:
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Payment not found'})
    except Exception as e:
        print(f"Callback error: {str(e)}")
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Failed'})


@login_required
def payment_status(request, checkout_request_id):
    """Display payment status page"""
    payment = get_object_or_404(Mpesa_payment, checkout_request_id=checkout_request_id, user=request.user)
    
    return render(request, 'Payment status.html', {
        'checkout_request_id': checkout_request_id,
        'payment': payment,
        'order': payment.order
    })


@login_required
@require_http_methods(["GET"])
def check_payment_status(request, checkout_request_id):
    """Check payment status (AJAX endpoint)"""
    try:
        payment = get_object_or_404(Mpesa_payment, checkout_request_id=checkout_request_id, user=request.user)
        
        return JsonResponse({
            'status': payment.status,
            'phone_number': payment.phone_number,
            'amount': str(payment.amount),
            'account_reference': payment.account_reference,
            'mpesa_receipt_number': payment.mpesa_receipt_number,
            'transaction_date': payment.transaction_date.isoformat() if payment.transaction_date else None,
            'result_desc': payment.result_desc,
            'created_at': payment.created_at.isoformat(),
            'order_id': payment.order.id
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)


@login_required
def payment_history(request):
    """Display user's M-Pesa payment history"""
    payments = Mpesa_payment.objects.filter(user=request.user).select_related('order')
    
    # Calculate statistics
    total_payments = payments.count()
    completed_payments = payments.filter(status='completed').count()
    pending_payments = payments.filter(status='pending').count()
    
    total_amount = sum(p.amount for p in payments.filter(status='completed'))
    
    return render(request, 'mpesa/payment_history.html', {
        'payments': payments,
        'total_payments': total_payments,
        'completed_payments': completed_payments,
        'pending_payments': pending_payments,
        'total_amount': total_amount
    })


# Admin views (optional)
@login_required
def admin_mpesa_payments(request):
    """Admin view for all M-Pesa payments (staff only)"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('index')
    
    payments = Mpesa_payment.objects.all().select_related('order', 'user')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        payments = payments.filter(status=status)
    
    return render(request, 'mpesa/admin_payments.html', {
        'payments': payments
    })
