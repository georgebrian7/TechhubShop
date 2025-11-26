from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.text import slugify
from application.models import Category, Product, UserProfile, User
from django.core.exceptions import ValidationError


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'

        widgets = {

            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone Number'}),
            'gender': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Gender'}),
            'age': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Age'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control',
                                                     'accept': 'images/*',
                                                     'title': 'upload your image here'})
        }

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'tf-field style-1'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'tf-field style-1'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'tf-field style-1'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name', 'slug', 'description']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional (auto-filled)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Category description'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        slug = cleaned_data.get('slug')

        if not slug and name:
            cleaned_data['slug'] = slugify(name)

        return cleaned_data


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'category', 'name', 'slug', 'description', 'price', 'stock',
            'image1', 'image2', 'available'
        ]

        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional (auto-filled)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_slug(self):
        name = self.cleaned_data.get('name')
        slug = self.cleaned_data.get('slug')

        if not slug and name:
            return slugify(name)

        return slug
    
class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    

class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'vTextField',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'vLargeTextField',
                'rows': 4,
                'placeholder': 'Enter category description'
            }),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError('Category name must be at least 3 characters long.')
        return name


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'vTextField',
                'placeholder': 'Enter product name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'vLargeTextField',
                'rows': 6,
                'placeholder': 'Enter detailed product description'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'vTextField',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'vTextField',
                'placeholder': '0'
            }),
            'image1': forms.ClearableFileInput(attrs={
                'class': 'vTextField',
                'placeholder': 'Input image'
            }),
            'image2': forms.ClearableFileInput(attrs={
                'class': 'vTextField',
                'placeholder': 'Input image'
            }),
            
        }
        help_texts = {
            'name': 'Enter a unique, descriptive product name',
            'slug': 'Auto-generated from name. Edit only if needed.',
            'price': 'Enter price in Ksh',
            'stock': 'Current stock quantity',
            'image1': 'Upload product image (JPG, PNG, max 5MB)',
            'image2': 'Upload product image (JPG, PNG, max 5MB)',
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError('Product name must be at least 3 characters long.')
        
        # Check for duplicate names (excluding current instance)
        instance_id = self.instance.id if self.instance else None
        if Product.objects.filter(name__iexact=name).exclude(id=instance_id).exists():
            raise ValidationError('A product with this name already exists.')
        
        return name
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError('Price must be greater than 0.')
        if price > 999999.99:
            raise ValidationError('Price cannot exceed $999,999.99.')
        return price
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise ValidationError('Stock cannot be negative.')
        if stock > 100000:
            raise ValidationError('Stock quantity seems unrealistic. Please verify.')
        return stock
    
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        # Auto-generate slug if empty
        if not slug and name:
            slug = slugify(name)
        
        # Check for duplicate slugs (excluding current instance)
        instance_id = self.instance.id if self.instance else None
        if Product.objects.filter(slug=slug).exclude(id=instance_id).exists():
            # Auto-append number to make it unique
            base_slug = slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(id=instance_id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
        
        return slug
    
    def clean(self):
        cleaned_data = super().clean()
        stock = cleaned_data.get('stock')
        available = cleaned_data.get('available')
        
        # Auto-set availability based on stock
        if stock == 0 and available:
            self.add_error('available', 'Product cannot be available with 0 stock.')
        
        return cleaned_data