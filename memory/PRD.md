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
- **Admin**: Single user mode (no authentication required per user request)

## Core Requirements (Static)
1. Store inventory of parts with picture, name, part number, description, and price
2. Track vehicle compatibility for each part
3. Print customizable invoices with company branding
4. Editable sales return policy and privacy policy
5. Customer database management
6. Low stock alerts
7. Sales and inventory reports/analytics
8. Editable tax settings (15% GCT default)

## Company Information
- **Name**: Timeless Parts and Accessories
- **Address**: Lot 36 Bustamante Highway, May Pen, Clarendon
- **Phone**: 876-403-8436
- **Email**: timelessautoimportslimited@gmail.com

## What's Been Implemented (March 7, 2026)

### Backend APIs
- Parts CRUD: Create, Read, Update, Delete parts with images
- Customers CRUD: Full customer database management
- Invoices: Create invoices with auto-generated numbers (TPA-XXXXX)
- Settings: Company info, tax settings, policies management
- Dashboard: Stats, low stock alerts, recent invoices
- Reports: Sales by period, inventory by category
- Image upload: Base64 encoding for part images

### Frontend Pages
1. **Dashboard** - Stats cards, low stock alerts, recent invoices
2. **Inventory** - Parts table with search, filter, add/edit/delete
3. **Customers** - Customer management with CRUD operations
4. **Invoices** - Invoice list with status filter, print capability
5. **Create Invoice** - Customer selection, part selection, discount, totals
6. **Invoice Print** - Professional print layout with policies
7. **Reports** - Sales chart, inventory by category
8. **Settings** - Company info, tax settings, editable policies

### Key Features Working
- Auto-generated invoice numbers (TPA-00001, TPA-00002, etc.)
- 15% GCT tax calculation (editable)
- JMD currency formatting
- Part image upload (file and URL)
- Vehicle compatibility tracking per part
- Low stock alerts on dashboard
- Print-friendly invoice layout with policies
- Sales and inventory reports with charts

## Prioritized Backlog

### P0 (Critical) - DONE
- [x] Parts inventory management
- [x] Customer database
- [x] Invoice creation and printing
- [x] Dashboard with stats

### P1 (High Priority) - DONE
- [x] Low stock alerts
- [x] Sales reports
- [x] Editable policies
- [x] Tax settings

### P2 (Medium Priority) - Future
- [ ] Export invoices to PDF
- [ ] Email invoices to customers
- [ ] Barcode/QR code scanning for parts
- [ ] Multiple user accounts with roles
- [ ] Inventory import/export (CSV)

## Next Tasks
1. Add PDF export functionality for invoices
2. Implement email sending for invoices
3. Add barcode scanning capability
4. Consider multi-user authentication if needed
5. Add inventory import from CSV/Excel
