# **AsiriaPOS Backend System Architecture**

## **1. Overview**
AsiriaPOS is a next-generation Point-of-Sale system designed for small businesses. It integrates AI-driven analytics, mobile payments, and cloud-based transactions for an efficient and scalable experience.

## 🚀 Features

* **AI-Driven Analytics**: Gain insights into sales trends and customer behavior.
* **Mobile Payments**: Seamless integration with M-Pesa API for mobile transactions.
* **Cloud-Based Transactions**: Secure and accessible data storage on cloud platforms.
* **Modular Architecture**: Easily extend or customize components as needed.
* **Role-Based Access Control**: Define user roles and permissions for enhanced security.

## **2. Technology Stack**
- **Backend Framework:** Django Framework (Python)
- **Database:** MySQL
- **Authentication:** JWT & OAuth2
- **Cloud Hosting:** Azure / AWS / Cpanel
- **Payment Integration:** M-Pesa API
- **Caching:** Redis
- **Logging & Monitoring:** Serilog, ELK Stack

## 📦 Installation
1. **Clone the repository**
```bash
git clone https://github.com/yourusername/AsiriaPOS.git
cd AsiriaPOS
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file and add your database and secret configurations.

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create a superuser**
```bash
python manage.py createsuperuser
```

7. **Start the development server**
```bash
python manage.py runserver
```
---

## 📘 API Documentation

* **Swagger UI**: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
* **Redoc**: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

The API supports full CRUD for:

* Clients (`/api/clients/`)
* Products (`/api/products/`)
* Categories (`/api/categories/`)
* Units (`/api/units/`)
* Sales & Purchases (`/api/salesheaders/`, `/api/purchaseheaders/`)
* Payments, Receipts, Expenses, etc.

---

## 🛡️ Roles & Permissions

| Role     | Access Level                         |
| -------- | ------------------------------------ |
| Owner    | Full access to all data and features |
| Manager  | Can manage sales, purchases, users   |
| Employee | Limited to sales operations          |

Authentication is required for all endpoints via JWT access tokens.

## **3. Architecture Components**
### **3.1 API Gateway**
- Handles authentication, request validation, and rate limiting.

### **3.2 Authentication & User Management Service**
- Secure login with biometric support.
- Role-based access control.

### **3.3 Product & Inventory Service**
- AI-powered demand forecasting.
- Smart inventory management with barcode scanning.

### **3.4 Sales & Purchase Service**
- Manages sales transactions and purchase orders.
- Real-time transaction syncing.

### **3.5 Reporting & Analytics Service**
- AI-driven sales insights and trends.
- Exportable reports for business intelligence.

### **3.6 Notification Service**
- Low stock alerts and real-time notifications.
- WhatsApp Business integration for customer engagement.

## **4. Modules**
- **User Management Module:** Secure authentication and role handling.
- **Product Management Module:** Stock tracking and barcode scanning.
- **Sales & Purchase Module:** Order processing, payments, and invoices.
- **AI Analytics Module:** Business insights and smart recommendations.
- **Notification Module:** Alerts for stock levels and transactions.

## **5. Database Schema**
- **Users Table:** UserID, Name, Email, Role, PasswordHash
- **Products Table:** ProductID, Name, Price, Stock, Barcode, CategoryID
- **Categories Table:** CategoryID, CategoryName
- **Sales Table:** SaleID, UserID, ProductID, Quantity, Total, Timestamp
- **Purchases Table:** PurchaseID, SupplierID, ProductID, Quantity, CostPrice, Timestamp
- **Suppliers Table:** SupplierID, Name, Contact, Address
- **Payments Table:** PaymentID, SaleID, Method, Status, Timestamp
- **Notifications Table:** NotificationID, UserID, Message, Status, Timestamp


## 📨 Contact

For support or inquiries:

* 🌐 Website: [https://www.asiriatech.ke](https://www.asiriatech.ke)
* 📧 Email: [support@asiriatech.ke](mailto:support@asiriatech.ke)

---

## 📄 License

This project is licensed under the **MIT License** 