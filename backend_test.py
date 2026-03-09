#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import uuid

class TimelessPartsAPITester:
    def __init__(self, base_url="https://invoice-mgmt-12.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.created_resources = {
            'parts': [],
            'customers': [],
            'invoices': []
        }

    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_base}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                return True, response.json() if response.content else {}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                if response.content:
                    try:
                        error_detail = response.json()
                        error_msg += f" - {error_detail.get('detail', 'No error detail')}"
                    except:
                        error_msg += f" - {response.text[:100]}"
                
                self.log(f"❌ {name} - {error_msg}")
                self.failed_tests.append({'test': name, 'error': error_msg})
                return False, {}
                
        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}")
            self.failed_tests.append({'test': name, 'error': str(e)})
            return False, {}

    def test_api_health(self):
        """Test basic API connectivity"""
        return self.run_test("API Health Check", "GET", "/", 200)

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        return self.run_test("Dashboard Stats", "GET", "/dashboard/stats", 200)

    def test_settings_get(self):
        """Test getting settings"""
        return self.run_test("Get Settings", "GET", "/settings", 200)

    def test_parts_crud(self):
        """Test complete parts CRUD operations"""
        self.log("🔧 Testing Parts CRUD Operations")
        
        # Test get all parts
        success, _ = self.run_test("Get All Parts", "GET", "/parts", 200)
        if not success:
            return False
            
        # Test create part
        part_data = {
            "name": "Test Brake Pad",
            "part_number": f"BP-{uuid.uuid4().hex[:8]}",
            "description": "High performance brake pad for testing",
            "price": 45.99,
            "cost_price": 25.00,
            "quantity": 10,
            "min_stock_level": 5,
            "category": "Brakes",
            "compatible_vehicles": [
                {"make": "Toyota", "model": "Corolla", "year_start": 2015, "year_end": 2020}
            ]
        }
        
        success, part_response = self.run_test("Create Part", "POST", "/parts", 200, part_data)
        if not success:
            return False
        
        part_id = part_response.get('id')
        if part_id:
            self.created_resources['parts'].append(part_id)
        
        # Test get specific part
        success, _ = self.run_test("Get Specific Part", "GET", f"/parts/{part_id}", 200)
        if not success:
            return False
            
        # Test update part
        update_data = {"price": 49.99, "quantity": 15}
        success, _ = self.run_test("Update Part", "PUT", f"/parts/{part_id}", 200, update_data)
        if not success:
            return False
            
        # Test search parts
        success, _ = self.run_test("Search Parts", "GET", "/parts", 200, params={"search": "brake"})
        if not success:
            return False
            
        # Test parts categories
        success, _ = self.run_test("Get Categories", "GET", "/parts/categories/list", 200)
        return success

    def test_customers_crud(self):
        """Test complete customers CRUD operations"""
        self.log("👥 Testing Customers CRUD Operations")
        
        # Test get all customers
        success, _ = self.run_test("Get All Customers", "GET", "/customers", 200)
        if not success:
            return False
            
        # Test create customer
        customer_data = {
            "name": "Test Customer",
            "phone": "876-555-0123",
            "email": "test@example.com",
            "address": "123 Test Street, Kingston, Jamaica"
        }
        
        success, customer_response = self.run_test("Create Customer", "POST", "/customers", 200, customer_data)
        if not success:
            return False
        
        customer_id = customer_response.get('id')
        if customer_id:
            self.created_resources['customers'].append(customer_id)
        
        # Test get specific customer
        success, _ = self.run_test("Get Specific Customer", "GET", f"/customers/{customer_id}", 200)
        if not success:
            return False
            
        # Test update customer
        update_data = {"phone": "876-555-0456"}
        success, _ = self.run_test("Update Customer", "PUT", f"/customers/{customer_id}", 200, update_data)
        if not success:
            return False
            
        # Test search customers
        success, _ = self.run_test("Search Customers", "GET", "/customers", 200, params={"search": "test"})
        return success

    def test_invoices_crud(self):
        """Test complete invoices CRUD operations"""
        self.log("📄 Testing Invoices CRUD Operations")
        
        # Need a part and customer for invoice testing
        if not self.created_resources['parts'] or not self.created_resources['customers']:
            self.log("❌ Cannot test invoices - missing part or customer")
            return False
            
        part_id = self.created_resources['parts'][0]
        customer_id = self.created_resources['customers'][0]
        
        # Test get all invoices
        success, _ = self.run_test("Get All Invoices", "GET", "/invoices", 200)
        if not success:
            return False
            
        # Test create invoice
        invoice_data = {
            "customer_id": customer_id,
            "customer_name": "Test Customer",
            "customer_phone": "876-555-0123",
            "customer_address": "123 Test Street, Kingston, Jamaica",
            "items": [
                {
                    "part_id": part_id,
                    "part_number": "BP-TEST",
                    "name": "Test Brake Pad",
                    "quantity": 2,
                    "unit_price": 49.99,
                    "total": 99.98
                }
            ],
            "subtotal": 99.98,
            "discount": 0,
            "discount_percentage": 0,
            "tax_rate": 15.0,
            "tax_amount": 14.997,
            "total": 114.977,
            "payment_method": "Cash",
            "status": "paid"
        }
        
        success, invoice_response = self.run_test("Create Invoice", "POST", "/invoices", 200, invoice_data)
        if not success:
            return False
        
        invoice_id = invoice_response.get('id')
        if invoice_id:
            self.created_resources['invoices'].append(invoice_id)
        
        # Test get specific invoice
        success, _ = self.run_test("Get Specific Invoice", "GET", f"/invoices/{invoice_id}", 200)
        if not success:
            return False
            
        # Test update invoice status
        update_data = {"status": "completed"}
        success, _ = self.run_test("Update Invoice", "PUT", f"/invoices/{invoice_id}", 200, update_data)
        return success

    def test_dashboard_endpoints(self):
        """Test dashboard specific endpoints"""
        self.log("📊 Testing Dashboard Endpoints")
        
        success, _ = self.run_test("Dashboard Stats", "GET", "/dashboard/stats", 200)
        if not success:
            return False
            
        success, _ = self.run_test("Low Stock Parts", "GET", "/dashboard/low-stock", 200)
        if not success:
            return False
            
        success, _ = self.run_test("Recent Invoices", "GET", "/dashboard/recent-invoices", 200, params={"limit": 5})
        return success

    def test_reports_endpoints(self):
        """Test reports endpoints"""
        self.log("📈 Testing Reports Endpoints")
        
        success, _ = self.run_test("Sales Report", "GET", "/reports/sales", 200)
        if not success:
            return False
            
        success, _ = self.run_test("Inventory Report", "GET", "/reports/inventory", 200)
        return success

    def test_settings_update(self):
        """Test settings update operations"""
        self.log("⚙️ Testing Settings Updates")
        
        # Test company settings update
        company_data = {
            "company_name": "Timeless Parts and Accessories - Test",
            "address": "Lot 36 Bustamante Highway, May Pen, Clarendon",
            "phone": "876-403-8436",
            "email": "timelessautoimportslimited@gmail.com",
            "tax_rate": 15.0,
            "tax_name": "GCT",
            "currency": "JMD",
            "invoice_prefix": "TPA"
        }
        
        success, _ = self.run_test("Update Company Settings", "PUT", "/settings/company", 200, company_data)
        if not success:
            return False
            
        # Test tax settings update
        success, _ = self.run_test("Update Tax Settings", "PUT", "/settings/tax", 200, params={"tax_rate": 15.0, "tax_name": "GCT"})
        return success

    def cleanup_resources(self):
        """Clean up created test resources"""
        self.log("🧹 Cleaning up test resources...")
        
        # Delete created invoices first (they depend on parts/customers)
        for invoice_id in self.created_resources['invoices']:
            try:
                requests.delete(f"{self.api_base}/invoices/{invoice_id}")
            except:
                pass
        
        # Delete created parts
        for part_id in self.created_resources['parts']:
            try:
                requests.delete(f"{self.api_base}/parts/{part_id}")
            except:
                pass
                
        # Delete created customers  
        for customer_id in self.created_resources['customers']:
            try:
                requests.delete(f"{self.api_base}/customers/{customer_id}")
            except:
                pass

    def run_all_tests(self):
        """Run all API tests"""
        self.log("🚀 Starting Timeless Parts & Accessories API Tests")
        self.log(f"🌐 Testing against: {self.base_url}")
        
        try:
            # Basic connectivity
            if not self.test_api_health():
                self.log("❌ API health check failed - aborting tests")
                return False
            
            # Core CRUD operations
            self.test_parts_crud()
            self.test_customers_crud() 
            self.test_invoices_crud()
            
            # Dashboard and reports
            self.test_dashboard_endpoints()
            self.test_reports_endpoints()
            
            # Settings
            self.test_settings_get()
            self.test_settings_update()
            
        finally:
            # Always cleanup
            self.cleanup_resources()
        
        # Print final results
        self.log("\n" + "="*60)
        self.log(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.failed_tests:
            self.log("\n❌ Failed Tests:")
            for test in self.failed_tests:
                self.log(f"  - {test['test']}: {test['error']}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"✨ Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = TimelessPartsAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())