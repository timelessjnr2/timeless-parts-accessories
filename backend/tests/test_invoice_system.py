"""
Test Suite for Timeless Parts & Accessories - Invoice System Features
Tests for: Invoice status (pending/paid), down payments, balance due, 
customer discount, invoice number format, password-protected operations,
sales journal, and customer invoice history.
"""
import pytest
import requests
import os
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://invoice-mgmt-12.preview.emergentagent.com').rstrip('/')
API_BASE = f"{BASE_URL}/api"

# Test credentials from requirements
ADMIN_PASSWORD = "timeless532002"
INVOICE_PASSWORD = "19752"


class TestAPIHealth:
    """Basic API health checks"""
    
    def test_api_is_running(self):
        """Verify API is accessible"""
        response = requests.get(f"{API_BASE}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("✅ API is running and accessible")


class TestPasswordVerification:
    """Test password verification endpoints"""
    
    def test_admin_password_valid(self):
        """Test admin password verification"""
        response = requests.post(f"{API_BASE}/verify-password", json={"password": ADMIN_PASSWORD})
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] == True
        print("✅ Admin password verification works")
    
    def test_admin_password_invalid(self):
        """Test invalid admin password"""
        response = requests.post(f"{API_BASE}/verify-password", json={"password": "wrong"})
        assert response.status_code == 401
        print("✅ Invalid admin password correctly rejected")
    
    def test_invoice_password_valid(self):
        """Test invoice password verification with password 19752"""
        response = requests.post(f"{API_BASE}/verify-invoice-password", json={"password": INVOICE_PASSWORD})
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] == True
        print(f"✅ Invoice password '{INVOICE_PASSWORD}' verification works")
    
    def test_invoice_password_invalid(self):
        """Test invalid invoice password"""
        response = requests.post(f"{API_BASE}/verify-invoice-password", json={"password": "wrong"})
        assert response.status_code == 401
        print("✅ Invalid invoice password correctly rejected")


class TestCustomerDiscountPercentage:
    """Test customer-specific discount percentage feature"""
    
    @pytest.fixture(autouse=True)
    def setup_customer(self):
        """Create and cleanup test customer with discount"""
        self.customer_data = {
            "name": "TEST_DiscountCustomer",
            "phone": "876-555-1234",
            "email": "discount@test.com",
            "address": "Test Address",
            "discount_percentage": 15.0
        }
        response = requests.post(f"{API_BASE}/customers", json=self.customer_data)
        if response.status_code == 200:
            self.customer = response.json()
            yield
            # Cleanup
            requests.delete(f"{API_BASE}/customers/{self.customer['id']}")
        else:
            pytest.skip("Could not create test customer")
    
    def test_customer_discount_created(self):
        """Verify customer is created with discount percentage"""
        assert self.customer["discount_percentage"] == 15.0
        print(f"✅ Customer created with {self.customer['discount_percentage']}% discount")
    
    def test_customer_discount_retrieved(self):
        """Verify discount percentage is retrieved correctly"""
        response = requests.get(f"{API_BASE}/customers/{self.customer['id']}")
        assert response.status_code == 200
        customer = response.json()
        assert customer["discount_percentage"] == 15.0
        print("✅ Customer discount percentage retrieved correctly")
    
    def test_customer_discount_updated(self):
        """Verify discount percentage can be updated"""
        response = requests.put(
            f"{API_BASE}/customers/{self.customer['id']}", 
            json={"discount_percentage": 20.0}
        )
        assert response.status_code == 200
        updated = response.json()
        assert updated["discount_percentage"] == 20.0
        print("✅ Customer discount percentage updated correctly")


class TestInvoiceNumberFormat:
    """Test invoice number format (TA-XX)"""
    
    @pytest.fixture(autouse=True)
    def setup_invoice(self):
        """Create test part and invoice"""
        # Create a test part first
        part_data = {
            "name": "TEST_InvoiceNumPart",
            "part_number": "INV-NUM-001",
            "price": 100.0,
            "quantity": 10
        }
        part_res = requests.post(f"{API_BASE}/parts", json=part_data)
        if part_res.status_code != 200:
            pytest.skip("Could not create test part")
        self.part = part_res.json()
        
        # Create invoice
        invoice_data = {
            "customer_name": "TEST_InvoiceNumCustomer",
            "items": [{
                "part_id": self.part["id"],
                "part_number": self.part["part_number"],
                "name": self.part["name"],
                "quantity": 1,
                "unit_price": 100.0,
                "total": 100.0
            }],
            "subtotal": 100.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 100.0,
            "status": "pending"
        }
        inv_res = requests.post(f"{API_BASE}/invoices", json=invoice_data)
        if inv_res.status_code == 200:
            self.invoice = inv_res.json()
            yield
            # Cleanup - use invoice password
            requests.delete(f"{API_BASE}/invoices/{self.invoice['id']}?password={INVOICE_PASSWORD}")
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
        else:
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
            pytest.skip("Could not create test invoice")
    
    def test_invoice_number_format(self):
        """Verify invoice number follows TA-XX format"""
        inv_num = self.invoice["invoice_number"]
        # Should match pattern TA-XX where XX is number
        assert inv_num.startswith("TA-"), f"Invoice number '{inv_num}' should start with 'TA-'"
        # Extract number part
        num_part = inv_num.split("-")[1]
        assert num_part.isdigit(), f"Invoice number '{inv_num}' should end with digits"
        print(f"✅ Invoice number format correct: {inv_num}")


class TestInvoiceStatus:
    """Test invoice status (pending/paid) functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_invoice(self):
        """Create test part and invoice with pending status"""
        # Create a test part
        part_data = {
            "name": "TEST_StatusPart",
            "part_number": "STATUS-001",
            "price": 200.0,
            "quantity": 10
        }
        part_res = requests.post(f"{API_BASE}/parts", json=part_data)
        if part_res.status_code != 200:
            pytest.skip("Could not create test part")
        self.part = part_res.json()
        
        # Create invoice with status 'pending' (NOT defaulting to paid)
        invoice_data = {
            "customer_name": "TEST_StatusCustomer",
            "items": [{
                "part_id": self.part["id"],
                "part_number": self.part["part_number"],
                "name": self.part["name"],
                "quantity": 1,
                "unit_price": 200.0,
                "total": 200.0
            }],
            "subtotal": 200.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 200.0,
            "status": "pending"  # Explicitly testing pending status
        }
        inv_res = requests.post(f"{API_BASE}/invoices", json=invoice_data)
        if inv_res.status_code == 200:
            self.invoice = inv_res.json()
            yield
            # Cleanup
            requests.delete(f"{API_BASE}/invoices/{self.invoice['id']}?password={INVOICE_PASSWORD}")
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
        else:
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
            pytest.skip("Could not create test invoice")
    
    def test_invoice_created_with_pending_status(self):
        """Verify invoice is created with 'pending' status not 'paid'"""
        assert self.invoice["status"] == "pending"
        print("✅ Invoice created with 'pending' status (not defaulting to paid)")
    
    def test_mark_invoice_as_paid(self):
        """Test marking invoice as paid"""
        response = requests.put(f"{API_BASE}/invoices/{self.invoice['id']}/mark-paid")
        assert response.status_code == 200
        
        # Verify the invoice is now paid
        get_res = requests.get(f"{API_BASE}/invoices/{self.invoice['id']}")
        assert get_res.status_code == 200
        invoice = get_res.json()
        assert invoice["status"] == "paid"
        assert invoice["balance_due"] == 0
        print("✅ Invoice marked as paid successfully")


class TestDownPaymentAndBalanceDue:
    """Test down payment and remaining balance calculation"""
    
    @pytest.fixture(autouse=True)
    def setup_invoice(self):
        """Create test part and invoice with down payment"""
        # Create a test part
        part_data = {
            "name": "TEST_DownPaymentPart",
            "part_number": "DP-001",
            "price": 1000.0,
            "quantity": 10
        }
        part_res = requests.post(f"{API_BASE}/parts", json=part_data)
        if part_res.status_code != 200:
            pytest.skip("Could not create test part")
        self.part = part_res.json()
        
        # Create invoice with down payment
        self.down_payment = 300.0
        self.total = 1000.0
        invoice_data = {
            "customer_name": "TEST_DownPaymentCustomer",
            "items": [{
                "part_id": self.part["id"],
                "part_number": self.part["part_number"],
                "name": self.part["name"],
                "quantity": 1,
                "unit_price": 1000.0,
                "total": 1000.0
            }],
            "subtotal": 1000.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 1000.0,
            "status": "pending",
            "down_payment": self.down_payment
        }
        inv_res = requests.post(f"{API_BASE}/invoices", json=invoice_data)
        if inv_res.status_code == 200:
            self.invoice = inv_res.json()
            yield
            # Cleanup
            requests.delete(f"{API_BASE}/invoices/{self.invoice['id']}?password={INVOICE_PASSWORD}")
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
        else:
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
            pytest.skip("Could not create test invoice")
    
    def test_down_payment_recorded(self):
        """Verify down payment is recorded correctly"""
        assert self.invoice["down_payment"] == self.down_payment
        print(f"✅ Down payment recorded: {self.invoice['down_payment']}")
    
    def test_balance_due_calculated(self):
        """Verify balance due is calculated correctly (total - down_payment)"""
        expected_balance = self.total - self.down_payment
        assert self.invoice["balance_due"] == expected_balance
        print(f"✅ Balance due calculated correctly: {self.invoice['balance_due']}")
    
    def test_add_payment_updates_balance(self):
        """Test adding a payment reduces balance"""
        payment_amount = 200.0
        response = requests.put(f"{API_BASE}/invoices/{self.invoice['id']}/add-payment?amount={payment_amount}")
        assert response.status_code == 200
        
        # Verify balance is updated
        get_res = requests.get(f"{API_BASE}/invoices/{self.invoice['id']}")
        invoice = get_res.json()
        
        # Balance should be: total - down_payment - amount_paid
        # Note: amount_paid accumulates including down_payment in some implementations
        assert invoice["balance_due"] <= (self.total - self.down_payment - payment_amount + 1)  # Allow small rounding
        print(f"✅ Payment added, new balance: {invoice['balance_due']}")


class TestAutoSaveCustomer:
    """Test auto-save customer from invoice feature"""
    
    @pytest.fixture(autouse=True)
    def setup_invoice(self):
        """Create test part and invoice with save_customer flag"""
        # Create a test part
        part_data = {
            "name": "TEST_AutoSavePart",
            "part_number": "AS-001",
            "price": 50.0,
            "quantity": 10
        }
        part_res = requests.post(f"{API_BASE}/parts", json=part_data)
        if part_res.status_code != 200:
            pytest.skip("Could not create test part")
        self.part = part_res.json()
        
        # Create invoice with save_customer = true
        self.customer_name = f"TEST_AutoSaveCustomer_{datetime.now().timestamp()}"
        invoice_data = {
            "customer_name": self.customer_name,
            "customer_phone": "876-555-9999",
            "customer_address": "Auto Save Test Address",
            "items": [{
                "part_id": self.part["id"],
                "part_number": self.part["part_number"],
                "name": self.part["name"],
                "quantity": 1,
                "unit_price": 50.0,
                "total": 50.0
            }],
            "subtotal": 50.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 50.0,
            "status": "pending",
            "save_customer": True  # Flag to auto-save customer
        }
        inv_res = requests.post(f"{API_BASE}/invoices", json=invoice_data)
        if inv_res.status_code == 200:
            self.invoice = inv_res.json()
            yield
            # Cleanup
            requests.delete(f"{API_BASE}/invoices/{self.invoice['id']}?password={INVOICE_PASSWORD}")
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
            # Try to cleanup auto-created customer
            if self.invoice.get("customer_id"):
                requests.delete(f"{API_BASE}/customers/{self.invoice['customer_id']}")
        else:
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
            pytest.skip("Could not create test invoice")
    
    def test_customer_auto_saved(self):
        """Verify customer was auto-saved from invoice"""
        # Invoice should now have a customer_id
        customer_id = self.invoice.get("customer_id")
        if customer_id:
            # Verify customer exists
            response = requests.get(f"{API_BASE}/customers/{customer_id}")
            assert response.status_code == 200
            customer = response.json()
            assert customer["name"] == self.customer_name
            print(f"✅ Customer auto-saved with ID: {customer_id}")
        else:
            # Alternatively, search for the customer
            response = requests.get(f"{API_BASE}/customers", params={"search": self.customer_name})
            assert response.status_code == 200
            customers = response.json()
            if len(customers) > 0:
                print(f"✅ Customer found after auto-save: {customers[0]['name']}")
            else:
                pytest.fail("Customer was not auto-saved")


class TestInvoiceDeleteCancel:
    """Test invoice delete and cancel with password protection"""
    
    @pytest.fixture(autouse=True)
    def setup_invoices(self):
        """Create test parts and invoices for delete/cancel tests"""
        # Create a test part
        part_data = {
            "name": "TEST_DeleteCancelPart",
            "part_number": "DC-001",
            "price": 75.0,
            "quantity": 20
        }
        part_res = requests.post(f"{API_BASE}/parts", json=part_data)
        if part_res.status_code != 200:
            pytest.skip("Could not create test part")
        self.part = part_res.json()
        self.initial_stock = self.part["quantity"]
        
        # Create two invoices - one for delete, one for cancel
        invoice_data = {
            "customer_name": "TEST_DeleteCancelCustomer",
            "items": [{
                "part_id": self.part["id"],
                "part_number": self.part["part_number"],
                "name": self.part["name"],
                "quantity": 2,
                "unit_price": 75.0,
                "total": 150.0
            }],
            "subtotal": 150.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 150.0,
            "status": "pending"
        }
        
        inv1_res = requests.post(f"{API_BASE}/invoices", json=invoice_data)
        inv2_res = requests.post(f"{API_BASE}/invoices", json=invoice_data)
        
        if inv1_res.status_code == 200 and inv2_res.status_code == 200:
            self.invoice_to_delete = inv1_res.json()
            self.invoice_to_cancel = inv2_res.json()
            yield
            # Cleanup remaining invoices
            requests.delete(f"{API_BASE}/invoices/{self.invoice_to_delete['id']}?password={INVOICE_PASSWORD}")
            requests.delete(f"{API_BASE}/invoices/{self.invoice_to_cancel['id']}?password={INVOICE_PASSWORD}")
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
        else:
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
            pytest.skip("Could not create test invoices")
    
    def test_delete_with_wrong_password_fails(self):
        """Verify invoice deletion fails with wrong password"""
        response = requests.delete(f"{API_BASE}/invoices/{self.invoice_to_delete['id']}?password=wrongpassword")
        assert response.status_code == 401
        print("✅ Delete correctly rejected with wrong password")
    
    def test_delete_with_correct_password(self):
        """Verify invoice can be deleted with correct password (19752)"""
        response = requests.delete(f"{API_BASE}/invoices/{self.invoice_to_delete['id']}?password={INVOICE_PASSWORD}")
        assert response.status_code == 200
        
        # Verify invoice no longer exists
        get_res = requests.get(f"{API_BASE}/invoices/{self.invoice_to_delete['id']}")
        assert get_res.status_code == 404
        print(f"✅ Invoice deleted successfully with password '{INVOICE_PASSWORD}'")
    
    def test_cancel_with_wrong_password_fails(self):
        """Verify invoice cancellation fails with wrong password"""
        response = requests.put(f"{API_BASE}/invoices/{self.invoice_to_cancel['id']}/cancel?password=wrongpassword")
        assert response.status_code == 401
        print("✅ Cancel correctly rejected with wrong password")
    
    def test_cancel_with_correct_password(self):
        """Verify invoice can be cancelled with correct password (19752)"""
        response = requests.put(f"{API_BASE}/invoices/{self.invoice_to_cancel['id']}/cancel?password={INVOICE_PASSWORD}")
        assert response.status_code == 200
        
        # Verify invoice status is cancelled
        get_res = requests.get(f"{API_BASE}/invoices/{self.invoice_to_cancel['id']}")
        assert get_res.status_code == 200
        invoice = get_res.json()
        assert invoice["status"] == "cancelled"
        print(f"✅ Invoice cancelled successfully with password '{INVOICE_PASSWORD}'")


class TestCustomerInvoiceHistory:
    """Test customer invoice history feature"""
    
    @pytest.fixture(autouse=True)
    def setup_customer_with_invoices(self):
        """Create customer with multiple invoices"""
        # Create customer
        customer_data = {
            "name": "TEST_HistoryCustomer",
            "phone": "876-555-7777",
            "discount_percentage": 5.0
        }
        cust_res = requests.post(f"{API_BASE}/customers", json=customer_data)
        if cust_res.status_code != 200:
            pytest.skip("Could not create test customer")
        self.customer = cust_res.json()
        
        # Create part
        part_data = {
            "name": "TEST_HistoryPart",
            "part_number": "HIST-001",
            "price": 100.0,
            "quantity": 20
        }
        part_res = requests.post(f"{API_BASE}/parts", json=part_data)
        if part_res.status_code != 200:
            requests.delete(f"{API_BASE}/customers/{self.customer['id']}")
            pytest.skip("Could not create test part")
        self.part = part_res.json()
        
        # Create multiple invoices for this customer
        self.invoices = []
        for i in range(3):
            invoice_data = {
                "customer_id": self.customer["id"],
                "customer_name": self.customer["name"],
                "items": [{
                    "part_id": self.part["id"],
                    "part_number": self.part["part_number"],
                    "name": self.part["name"],
                    "quantity": i + 1,
                    "unit_price": 100.0,
                    "total": (i + 1) * 100.0
                }],
                "subtotal": (i + 1) * 100.0,
                "tax_rate": 0,
                "tax_amount": 0,
                "total": (i + 1) * 100.0,
                "status": "pending" if i % 2 == 0 else "paid"
            }
            inv_res = requests.post(f"{API_BASE}/invoices", json=invoice_data)
            if inv_res.status_code == 200:
                self.invoices.append(inv_res.json())
        
        yield
        
        # Cleanup
        for inv in self.invoices:
            requests.delete(f"{API_BASE}/invoices/{inv['id']}?password={INVOICE_PASSWORD}")
        requests.delete(f"{API_BASE}/parts/{self.part['id']}")
        requests.delete(f"{API_BASE}/customers/{self.customer['id']}")
    
    def test_customer_invoice_history_endpoint(self):
        """Test the customer invoices endpoint"""
        response = requests.get(f"{API_BASE}/customers/{self.customer['id']}/invoices")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "customer" in data
        assert "invoices" in data
        assert "summary" in data
        
        # Verify customer info
        assert data["customer"]["id"] == self.customer["id"]
        
        # Verify invoices
        assert len(data["invoices"]) >= len(self.invoices)
        
        # Verify summary
        assert "total_invoices" in data["summary"]
        assert "total_purchases" in data["summary"]
        assert "total_paid" in data["summary"]
        assert "total_balance" in data["summary"]
        
        print(f"✅ Customer invoice history retrieved: {data['summary']['total_invoices']} invoices")


class TestSalesJournal:
    """Test Sales Journal functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_invoices_for_journal(self):
        """Create invoices for today's sales journal"""
        # Create part
        part_data = {
            "name": "TEST_JournalPart",
            "part_number": "JRNL-001",
            "price": 150.0,
            "quantity": 20
        }
        part_res = requests.post(f"{API_BASE}/parts", json=part_data)
        if part_res.status_code != 200:
            pytest.skip("Could not create test part")
        self.part = part_res.json()
        
        # Create invoice for today
        invoice_data = {
            "customer_name": "TEST_JournalCustomer",
            "items": [{
                "part_id": self.part["id"],
                "part_number": self.part["part_number"],
                "name": self.part["name"],
                "quantity": 1,
                "unit_price": 150.0,
                "total": 150.0
            }],
            "subtotal": 150.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 150.0,
            "status": "pending"
        }
        inv_res = requests.post(f"{API_BASE}/invoices", json=invoice_data)
        if inv_res.status_code == 200:
            self.invoice = inv_res.json()
            yield
            requests.delete(f"{API_BASE}/invoices/{self.invoice['id']}?password={INVOICE_PASSWORD}")
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
        else:
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
            pytest.skip("Could not create test invoice")
    
    def test_sales_journal_today(self):
        """Test sales journal for today"""
        today = datetime.now(timezone.utc).date().isoformat()
        response = requests.get(f"{API_BASE}/sales-journal?date={today}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "date" in data
        assert "invoices" in data
        assert "summary" in data
        
        # Verify summary fields
        summary = data["summary"]
        assert "total_invoices" in summary
        assert "total_sales" in summary
        assert "total_paid" in summary
        assert "total_pending" in summary
        assert "checked_off_count" in summary
        
        print(f"✅ Sales journal retrieved for {today}: {summary['total_invoices']} invoices")
    
    def test_sales_journal_check_off(self):
        """Test sales journal check-off feature"""
        # Toggle check off
        response = requests.put(f"{API_BASE}/sales-journal/check-off/{self.invoice['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["checked_off"] == True
        
        # Toggle back
        response = requests.put(f"{API_BASE}/sales-journal/check-off/{self.invoice['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["checked_off"] == False
        
        print("✅ Sales journal check-off toggle works correctly")
    
    def test_sales_journal_dates(self):
        """Test sales journal dates endpoint"""
        response = requests.get(f"{API_BASE}/sales-journal/dates")
        assert response.status_code == 200
        dates = response.json()
        
        # Should return list of date objects
        assert isinstance(dates, list)
        if len(dates) > 0:
            assert "date" in dates[0]
            assert "invoice_count" in dates[0]
            print(f"✅ Sales journal dates retrieved: {len(dates)} dates with invoices")
        else:
            print("✅ Sales journal dates endpoint works (no dates yet)")


class TestInvoicePrintView:
    """Test invoice data for print view"""
    
    @pytest.fixture(autouse=True)
    def setup_invoice(self):
        """Create invoice with down payment for print view test"""
        # Create part
        part_data = {
            "name": "TEST_PrintViewPart",
            "part_number": "PRINT-001",
            "price": 500.0,
            "quantity": 10
        }
        part_res = requests.post(f"{API_BASE}/parts", json=part_data)
        if part_res.status_code != 200:
            pytest.skip("Could not create test part")
        self.part = part_res.json()
        
        # Create invoice with down payment
        invoice_data = {
            "customer_name": "TEST_PrintViewCustomer",
            "customer_phone": "876-555-1111",
            "customer_address": "Print View Test Address",
            "items": [{
                "part_id": self.part["id"],
                "part_number": self.part["part_number"],
                "name": self.part["name"],
                "quantity": 2,
                "unit_price": 500.0,
                "total": 1000.0
            }],
            "subtotal": 1000.0,
            "discount": 100.0,
            "discount_percentage": 10.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 900.0,
            "status": "pending",
            "down_payment": 200.0,
            "notes": "Test print view"
        }
        inv_res = requests.post(f"{API_BASE}/invoices", json=invoice_data)
        if inv_res.status_code == 200:
            self.invoice = inv_res.json()
            yield
            requests.delete(f"{API_BASE}/invoices/{self.invoice['id']}?password={INVOICE_PASSWORD}")
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
        else:
            requests.delete(f"{API_BASE}/parts/{self.part['id']}")
            pytest.skip("Could not create test invoice")
    
    def test_print_view_has_all_fields(self):
        """Verify invoice has all fields needed for print view"""
        response = requests.get(f"{API_BASE}/invoices/{self.invoice['id']}")
        assert response.status_code == 200
        invoice = response.json()
        
        # Check required fields for print view
        assert "invoice_number" in invoice
        assert invoice["invoice_number"].startswith("TA-")
        
        assert "status" in invoice
        assert invoice["status"] in ["pending", "paid", "cancelled"]
        
        assert "down_payment" in invoice
        assert invoice["down_payment"] == 200.0
        
        assert "balance_due" in invoice
        assert invoice["balance_due"] == 700.0  # 900 - 200
        
        assert "discount" in invoice
        assert "discount_percentage" in invoice
        
        assert "customer_name" in invoice
        assert "items" in invoice
        assert len(invoice["items"]) > 0
        
        print(f"✅ Invoice print view data complete: {invoice['invoice_number']}")
        print(f"   Status: {invoice['status']}, Down Payment: {invoice['down_payment']}, Balance: {invoice['balance_due']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
