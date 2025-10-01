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
git clone https://github.com/muthaa/AsiriaPOS.git
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

### Fine-grained permissions
- `CanApproveRefunds`: Only Owners/Managers can approve returns and refunds
  - Applies to: `POST /api/sales-returns/{id}/approve/`, `POST /api/sales-refunds/{id}/approve/`
- `CanVoidTransactions`: Only Owners/Managers can void sales lines
  - Applies to: `DELETE /api/salesdetails/{id}/`
- `CanOverridePrices`: Reserved for Owners/Managers (hook available for price override flows)

How to configure:
1. Create Django groups named `Owner`, `Manager`, `Employee`.
2. Assign users to groups. The permissions above check group membership.

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

### 3.4 Returns & Refunds
- Record returns with reasons; stock increases and movements/audit are recorded.
- Issue refunds (cash/card/mobile/store-credit) linked to a sale.

Endpoints:
- `POST /api/sales-returns/` (create return)
- `GET /api/sales-returns/`
- `POST /api/sales-returns/{id}/approve/` (approve return)
- `POST /api/sales-refunds/` (create refund)
- `GET /api/sales-refunds/`
- `POST /api/sales-refunds/{id}/approve/` (approve refund)

Example return payload:
```json
{
  "user_client": "<user_client_id>",
  "sales_header": "<sales_header_id>",
  "product": "<product_id>",
  "unit": "<unit_id>",
  "quantity": 2,
  "reason": "DAMAGED",
  "notes": "Box torn"
}
```

Example refund payload:
```json
{
  "user_client": "<user_client_id>",
  "sales_header": "<sales_header_id>",
  "amount": 1750.00,
  "method": "CASH",
  "reference": "RF-00123"
}
```

### 3.5 Purchase Orders → GRN
- Create Purchase Orders (PO) and receive goods via GRN; stock increases on GRN.

Endpoints:
- `POST /api/poheaders/`, `POST /api/podetails/`
- `POST /api/grnheaders/`, `POST /api/grndetails/`

Example PO payloads:
```json
// Header
{
  "user_client": "<user_client_id>",
  "supplier": "<supplier_id>",
  "order_number": "PO-2025-0001",
  "expected_date": "2025-09-01",
  "notes": "Urgent"
}
```
```json
// Detail
{
  "user_client": "<user_client_id>",
  "po_header": "<po_header_id>",
  "product": "<product_id>",
  "unit": "<unit_id>",
  "quantity": 50,
  "price_per_unit": 120.00
}
```

Example GRN payloads:
```json
// Header
{
  "user_client": "<user_client_id>",
  "supplier": "<supplier_id>",
  "po_header": "<po_header_id>",
  "grn_number": "GRN-2025-0001",
  "notes": "Received in good condition"
}
```
```json
// Detail (increases stock)
{
  "user_client": "<user_client_id>",
  "grn_header": "<grn_header_id>",
  "product": "<product_id>",
  "unit": "<unit_id>",
  "quantity": 50,
  "price_per_unit": 120.00
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

### 3.6 Multi-location Inventory
- Manage multiple locations/branches and track per-location stock.
- Transfer stock between locations with audit trail and stock movements.

Endpoints:
- `POST /api/locations/`, `GET /api/locations/`
- `POST /api/location-stocks/` (seed/adjust per-location stock)
- `POST /api/stock-transfers/` to create, and `POST /api/stock-transfers/{id}/apply/` to move stock

Example location:
```json
{
  "user_client": "<user_client_id>",
  "name": "Warehouse A",
  "code": "WH-A",
  "address": "Industrial Rd"
}
```

### 3.7 Reservations (Layaway / Online Pending Orders)
- Reserve stock for pending sales so it’s not sold elsewhere.
- Confirm order to release reservations and proceed; cancel to free stock.

Endpoints:
- `POST /api/salesdetails/{id}/reserve/` (optional body: `{ "expiry_days": 2 }`)
- `POST /api/salesheaders/{id}/confirm/`
- `POST /api/salesheaders/{id}/cancel/`
- `GET /api/sales-reservations/?product=<id>&is_active=true`

Auto-release expired reservations:
- Command: `python manage.py release_expired_reservations`
- Schedule (Windows Task Scheduler):
```
powershell -NoProfile -ExecutionPolicy Bypass -Command "& 'C:\\Users\\hp\\Desktop\\POS\\vpos\\Scripts\\Activate.ps1'; cd 'C:\\Users\\hp\\Desktop\\POS\\AsiriaPOS'; python manage.py release_expired_reservations"
```
- Cron (Linux): `*/15 * * * * cd /path/AsiriaPOS && . venv/bin/activate && python manage.py release_expired_reservations`

Example transfer:
```json
{
  "user_client": "<user_client_id>",
  "product": "<product_id>",
  "from_location": "<location_id_src>",
  "to_location": "<location_id_dst>",
  "quantity": 10,
  "reference": "TX-TR-0001",
  "reason": "Replenish front store",
  "created_by": "<user_client_id>"
}
```

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