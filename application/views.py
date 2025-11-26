
import uuid
from django.contrib.auth import authenticate, login

from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Category, Order, OrderItem, Payment, Product, User,UserProfile
from application.forms import CategoryAdminForm, CategoryForm, CheckoutForm, ProductAdminForm, ProductForm, SignUpForm, UserProfileForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
# Create your views here.
def index(request):
    featured_products = Product.objects.filter(available=True)[:8]
    categories = Category.objects.all()[:6]
    products = Product.objects.all()

    return render(request, 'index.html', {
        'featured_products': featured_products,
        'categories': categories,
        'products':products
    })

def register(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user=authenticate(request, username=username,password=raw_password)
            login(request, user)
            return redirect('login')
        else:
            messages.error(request, 'Please correct the error below.')

    return render(request, 'register.html',{'form':form})

def login_view(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('cart')
    return render(request, 'login.html')

@login_required(login_url='dashboard_login')
def dashboard(request,):
    return render(request, 'admin.html')

def products(request):
    products = Product.objects.filter(available=True)
    query = request.GET.get('q')
    category_slug = request.GET.get('category')

    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    return render(request, 'products.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_slug
    })

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('cart')


@login_required
def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    total = cart.get_total_price()
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })

def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')
    
    return redirect('cart')

def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(CartItem, id=product_id)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('cart')

def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('shop:product_list')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                postal_code=form.cleaned_data['postal_code'],
                city=form.cleaned_data['city']
            )
            
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )
                item.product.stock -= item.quantity
                item.product.save()
            
            Payment.objects.create(
                order=order,
                transaction_id=str(uuid.uuid4()),
                amount=order.get_total_cost(),
                status='completed'
            )
            
            cart_items.delete()
            
            return redirect('shop:order_confirmation', order_id=order.id)
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = CheckoutForm(initial=initial_data)
    
    total = cart.get_total_price()
    
    return render(request, 'cart.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total
    })
def cart_total(request, total):
    total_item = get_object_or_404(total)
    return render (request, total_item) 

def admin_login(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('dashboard')
    return render(request, 'auth.html')

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = product.get_related_products()
    return render(request, 'products.html', {
        'product': product,
        'related_products': related_products
    })

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'cart.html', {'order': order})



def product_add(request):
    if request.method == 'POST':
        form=ProductAdminForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_add')
    else:
        form=ProductAdminForm()

    return render(request, 'product-add.html',{'form':form})


def category_add(request):
    if request.method == 'POST':
        form=CategoryAdminForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category_add')
    else:
        form=CategoryAdminForm()

    return render(request, 'category_add.html',{'form':form})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product-list.html', {'products':products})

def selected_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    return render(request, 'products.html', {'category': category, 'products': products})

def product_edit(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product-edit.html', {'form': form, 'product': product})


def order_list(request):
    return render(request, 'order-list.html')

def order_details(request):
    return render(request, 'order-details.html')

def customer_list(request):
    return render(request, 'customers.html')

def customer_detail(request):
    return render(request, 'customer-detail.html')

def stock_list(request):
    return render(request, 'inventory-info.html')

def purchase(request):
    return render(request, 'purchase.html')

def admin_profile(request):
    return render(request, 'admin-profile.html')

def categories(request):
    if request.method == 'POST':
        form=CategoryForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form=CategoryForm()
    return render(request, 'categories.html' ,{'form':form})