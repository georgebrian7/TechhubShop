from django.urls import path
from . import views

app_name = 'mpesa'

urlpatterns = [
    # Payment initiation
    path('pay/<int:order_id>/', views.payment_form, name='payment_form'),
    path('initiate/<int:order_id>/', views.initiate_payment, name='initiate_payment'),
    
    # Payment status
    path('status/<str:checkout_request_id>/', views.payment_status, name='payment_status'),
    path('check-status/<str:checkout_request_id>/', views.check_payment_status, name='check_status'),
    
    # Callback
    path('callback/', views.mpesa_callback, name='callback'),
    
    # Payment history
    path('history/', views.payment_history, name='payment_history'),
    
    # Admin (optional)
    path('admin/payments/', views.admin_mpesa_payments, name='admin_payments'),
]