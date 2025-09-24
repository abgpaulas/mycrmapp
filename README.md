# Django Multi-Purpose Business Application

A comprehensive Django-based business management application with multiple modules for accounting, inventory, invoicing, and more.

## 🚀 Features

- **User Management**: Complete authentication and authorization system
- **Company Management**: Multi-company support with role-based access
- **Inventory Management**: Product tracking, stock management, and reporting
- **Invoice System**: Create, manage, and track invoices
- **Receipt Management**: Handle customer receipts and payments
- **Job Orders**: Track work orders and project management
- **Quotations**: Create and manage customer quotations
- **Expense Tracking**: Monitor business expenses
- **Client Management**: Customer relationship management
- **Accounting**: Financial reporting and bookkeeping
- **Waybills**: Shipping and delivery management

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **API**: Django REST Framework
- **Authentication**: Custom user model with email authentication
- **File Handling**: Pillow for image processing
- **PDF Generation**: ReportLab and xhtml2pdf
- **Excel Support**: openpyxl for spreadsheet operations

## 📋 Prerequisites

- Python 3.9+
- pip (Python package installer)
- Git
- PostgreSQL (for production)

## 🔧 Installation

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/abgpaulas/mycrmapp.git
   cd mycrmapp
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.template .env
   # Edit .env with your configuration
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```

8. **Run development server**:
   ```bash
   python manage.py runserver
   ```

## 🌐 Deployment

### Railway Deployment

This application is configured for easy deployment on Railway platform.

1. **Follow the Railway deployment guide**: See `RAILWAY_DEPLOYMENT.md`
2. **Configure environment variables** in Railway dashboard
3. **Add PostgreSQL database** service
4. **Deploy and test** your application

### Other Platforms

The application can also be deployed on:
- Heroku
- DigitalOcean App Platform
- AWS Elastic Beanstalk
- Google Cloud Platform

## 📁 Project Structure

```
mycrmapp/
├── apps/                    # Django applications
│   ├── accounts/           # User authentication and management
│   ├── core/               # Core functionality and utilities
│   ├── rbac/               # Role-based access control
│   ├── company_management/ # Company and organization management
│   ├── inventory/          # Product and stock management
│   ├── invoices/           # Invoice creation and management
│   ├── receipts/           # Receipt handling
│   ├── waybills/           # Shipping and delivery
│   ├── job_orders/         # Work order management
│   ├── quotations/         # Customer quotations
│   ├── expenses/           # Expense tracking
│   ├── clients/            # Customer management
│   └── accounting/         # Financial reporting
├── business_app/           # Django project settings
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploaded files
├── logs/                   # Application logs
└── requirements.txt        # Python dependencies
```

## 🔐 Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
DEBUG_INVENTORY=False

# Database (Railway provides DATABASE_URL automatically)
# DATABASE_URL=postgresql://user:password@host:port/database

# Email Settings (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

## 🎯 Usage

### Getting Started

1. **Access the application** at `http://localhost:8000` (development)
2. **Login** with your superuser credentials
3. **Set up your company** in the company management section
4. **Configure user roles** and permissions
5. **Start adding** products, clients, and managing your business

### Key Features

- **Dashboard**: Overview of your business metrics
- **Multi-company Support**: Manage multiple companies from one interface
- **Role-based Access**: Control what users can see and do
- **Real-time Updates**: Live data updates across the application
- **Export Capabilities**: Export data to PDF and Excel formats
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

## 📊 API Documentation

The application includes a REST API built with Django REST Framework:

- **API Endpoints**: Available at `/api/`
- **Authentication**: Session and Token authentication
- **Documentation**: Auto-generated API documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. **Check the documentation**: Review the deployment guides and README
2. **Create an issue**: Use GitHub Issues for bug reports and feature requests
3. **Community**: Join discussions in the GitHub Discussions section

## 🔄 Version History

- **v1.0.0**: Initial release with core business management features
- **v1.1.0**: Added Railway deployment configuration
- **v1.2.0**: Enhanced API and improved user interface

## 🎉 Acknowledgments

- Django community for the excellent framework
- Bootstrap for the responsive UI components
- All contributors and users who provide feedback

---

**Made with ❤️ using Django**
