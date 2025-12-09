"""
URL configuration for Techhub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path

from application import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login_view, name='login'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('products', views.products, name='products'),
    path('cart', views.cart_view, name='cart'),
    path('dashboard_login', views.admin_login, name='dashboard_login'),
    path('product_list', views.product_list, name='product_list'),
    path('product_add', views.product_add, name='product_add'),
    path('order_list', views.order_list, name='order_list'),
    path('order_details/<int:order_id>/', views.order_details, name='order_details'),
    path('customer_list', views.customer_list, name='customer_list'),
    path('customer_detail', views.customer_detail, name='customer_detail'),
    path('purchase', views.purchase, name='purchase'),
    path('stock_list', views.stock_list, name='stock_list'),
    path('admin_profile', views.admin_profile, name='admin_profile'),
    path('categories', views.categories, name='categories'),
    path('product/<slug:slug>/', views.product_detail, name='product'),
    path('product_edit/<slug:slug>/', views.product_edit, name='product_edit'),
    path('products/<slug:slug>/', views.selected_category, name='products'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('confirm/<int:cart_items_id>/', views.order_confirmation, name='confirm'),
    path('category_add', views.category_add, name='category_add'),
    path('product_delete/<slug:slug>/', views.delete_product, name='product_delete'),
    path('checkout', views.checkout, name='checkout'),
    path('confirm_order/<int:order_id>/', views.order_confirmation, name='confirm_order'),
    path('profile', views.profile, name='profile'),
    path('order/', views.order_page, name='order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('logout/', views.user_logout, name='logout'),
]   
