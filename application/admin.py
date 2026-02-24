from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from application.forms import CategoryAdminForm, ProductAdminForm
from application.models import UserProfile , Category, Product, Cart, CartItem, Order, OrderItem, Payment
from django.urls import reverse

# Register your models here.
admin.site.register(UserProfile)


class ProfileInline(admin.StackedInline):
    model = UserProfile

# extend user

class UserAdmin(admin.ModelAdmin):
    model = User
    field = ['username', 'first_name', 'last_name', 'email']
    inlines = [ProfileInline]

# unregister old user
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ['name', 'slug', 'product_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    def product_count(self, obj):
        count = obj.products.count()
        url = reverse('categories') + f'?category__id__exact={obj.id}'
        return format_html('{} products', url, count)
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = [
        'name', 
        'category', 
        'price', 
        'stock',
        'image1',
        'image2', 
        'available', 
        'created_at',
        'action_buttons'
    ]
    list_filter = ['available', 'category', 'created_at', 'updated_at']
    list_editable = ['price', 'stock', 'available', 'image1', 'image2']
    search_fields = ['name', 'description', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category')
        }),
        ('Product Details', {
            'fields': ('description', 'price', 'stock', 'image1', 'image2')
        }),
        ('Availability', {
            'fields': ('available',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_available', 'make_unavailable', 'duplicate_products']
    
    
    def action_buttons(self, obj):
        view_url = reverse('product', args=[obj.slug])
        return format_html(
            'View on Site',
            view_url
        )
    action_buttons.short_description = 'Actions'
    
    def make_available(self, request, queryset):
        updated = queryset.update(available=True)
        self.message_user(request, f'{updated} products marked as available.')
    make_available.short_description = 'Mark selected as available'
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(available=False)
        self.message_user(request, f'{updated} products marked as unavailable.')
    make_unavailable.short_description = 'Mark selected as unavailable'
    
    def duplicate_products(self, request, queryset):
        for product in queryset:
            product.pk = None
            product.name = f"{product.name} (Copy)"
            product.slug = None  # Will be auto-generated
            product.save()
        self.message_user(request, f'{queryset.count()} products duplicated.')
    duplicate_products.short_description = 'Duplicate selected products'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'get_total_price', 'added_at']
    can_delete = False
    
    def get_total_price(self, obj):
        return f"${obj.get_total_price()}"
    get_total_price.short_description = 'Total'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'session_key']
    readonly_fields = ['created_at', 'updated_at', 'total_price', 'items_count']
    inlines = [CartItemInline]

    def items_count(self, obj):
        return obj.get_total_items()
    items_count.short_description = 'Items'
    
    def total_price(self, obj):
        return f"${obj.get_total_price()}"
    total_price.short_description = 'Total'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity', 'get_cost']
    can_delete = False
    
    def get_cost(self, obj):
        return f"${obj.get_cost()}"
    get_cost.short_description = 'Subtotal'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'email', 'total_cost', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at', 'total_cost']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'first_name', 'last_name', 'email')
        }),
        ('Order Status', {
            'fields': ('status',)
        }),
        ('Order Summary', {
            'fields': ('total_cost',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_processing', 'mark_shipped', 'mark_delivered']
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Customer'
    
    def total_cost(self, obj):
        return f"${obj.get_total_cost()}"
    total_cost.short_description = 'Total'
    
    def payment_status(self, obj):
        try:
            payment = obj.payment
            colors = {
                'pending': '#FFA500',
                'completed': '#28A745',
                'failed': '#DC3545',
                'refunded': '#6C757D'
            }
            color = colors.get(payment.status, '#999')
            return format_html(
                '{}',
                color,
                payment.get_status_display()
            )
        except Payment.DoesNotExist:
            return format_html('No payment')
    payment_status.short_description = 'Payment'
    
    def mark_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_processing.short_description = 'Mark as Processing'
    
    def mark_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_shipped.short_description = 'Mark as Shipped'
    
    def mark_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_delivered.short_description = 'Mark as Delivered'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['transaction_id']

    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'transaction_id', 'amount', 'payment_method')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def order_link(self, obj):
        url = reverse('admin:shop_order_change', args=[obj.order.id])
        return format_html('Order #{}', url, obj.order.id)
    order_link.short_description = 'Order'

