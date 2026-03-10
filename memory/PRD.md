# Timeless Parts and Accessories - Product Requirements Document

## Original Problem Statement
Create an internal company inventory management app called "Timeless Parts and Accessories" for managing auto parts inventory, customers, and invoices with printable invoice capability.

## Architecture
- **Frontend**: React with Tailwind CSS and Shadcn UI components
- **Backend**: FastAPI with Python
- **Database**: MongoDB
- **Hosting**: Kubernetes container environment
- **Authentication**: JWT-based session tokens with bcrypt password hashing

## User Personas
- **Admin**: Can manage all users, view activity logs, perform all operations
- **Staff**: Can perform day-to-day operations (create invoices, manage inventory)

## Company Information
- **Name**: Timeless Parts and Accessories
- **Address**: Lot 36 Bustamante Highway, May Pen, Clarendon
- **Phone**: 876-403-8436
- **Email**: timelessautoimportslimited@gmail.com

## Core Requirements
1. Store inventory of parts with picture, name, part number, description, and price
2. Track vehicle compatibility for each part
3. Print customizable invoices with company branding
4. Editable sales return policy and privacy policy
5. Customer database management with discount support
6. Low stock alerts
7. Sales and inventory reports/analytics
8. Editable tax settings (GCT, default 0%)
9. **User authentication system with online/offline tracking**
10. **Activity logging for audit trail**

## What's Been Implemented

### Phase 1 - Core Features (Complete)
- [x] Parts inventory management with CRUD operations
- [x] Customer database management with discounts
- [x] Invoice creation and printing
- [x] Dashboard with stats and alerts
- [x] Low stock alerts
- [x] Sales reports
- [x] Editable policies
- [x] Tax settings
- [x] PWA support (installable on mobile)
- [x] Mobile-responsive layout with hamburger menu
- [x] Red/white theme

### Phase 2 - Advanced Invoice System (Complete - March 9, 2026)
- [x] Invoice status system (Pending, Paid, Cancelled, Refunded)
- [x] Down payment support with balance calculation
- [x] Invoice number format: TA-XX (short format)
- [x] Delete/Cancel invoices with separate password (19752)
- [x] Mark as Paid functionality
- [x] Add Payment functionality
- [x] Auto-save new customers from invoices
- [x] Customer-specific discount percentages
- [x] Customer invoice history view
- [x] Sales Journal - Daily transaction summary with check-off feature

### Phase 3 - User Authentication & Activity Tracking (Complete - March 10, 2026)
- [x] User login system with individual usernames/passwords
- [x] User registration (Admin can add new users)
- [x] Online/offline status indicators
- [x] Activity logging (who did what, when)
- [x] Invoice creator tracking (shows who created each invoice)
- [x] **Refund invoices** - Return paid invoices to stock
- [x] **Uncancel invoices** - Restore cancelled invoices
- [x] Protected routes (require login)
- [x] Session management with logout

## Key Features

### User System
- **Users**: Support for ~4 staff members
- **Roles**: Admin (full access) and Staff (day-to-day operations)
- **Online Status**: Green dot indicator, "Online now" vs time since last seen
- **Activity Log**: Records all actions with timestamps

### Invoice System
- **Status**: Pending, Paid, Cancelled, Refunded (defaults to Pending)
- **Down Payments**: Record partial payments, shows balance due
- **Invoice Numbers**: TA-01, TA-02, etc. (short format)
- **Creator Tracking**: Shows which user created each invoice
- **Password Protection**: 
  - User login: Individual per user
  - Invoice operations (delete/cancel/refund/uncancel): `19752`

### Customer Management
- Basic info: Name, Phone, Email, Address
- Discount percentage (applied automatically to all purchases)
- View all customer invoices with summary totals

### Sales Journal
- Daily transaction summary
- Check-off feature for end-of-day reconciliation
- Filter by date
- Print journal functionality
- Shows: Total invoices, sales, paid, pending, items sold

## API Endpoints

### User Auth APIs
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/register` - Register new user
- `GET /api/auth/me` - Get current user
- `GET /api/auth/users` - Get all users with online status
- `GET /api/auth/activity` - Get activity logs
- `PUT /api/auth/users/{id}/toggle-active` - Enable/disable user

### Core APIs
- `GET, POST /api/parts` - Parts CRUD
- `GET, POST /api/customers` - Customers CRUD
- `GET /api/customers/{id}/invoices` - Customer invoice history
- `GET, POST /api/invoices` - Invoices CRUD
- `PUT /api/invoices/{id}/mark-paid` - Mark invoice as paid
- `PUT /api/invoices/{id}/add-payment` - Add payment to invoice
- `PUT /api/invoices/{id}/refund?password=X` - Refund invoice
- `PUT /api/invoices/{id}/uncancel?password=X` - Restore cancelled invoice
- `DELETE /api/invoices/{id}?password=X` - Delete invoice
- `PUT /api/invoices/{id}/cancel?password=X` - Cancel invoice

### Sales Journal APIs
- `GET /api/sales-journal?date=YYYY-MM-DD` - Daily transactions
- `GET /api/sales-journal/dates` - Available dates with totals
- `PUT /api/sales-journal/check-off/{invoice_id}` - Toggle check-off

## Database Schema

### Users
```json
{
  "id": "uuid",
  "username": "string",
  "password_hash": "bcrypt hash",
  "full_name": "string",
  "role": "admin|staff",
  "is_active": "bool",
  "is_online": "bool",
  "last_seen": "datetime"
}
```

### Activity Logs
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "username": "string",
  "action": "string (login, create_invoice, etc)",
  "details": "string",
  "entity_type": "string (invoice, part, etc)",
  "entity_id": "uuid",
  "timestamp": "datetime"
}
```

### Invoices
```json
{
  "id": "uuid",
  "invoice_number": "TA-XX",
  "customer_id": "uuid",
  "customer_name": "string",
  "items": [...],
  "total": "float",
  "status": "pending|paid|cancelled|refunded",
  "down_payment": "float",
  "balance_due": "float",
  "created_by_id": "uuid",
  "created_by_name": "string",
  "refunded_at": "datetime",
  "refund_reason": "string"
}
```

## Credentials

### Default Admin User
- **Username**: admin
- **Password**: timeless532002

### Invoice Operations Password
- **Password**: 19752 (for delete, cancel, refund, uncancel)

## Prioritized Backlog

### P0 (Critical) - COMPLETE
All P0 features have been implemented

### P1 (High Priority) - COMPLETE
All P1 features have been implemented

### P2 (Medium Priority) - Future
- [ ] Export invoices to PDF
- [ ] Email invoices to customers
- [ ] Barcode/QR code scanning for parts
- [ ] Inventory import/export (CSV)
- [ ] Profit margin reports

## Test Reports
- `/app/test_reports/iteration_2.json` - Invoice system tests (24/24 passed)
- `/app/test_reports/iteration_3.json` - User auth tests (22/22 passed)
- `/app/backend/tests/test_user_auth.py` - Auth test suite

## Known Issues
- Browser/PWA caching may delay updates on deployed production app
  - Solution: Hard refresh, clear cache, or reinstall PWA
