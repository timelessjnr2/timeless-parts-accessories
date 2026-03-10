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
9. **User self-registration** - Users create their own accounts
10. **Comprehensive activity logging** - Track EVERYTHING users do

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
- [x] Refund invoices
- [x] Uncancel invoices (restore cancelled)

### Phase 3 - User Authentication & Activity Tracking (Complete - March 10, 2026)
- [x] **Self-registration** - Users create their own accounts on login page
- [x] User login system with individual usernames/passwords
- [x] Online/offline status indicators
- [x] Invoice creator tracking (shows who created each invoice)
- [x] Protected routes (require login)
- [x] Session management with logout

### Phase 4 - Comprehensive Activity Logging (Complete - March 10, 2026)
- [x] **Login/Logout tracking**
- [x] **Parts**: create_part, update_part, delete_part, increase_stock, decrease_stock
- [x] **Customers**: create_customer, update_customer, delete_customer
- [x] **Invoices**: create_invoice, update_invoice, delete_invoice, cancel_invoice, uncancel_invoice, refund_invoice, mark_invoice_paid, add_payment, check_off_invoice, uncheck_invoice
- [x] **Settings**: update_settings (company, policies, tax)
- [x] **Vehicles**: create_vehicle, delete_vehicle
- [x] **User registration**: user_registered

## Key Features

### User System
- **Self-Registration**: Users click "Create one" on login page to make their own account
- **Roles**: Admin (full access) and Staff (day-to-day operations)
- **Online Status**: Green dot indicator, "Online now" vs time since last seen
- **Activity Log**: Records ALL actions with timestamps, user, action type, and details

### Activity Logging - Tracked Actions
| Category | Actions Tracked |
|----------|-----------------|
| Auth | login, logout, user_registered |
| Parts | create_part, update_part, delete_part, increase_stock, decrease_stock |
| Customers | create_customer, update_customer, delete_customer |
| Invoices | create_invoice, update_invoice, delete_invoice, cancel_invoice, uncancel_invoice, refund_invoice, mark_invoice_paid, add_payment |
| Sales Journal | check_off_invoice, uncheck_invoice |
| Settings | update_settings (company, policies, tax) |
| Vehicles | create_vehicle, delete_vehicle |

### Invoice System
- **Status**: Pending, Paid, Cancelled, Refunded (defaults to Pending)
- **Down Payments**: Record partial payments, shows balance due
- **Invoice Numbers**: TA-01, TA-02, etc. (short format)
- **Creator Tracking**: Shows which user created each invoice
- **Password Protection**: 
  - User login: Individual per user (self-created)
  - Invoice operations (delete/cancel/refund/uncancel): `19752`

## API Endpoints

### User Auth APIs
- `POST /api/auth/register` - Self-register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user
- `GET /api/auth/users` - Get all users with online status
- `GET /api/auth/activity` - Get activity logs

## Database Schema

### Activity Logs
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "username": "string",
  "action": "string",
  "details": "string",
  "entity_type": "string",
  "entity_id": "uuid",
  "timestamp": "datetime"
}
```

## Credentials

### Default Admin User
- **Username**: admin
- **Password**: timeless532002

### Invoice Operations Password
- **Password**: 19752 (for delete, cancel, refund, uncancel)

## Test Reports
- `/app/test_reports/iteration_2.json` - Invoice system tests (24/24 passed)
- `/app/test_reports/iteration_3.json` - User auth tests (22/22 passed)

## Prioritized Backlog

### P0-P1 (Critical/High) - COMPLETE
All P0 and P1 features have been implemented

### P2 (Medium Priority) - Future
- [ ] Export invoices to PDF
- [ ] Email invoices to customers
- [ ] Barcode/QR code scanning for parts
- [ ] Inventory import/export (CSV)
- [ ] Profit margin reports

## Known Issues
- Browser/PWA caching may delay updates on deployed production app
  - Solution: Hard refresh, clear cache, or reinstall PWA
