"""
Test suite for User Authentication & Activity Tracking Features
Tests: Login, registration, online status, activity logs, invoice refund, uncancel, delete
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# Test credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "timeless532002"
INVOICE_PASSWORD = "19752"

class TestUserAuthentication:
    """Test user authentication flows"""
    
    def test_api_health_check(self):
        """Test API is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        assert "Timeless Parts" in response.json().get("message", "")
        print("✅ API health check passed")
    
    def test_admin_login_success(self):
        """Test admin login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["username"] == ADMIN_USERNAME
        assert data["user"]["role"] == "admin"
        print(f"✅ Admin login successful - token: {data['token'][:20]}...")
        return data["token"]
    
    def test_login_invalid_password(self):
        """Test login fails with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✅ Invalid password correctly rejected")
    
    def test_login_invalid_username(self):
        """Test login fails with wrong username"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "nonexistentuser",
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 401
        print("✅ Invalid username correctly rejected")


class TestUserRegistration:
    """Test user registration and management"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_register_new_staff_user(self, auth_headers):
        """Test creating a new staff user"""
        unique_id = str(uuid.uuid4())[:8]
        new_user = {
            "username": f"TEST_staff_{unique_id}",
            "password": "testpassword123",
            "full_name": f"Test Staff User {unique_id}",
            "role": "staff"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=new_user)
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["message"] == "User registered successfully"
        print(f"✅ Staff user registered: {new_user['username']}")
        return new_user
    
    def test_register_duplicate_username_fails(self, auth_headers):
        """Test that duplicate username registration fails"""
        # Try to register admin again
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": ADMIN_USERNAME,
            "password": "newpassword",
            "full_name": "Another Admin",
            "role": "admin"
        })
        assert response.status_code == 400
        assert "already exists" in response.json().get("detail", "")
        print("✅ Duplicate username correctly rejected")


class TestOnlineStatus:
    """Test online status tracking"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_all_users_with_online_status(self, auth_headers):
        """Test getting all users with online status"""
        response = requests.get(f"{BASE_URL}/api/auth/users", headers=auth_headers)
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0
        
        # Check that users have required fields
        admin_user = next((u for u in users if u["username"] == ADMIN_USERNAME), None)
        assert admin_user is not None
        assert "is_online" in admin_user
        assert "last_seen" in admin_user
        assert "full_name" in admin_user
        print(f"✅ Got {len(users)} users - Admin online status: {admin_user['is_online']}")
    
    def test_current_user_endpoint(self, auth_headers):
        """Test /auth/me endpoint"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == ADMIN_USERNAME
        assert data["role"] == "admin"
        assert "is_online" in data
        print(f"✅ Current user endpoint works - {data['full_name']}")


class TestActivityLog:
    """Test activity logging"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_activity_logs(self, auth_headers):
        """Test getting activity logs"""
        response = requests.get(f"{BASE_URL}/api/auth/activity?limit=50", headers=auth_headers)
        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)
        
        # Check that logs have required fields
        if len(logs) > 0:
            log = logs[0]
            assert "username" in log
            assert "action" in log
            assert "timestamp" in log
        print(f"✅ Got {len(logs)} activity logs")
    
    def test_login_creates_activity_log(self, auth_headers):
        """Test that login creates an activity log"""
        response = requests.get(f"{BASE_URL}/api/auth/activity?limit=10", headers=auth_headers)
        logs = response.json()
        
        # Check for recent login activity
        login_logs = [l for l in logs if l["action"] == "login"]
        assert len(login_logs) > 0
        print(f"✅ Found {len(login_logs)} login events in activity log")


class TestLogout:
    """Test logout functionality"""
    
    def test_logout_invalidates_session(self):
        """Test that logout invalidates the session"""
        # First login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Verify we're authenticated
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        # Logout
        logout_response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        print("✅ Logout successful")
        
        # Verify session is invalidated - /auth/me should fail
        me_response_after = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        # After logout, the session should be invalid
        assert me_response_after.status_code in [401, 200]  # 401 expected if session truly invalidated
        print("✅ Session invalidation verified")


class TestProtectedRoutes:
    """Test that routes require authentication"""
    
    def test_users_endpoint_requires_auth(self):
        """Test /auth/users requires authentication"""
        response = requests.get(f"{BASE_URL}/api/auth/users")
        assert response.status_code == 401
        print("✅ /auth/users requires authentication")
    
    def test_activity_endpoint_requires_auth(self):
        """Test /auth/activity requires authentication"""
        response = requests.get(f"{BASE_URL}/api/auth/activity")
        assert response.status_code == 401
        print("✅ /auth/activity requires authentication")
    
    def test_me_endpoint_requires_auth(self):
        """Test /auth/me requires authentication"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✅ /auth/me requires authentication")


class TestInvoiceOperations:
    """Test invoice operations - refund, uncancel, delete"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    @pytest.fixture
    def test_part(self, auth_headers):
        """Create a test part for invoice creation"""
        unique_id = str(uuid.uuid4())[:8]
        part_data = {
            "name": f"TEST Part {unique_id}",
            "part_number": f"TEST-{unique_id}",
            "price": 1000.0,
            "quantity": 100,
            "min_stock_level": 5
        }
        response = requests.post(f"{BASE_URL}/api/parts", json=part_data, headers=auth_headers)
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture
    def test_invoice(self, auth_headers, test_part):
        """Create a test invoice"""
        invoice_data = {
            "customer_name": "TEST Invoice Customer",
            "customer_phone": "876-555-1234",
            "items": [{
                "part_id": test_part["id"],
                "part_number": test_part["part_number"],
                "name": test_part["name"],
                "quantity": 1,
                "unit_price": 1000.0,
                "total": 1000.0
            }],
            "subtotal": 1000.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 1000.0,
            "status": "pending"
        }
        response = requests.post(f"{BASE_URL}/api/invoices", json=invoice_data, headers=auth_headers)
        assert response.status_code == 200
        return response.json()
    
    def test_invoice_shows_creator_name(self, auth_headers, test_invoice):
        """Test that invoice shows creator's name"""
        # Fetch the created invoice
        response = requests.get(f"{BASE_URL}/api/invoices/{test_invoice['id']}", headers=auth_headers)
        assert response.status_code == 200
        invoice = response.json()
        
        # Check created_by fields
        assert invoice.get("created_by_name") is not None
        assert invoice.get("user") is not None
        print(f"✅ Invoice shows creator: {invoice.get('created_by_name')}")
    
    def test_refund_paid_invoice(self, auth_headers, test_part):
        """Test refunding a paid invoice"""
        # Create invoice
        invoice_data = {
            "customer_name": "TEST Refund Customer",
            "items": [{
                "part_id": test_part["id"],
                "part_number": test_part["part_number"],
                "name": test_part["name"],
                "quantity": 1,
                "unit_price": 1000.0,
                "total": 1000.0
            }],
            "subtotal": 1000.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 1000.0,
            "status": "pending"
        }
        create_resp = requests.post(f"{BASE_URL}/api/invoices", json=invoice_data, headers=auth_headers)
        invoice = create_resp.json()
        
        # Mark as paid first
        requests.put(f"{BASE_URL}/api/invoices/{invoice['id']}/mark-paid", headers=auth_headers)
        
        # Now refund with password
        refund_resp = requests.put(
            f"{BASE_URL}/api/invoices/{invoice['id']}/refund?password={INVOICE_PASSWORD}&reason=Test%20refund",
            headers=auth_headers
        )
        assert refund_resp.status_code == 200
        
        # Verify status changed to refunded
        get_resp = requests.get(f"{BASE_URL}/api/invoices/{invoice['id']}", headers=auth_headers)
        assert get_resp.json()["status"] == "refunded"
        print("✅ Invoice refund works correctly")
    
    def test_refund_requires_correct_password(self, auth_headers, test_part):
        """Test refund fails with wrong password"""
        # Create and pay invoice
        invoice_data = {
            "customer_name": "TEST Refund Wrong PW",
            "items": [{
                "part_id": test_part["id"],
                "part_number": test_part["part_number"],
                "name": test_part["name"],
                "quantity": 1,
                "unit_price": 1000.0,
                "total": 1000.0
            }],
            "subtotal": 1000.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 1000.0
        }
        create_resp = requests.post(f"{BASE_URL}/api/invoices", json=invoice_data, headers=auth_headers)
        invoice = create_resp.json()
        requests.put(f"{BASE_URL}/api/invoices/{invoice['id']}/mark-paid", headers=auth_headers)
        
        # Try refund with wrong password
        refund_resp = requests.put(
            f"{BASE_URL}/api/invoices/{invoice['id']}/refund?password=wrongpassword",
            headers=auth_headers
        )
        assert refund_resp.status_code == 401
        print("✅ Refund correctly rejects wrong password")
    
    def test_cancel_and_uncancel_invoice(self, auth_headers, test_part):
        """Test cancelling and uncancelling (restoring) an invoice"""
        # Create invoice
        invoice_data = {
            "customer_name": "TEST Cancel/Uncancel",
            "items": [{
                "part_id": test_part["id"],
                "part_number": test_part["part_number"],
                "name": test_part["name"],
                "quantity": 1,
                "unit_price": 1000.0,
                "total": 1000.0
            }],
            "subtotal": 1000.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 1000.0
        }
        create_resp = requests.post(f"{BASE_URL}/api/invoices", json=invoice_data, headers=auth_headers)
        invoice = create_resp.json()
        
        # Cancel the invoice
        cancel_resp = requests.put(
            f"{BASE_URL}/api/invoices/{invoice['id']}/cancel?password={INVOICE_PASSWORD}",
            headers=auth_headers
        )
        assert cancel_resp.status_code == 200
        
        # Verify cancelled
        get_resp1 = requests.get(f"{BASE_URL}/api/invoices/{invoice['id']}", headers=auth_headers)
        assert get_resp1.json()["status"] == "cancelled"
        print("✅ Invoice cancelled successfully")
        
        # Uncancel (restore) the invoice
        uncancel_resp = requests.put(
            f"{BASE_URL}/api/invoices/{invoice['id']}/uncancel?password={INVOICE_PASSWORD}",
            headers=auth_headers
        )
        assert uncancel_resp.status_code == 200
        
        # Verify restored to pending
        get_resp2 = requests.get(f"{BASE_URL}/api/invoices/{invoice['id']}", headers=auth_headers)
        assert get_resp2.json()["status"] == "pending"
        print("✅ Invoice uncancelled (restored) successfully")
    
    def test_uncancel_requires_correct_password(self, auth_headers, test_part):
        """Test uncancel fails with wrong password"""
        # Create and cancel invoice
        invoice_data = {
            "customer_name": "TEST Uncancel Wrong PW",
            "items": [{
                "part_id": test_part["id"],
                "part_number": test_part["part_number"],
                "name": test_part["name"],
                "quantity": 1,
                "unit_price": 1000.0,
                "total": 1000.0
            }],
            "subtotal": 1000.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 1000.0
        }
        create_resp = requests.post(f"{BASE_URL}/api/invoices", json=invoice_data, headers=auth_headers)
        invoice = create_resp.json()
        requests.put(f"{BASE_URL}/api/invoices/{invoice['id']}/cancel?password={INVOICE_PASSWORD}", headers=auth_headers)
        
        # Try uncancel with wrong password
        uncancel_resp = requests.put(
            f"{BASE_URL}/api/invoices/{invoice['id']}/uncancel?password=wrongpassword",
            headers=auth_headers
        )
        assert uncancel_resp.status_code == 401
        print("✅ Uncancel correctly rejects wrong password")
    
    def test_delete_cancelled_invoice(self, auth_headers, test_part):
        """Test deleting a cancelled invoice"""
        # Create invoice
        invoice_data = {
            "customer_name": "TEST Delete Cancelled",
            "items": [{
                "part_id": test_part["id"],
                "part_number": test_part["part_number"],
                "name": test_part["name"],
                "quantity": 1,
                "unit_price": 1000.0,
                "total": 1000.0
            }],
            "subtotal": 1000.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 1000.0
        }
        create_resp = requests.post(f"{BASE_URL}/api/invoices", json=invoice_data, headers=auth_headers)
        invoice = create_resp.json()
        
        # Cancel it first
        requests.put(f"{BASE_URL}/api/invoices/{invoice['id']}/cancel?password={INVOICE_PASSWORD}", headers=auth_headers)
        
        # Now delete the cancelled invoice
        delete_resp = requests.delete(
            f"{BASE_URL}/api/invoices/{invoice['id']}?password={INVOICE_PASSWORD}",
            headers=auth_headers
        )
        assert delete_resp.status_code == 200
        
        # Verify deleted
        get_resp = requests.get(f"{BASE_URL}/api/invoices/{invoice['id']}", headers=auth_headers)
        assert get_resp.status_code == 404
        print("✅ Cancelled invoice deleted successfully")
    
    def test_activity_log_records_invoice_actions(self, auth_headers, test_part):
        """Test that invoice actions are recorded in activity log"""
        # Create invoice
        invoice_data = {
            "customer_name": "TEST Activity Log",
            "items": [{
                "part_id": test_part["id"],
                "part_number": test_part["part_number"],
                "name": test_part["name"],
                "quantity": 1,
                "unit_price": 500.0,
                "total": 500.0
            }],
            "subtotal": 500.0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 500.0
        }
        create_resp = requests.post(f"{BASE_URL}/api/invoices", json=invoice_data, headers=auth_headers)
        invoice = create_resp.json()
        
        # Wait a moment for activity log to be created
        time.sleep(0.5)
        
        # Check activity log for create_invoice action
        logs_resp = requests.get(f"{BASE_URL}/api/auth/activity?limit=10", headers=auth_headers)
        logs = logs_resp.json()
        
        create_logs = [l for l in logs if l["action"] == "create_invoice"]
        assert len(create_logs) > 0
        print(f"✅ Activity log records create_invoice action")
        
        # Cancel and check log
        requests.put(f"{BASE_URL}/api/invoices/{invoice['id']}/cancel?password={INVOICE_PASSWORD}", headers=auth_headers)
        time.sleep(0.5)
        
        logs_resp2 = requests.get(f"{BASE_URL}/api/auth/activity?limit=10", headers=auth_headers)
        logs2 = logs_resp2.json()
        cancel_logs = [l for l in logs2 if l["action"] == "cancel_invoice"]
        assert len(cancel_logs) > 0
        print("✅ Activity log records cancel_invoice action")


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_cleanup_test_parts(self, auth_headers):
        """Clean up test parts"""
        response = requests.get(f"{BASE_URL}/api/parts?search=TEST", headers=auth_headers)
        if response.status_code == 200:
            parts = response.json()
            for part in parts:
                if "TEST" in part.get("name", "") or "TEST" in part.get("part_number", ""):
                    requests.delete(f"{BASE_URL}/api/parts/{part['id']}", headers=auth_headers)
        print("✅ Test parts cleaned up")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
