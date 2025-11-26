import os
import sys
import django
import csv
from decimal import Decimal

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Set the Django settings module - CHANGE THIS to match your project structure
# Common options: "TechhubShop.settings" or "config.settings" or "core.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TechhubShop.settings")

django.setup()

# Now import your models after Django is set up
from django.contrib.auth.models import User
from application.models import Category, Product, UserProfile  # CHANGE 'yourapp' to your actual app name


def import_categories(csv_file):
    """Import categories from CSV file"""
    print(f"Importing categories from {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        created_count = 0
        updated_count = 0
        
        for row in reader:
            category, created = Category.objects.update_or_create(
                name=row['name'],
                defaults={
                    'description': row.get('description', ''),
                }
            )
            if created:
                created_count += 1
                print(f"Created category: {category.name}")
            else:
                updated_count += 1
                print(f"Updated category: {category.name}")
    
    print(f"\nCategories import complete: {created_count} created, {updated_count} updated")


def import_products(csv_file):
    """Import products from CSV file"""
    print(f"\nImporting products from {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for row in reader:
            try:
                # Get or create the category
                category_name = row.get('category', 'Uncategorized')
                category, _ = Category.objects.get_or_create(name=category_name)
                
                # Create or update the product
                product, created = Product.objects.update_or_create(
                    name=row['name'],
                    defaults={
                        'category': category,
                        'description': row.get('description', ''),
                        'price': Decimal(row['price']),
                        'stock': int(row.get('stock', 0)),
                        'available': row.get('available', 'True').lower() in ['true', '1', 'yes'],
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"Created product: {product.name} - ${product.price}")
                else:
                    updated_count += 1
                    print(f"Updated product: {product.name} - ${product.price}")
                    
            except Exception as e:
                error_count += 1
                print(f"Error importing product '{row.get('name', 'Unknown')}': {str(e)}")
    
    print(f"\nProducts import complete: {created_count} created, {updated_count} updated, {error_count} errors")


def import_users(csv_file):
    """Import users from CSV file"""
    print(f"\nImporting users from {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for row in reader:
            try:
                # Create or update user
                user, created = User.objects.update_or_create(
                    username=row['username'],
                    defaults={
                        'email': row.get('email', ''),
                        'first_name': row.get('first_name', ''),
                        'last_name': row.get('last_name', ''),
                    }
                )
                
                # Set password if provided (only for new users)
                if created and row.get('password'):
                    user.set_password(row['password'])
                    user.save()
                
                # Update or create user profile
                if hasattr(user, 'userprofile'):
                    profile = user.userprofile
                    profile.phone_number = row.get('phone_number', '')
                    profile.gender = row.get('gender', '')
                    profile.age = int(row['age']) if row.get('age') else None
                    profile.save()
                else:
                    UserProfile.objects.create(
                        user=user,
                        phone_number=row.get('phone_number', ''),
                        gender=row.get('gender', ''),
                        age=int(row['age']) if row.get('age') else None
                    )
                
                if created:
                    created_count += 1
                    print(f"Created user: {user.username}")
                else:
                    updated_count += 1
                    print(f"Updated user: {user.username}")
                    
            except Exception as e:
                error_count += 1
                print(f"Error importing user '{row.get('username', 'Unknown')}': {str(e)}")
    
    print(f"\nUsers import complete: {created_count} created, {updated_count} updated, {error_count} errors")


def main():
    """Main function to run imports"""
    print("=" * 60)
    print("Django CSV Import Script")
    print("=" * 60)
    
    # Define your CSV file paths here
    csv_files = {
        'categories': 'data/categories.csv',
        'products': 'data/products.csv',
        'users': 'data/users.csv',
    }
    
    # Import categories first (as products depend on them)
    if os.path.exists(csv_files['categories']):
        import_categories(csv_files['categories'])
    else:
        print(f"Categories file not found: {csv_files['categories']}")
    
    # Import products
    if os.path.exists(csv_files['products']):
        import_products(csv_files['products'])
    else:
        print(f"Products file not found: {csv_files['products']}")
    
    # Import users
    if os.path.exists(csv_files['users']):
        import_users(csv_files['users'])
    else:
        print(f"Users file not found: {csv_files['users']}")
    
    print("\n" + "=" * 60)
    print("Import complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()