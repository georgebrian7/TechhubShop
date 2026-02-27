# 🛍️ TechhubShop

> **A modern, full-featured e-commerce platform for electronics with an intuitive admin dashboard**

![Status Badge](https://img.shields.io/badge/Status-Live-brightgreen) ![License Badge](https://img.shields.io/badge/License-MIT-blue)

---

## 📋 Overview

**TechhubShop** is a comprehensive online electronics marketplace built with modern web technologies. It features a complete e-commerce experience for customers and a powerful dashboard for administrators to manage inventory, orders, and sales analytics.

🔗 **Live Site:** [www.keshilimited.com](https://www.keshilimited.com)  
🚀 **Hosted on:** Render

---

## ✨ Key Features

- 🛒 **Full E-Commerce Platform** - Browse, filter, and purchase electronics with ease
- 📊 **Admin Dashboard** - Comprehensive tools for managing products, orders, and inventory
- 🔐 **Secure Authentication** - User authentication and authorization system
- 💳 **Payment Integration** - Seamless checkout experience
- 🖼️ **Image Management** - Cloud-based image hosting and optimization
- 📱 **Responsive Design** - Works flawlessly on desktop, tablet, and mobile devices
- 🔍 **Product Search & Filtering** - Find exactly what you need with advanced filters
- 📦 **Order Management** - Track orders from purchase to delivery

---

## 🛠️ Tech Stack

### Backend
- **Framework:** ![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white) **Django** - Powerful Python web framework with built-in admin panel

### Frontend
- **Styling:** ![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white) **Bootstrap CSS** - Responsive UI components for modern interfaces

### Database
- **Database:** ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white) **PostgreSQL** - Robust relational database for reliable data management

### Cloud Services
- **Image Hosting:** ![Cloudinary](https://img.shields.io/badge/Cloudinary-3448C5?style=flat&logo=cloudinary&logoColor=white) **Cloudinary** - Optimized image uploads and delivery

### Deployment
- **Platform:** ![Render](https://img.shields.io/badge/Render-46E3B7?style=flat&logo=render&logoColor=white) **Render** - Fast, reliable cloud hosting

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Cloudinary account

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/techhubshop.git
cd techhubshop

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database, Cloudinary, and other credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit `http://localhost:8000` to see the application.

---

## 📁 Project Structure

```
techhubshop/
├── manage.py
├── requirements.txt
├── .env.example
├── techhubshop/          # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shop/                 # Main app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   └── static/
├── dashboard/            # Admin dashboard app
│   ├── models.py
│   ├── views.py
│   └── templates/
└── static/              # Global static files
    ├── css/
    ├── js/
    └── images/
```

---

## 🎯 Core Features Explained

### For Customers
- **Product Catalog** - Browse thousands of electronics with detailed specs and images
- **Smart Search** - Find products by category, price range, brand, and specifications
- **Wishlist** - Save favorite items for later purchase
- **Secure Checkout** - PCI-compliant payment processing
- **Order History** - Track all past and current orders

### For Administrators
- **Inventory Management** - Add, edit, delete, and manage product stock levels
- **Sales Analytics** - View detailed reports on revenue, top products, and customer trends
- **Order Management** - Process, ship, and track customer orders
- **User Management** - Manage customer accounts and permissions
- **Image Gallery** - Organize and optimize product images via Cloudinary integration

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=www.keshilimited.com,localhost

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/techhubshop

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Email (for order notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

---

## 📊 Performance Metrics

- ⚡ **Load Time:** < 2 seconds
- 🔒 **Security:** Django security middleware, CSRF protection
- 📈 **Scalability:** Optimized queries, caching strategies
- 🌍 **CDN:** Cloudinary for fast image delivery globally

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

For support, email support@keshilimited.com or open an issue on GitHub.

---

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap for responsive design components
- Cloudinary for reliable image hosting
- Render for seamless deployment

---

**Built with ❤️ by Keshi Limited**