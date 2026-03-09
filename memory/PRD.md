# Timeless Parts and Accessories - Product Requirements Document

## Original Problem Statement
Create an internal company inventory management app called "Timeless Parts and Accessories" for managing auto parts inventory, customers, and invoices with printable invoice capability.

## Architecture
- **Frontend**: React with Tailwind CSS and Shadcn UI components
- **Backend**: FastAPI with Python
- **Database**: MongoDB
- **Hosting**: Kubernetes container environment

## User Personas
- **Internal Staff**: Company employees managing inventory, creating invoices, and tracking customers
- **Admin**: Single user mode (password protection for sensitive actions)

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

## What's Been Implemented

### Phase 1 - Core Features (Complete)
- [x] Parts inventory management with CRUD operations
- [x] Customer database management
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
- [x] Invoice status system (Pending, Paid, Cancelled)
- [x] Down payment support with balance calculation
- [x] Invoice number format: TA-XX (short format)
- [x] Delete/Cancel invoices with separate password (19752)
- [x] Mark as Paid functionality
- [x] Add Payment functionality
- [x] Auto-save new customers from invoices
- [x] Customer-specific discount percentages
- [x] Customer invoice history view
- [x] **Sales Journal** - Daily transaction summary with check-off feature

## Key Features

### Invoice System
- **Status**: Pending, Paid, Cancelled (defaults to Pending)
- **Down Payments**: Record partial payments, shows balance due
- **Invoice Numbers**: TA-01, TA-02, etc. (short format)
- **Password Protection**: 
  - General edit/delete: `timeless532002`
  - Invoice delete/cancel: `19752`

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

### Core APIs
- `GET, POST /api/parts` - Parts CRUD
- `GET, POST /api/customers` - Customers CRUD
- `GET /api/customers/{id}/invoices` - Customer invoice history
- `GET, POST /api/invoices` - Invoices CRUD
- `PUT /api/invoices/{id}/mark-paid` - Mark invoice as paid
- `PUT /api/invoices/{id}/add-payment` - Add payment to invoice
- `DELETE /api/invoices/{id}?password=X` - Delete invoice (requires password)
- `PUT /api/invoices/{id}/cancel?password=X` - Cancel invoice (requires password)
- `GET, PUT /api/settings` - Settings management

### Sales Journal APIs
- `GET /api/sales-journal?date=YYYY-MM-DD` - Daily transactions
- `GET /api/sales-journal/dates` - Available dates with totals
- `PUT /api/sales-journal/check-off/{invoice_id}` - Toggle check-off

### Authentication APIs
- `POST /api/verify-password` - Verify admin password
- `POST /api/verify-invoice-password` - Verify invoice password

## Database Schema

### Parts
```json
{
  "id": "uuid",
  "name": "string",
  "part_number": "string",
  "price": "float",
  "cost_price": "float",
  "quantity": "int",
  "min_stock_level": "int",
  "category": "string",
  "image_url": "string",
  "compatible_vehicles": [{"make", "model", "year_start", "year_end"}]
}
```

### Customers
```json
{
  "id": "uuid",
  "name": "string",
  "phone": "string",
  "email": "string",
  "address": "string",
  "discount_percentage": "float"
}
```

### Invoices
```json
{
  "id": "uuid",
  "invoice_number": "TA-XX",
  "customer_id": "uuid",
  "customer_name": "string",
  "items": [{"part_id", "name", "quantity", "unit_price", "total"}],
  "subtotal": "float",
  "discount": "float",
  "tax_rate": "float",
  "tax_amount": "float",
  "total": "float",
  "status": "pending|paid|cancelled",
  "down_payment": "float",
  "amount_paid": "float",
  "balance_due": "float",
  "checked_off": "bool",
  "checked_off_at": "datetime"
}
```

## Prioritized Backlog

### P0 (Critical) - COMPLETE
- [x] Parts inventory management
- [x] Customer database
- [x] Invoice creation and printing
- [x] Dashboard with stats
- [x] Invoice status system
- [x] Down payments
- [x] Sales Journal

### P1 (High Priority) - COMPLETE
- [x] Low stock alerts
- [x] Sales reports
- [x] Editable policies
- [x] Tax settings
- [x] PWA support
- [x] Mobile-responsive design
- [x] Password protection

### P2 (Medium Priority) - Future
- [ ] Export invoices to PDF
- [ ] Email invoices to customers
- [ ] Barcode/QR code scanning for parts
- [ ] Multiple user accounts with roles
- [ ] Inventory import/export (CSV)
- [ ] Profit margin reports

## Next Tasks
1. User testing and feedback collection
2. Bug fixes based on user feedback
3. Consider PDF export feature
4. Consider email invoice feature

## Known Issues
- Browser/PWA caching may delay updates on deployed production app
  - Solution: Hard refresh, clear cache, or reinstall PWA
