# **AsiriaPOS Backend System Architecture**

## **1. Overview**
AsiriaPOS is a next-generation Point-of-Sale system designed for small businesses. It integrates AI-driven analytics, mobile payments, and cloud-based transactions for an efficient and scalable experience.

## 🚀 Features

* **AI-Driven Analytics**: Gain insights into sales trends and customer behavior.
* **Mobile Payments**: Seamless integration with M-Pesa API for mobile transactions.
* **Cloud-Based Transactions**: Secure and accessible data storage on cloud platforms.
* **Modular Architecture**: Easily extend or customize components as needed.
* **Role-Based Access Control**: Define user roles and permissions for enhanced security.
* **Stock Control**: Real-time stock updates, movement tracking, adjustments, and alerts.
* **Cash Sessions & Split Payments**: Track cash drawer sessions and support multi-method payments per sale.
* **Audit Logs**: Sensitive actions (voids, price overrides, refunds) are recorded with who/when/what.

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
* Stock control (`/api/stock-movements/`, `/api/stock-adjustments/`, `/api/stock-alerts/`)
* Cash sessions (`/api/cash-sessions/`) and Sales payments (`/api/sales-payments/`)

---

## 🛡️ Roles & Permissions

| Role     | Access Level                         |
| -------- | ------------------------------------ |
| Owner    | Full access to all data and features |
| Manager  | Can manage sales, purchases, users   |
| Employee | Limited to sales operations          |

Authentication is required for all endpoints via JWT access tokens.

## Authentication (JWT)

This project uses JWT authentication via [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/).

### Obtain Token (Login)

POST `/api/token/`

Request body:
```json
{
  "phone_number": "your_phone_number",
  "password": "your_password"
}
```

Response:
```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

### Refresh Token

POST `/api/token/refresh/`

Request body:
```json
{
  "refresh": "<refresh_token>"
}
```

Response:
```json
{
  "access": "<new_access_token>"
}
```

### Using the Access Token

Include the following header in your requests:

```
Authorization: Bearer <access_token>
```

### API Documentation

Interactive API docs (including JWT login/logout) are available at:
- `/swagger/` (Swagger UI)
- `/redoc/` (ReDoc)

## **3. Key POS Modules**

### 3.1 Stock Control
- Real-time stock updates on sales and purchases
- Movement tracking with reasons and references
- Adjustments with approval workflow
- Low/out-of-stock alerts

Endpoints:
- `/api/products/low_stock/`, `/api/products/out_of_stock/`
- `/api/stock-movements/`, `/api/stock-adjustments/`, `/api/stock-alerts/`

### 3.2 Cash Sessions
- Open/close cash drawer sessions (with opening float and closing totals)
- Associate sales payments to sessions

Endpoints:
- `POST /api/cash-sessions/` (open)
- `POST /api/cash-sessions/{id}/close/` (close)
- `GET /api/cash-sessions/`

Example close payload:
```json
{
  "closing_total": 125000.00
}
```

### 3.3 Split Payments
- Support multiple payment methods per sale

Endpoints:
- `POST /api/sales-payments/` (single payment)
- `POST /api/sales-payments/split/` (batch create payments for a sale)

Example split payload:
```json
{
  "sales_header": "<sales_header_id>",
  "session": "<cash_session_id>",
  "payments": [
    { "method": "CASH", "amount": 500.00 },
    { "method": "CARD", "amount": 1250.00, "reference": "TX-123" }
  ]
}
```

### 3.4 Audit Logs
- Sensitive actions are recorded with who/when/what and before/after snapshots
- Currently implemented for:
  - Price override on `SalesDetail` updates
  - Void on `SalesDetail` delete

Model: `Domain.AuditLog`
Fields: `action`, `model_name`, `object_id`, `user`, `reason`, `before_data`, `after_data`, `created_at`

Admin: searchable and filterable under “Audit Logs”.

Planned:
- Refund logs, receipt reversals
- Purchase/sales header voids

---

## **4. Architecture Components**
### **4.1 API Gateway**
- Handles authentication, request validation, and rate limiting.

### **4.2 Authentication & User Management Service**
- Secure login with biometric support.
- Role-based access control.

### **4.3 Product & Inventory Service**
- AI-powered demand forecasting.
- Smart inventory management with barcode scanning.

### **4.4 Sales & Purchase Service**
- Manages sales transactions and purchase orders.
- Real-time transaction syncing.

### **4.5 Reporting & Analytics Service**
- AI-driven sales insights and trends.
- Exportable reports for business intelligence.

### **4.6 Notification Service**
- Low stock alerts and real-time notifications.
- WhatsApp Business integration for customer engagement.

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