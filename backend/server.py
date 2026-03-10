# App Version: 4.0.0 - User Authentication & Activity Tracking
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Query, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import base64
import hashlib
import secrets
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Admin password from environment variable (MUST be after load_dotenv)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change_me_in_production')
INVOICE_PASSWORD = os.environ.get('INVOICE_PASSWORD', 'change_me_in_production')
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))

def verify_password(password: str) -> bool:
    return password == ADMIN_PASSWORD

def verify_invoice_password(password: str) -> bool:
    return password == INVOICE_PASSWORD

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Timeless Parts and Accessories API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)

# ==================== USER MODELS ====================

class UserBase(BaseModel):
    username: str
    full_name: str
    role: str = "staff"  # admin or staff

class UserCreate(UserBase):
    password: str

class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    last_seen: Optional[datetime] = None
    is_online: bool = False

class UserLogin(BaseModel):
    username: str
    password: str

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    is_active: bool = True

class ActivityLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    username: str
    action: str  # login, logout, create_invoice, delete_invoice, etc.
    details: Optional[str] = None
    entity_type: Optional[str] = None  # invoice, part, customer, etc.
    entity_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== MODELS ====================

class VehicleCompatibility(BaseModel):
    make: str
    model: str
    year_start: Optional[int] = None
    year_end: Optional[int] = None

class PartBase(BaseModel):
    name: str
    part_number: str
    description: Optional[str] = None
    price: float
    cost_price: Optional[float] = None
    quantity: int = 0
    min_stock_level: int = 5
    category: Optional[str] = None
    image_url: Optional[str] = None
    compatible_vehicles: List[VehicleCompatibility] = []

class PartCreate(PartBase):
    pass

class Part(PartBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PartUpdate(BaseModel):
    name: Optional[str] = None
    part_number: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    quantity: Optional[int] = None
    min_stock_level: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    compatible_vehicles: Optional[List[VehicleCompatibility]] = None

class CustomerBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    discount_percentage: float = 0  # Customer-specific discount

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    discount_percentage: Optional[float] = None

class InvoiceItem(BaseModel):
    part_id: str
    part_number: str
    name: str
    quantity: int
    unit_price: float
    total: float

class InvoiceBase(BaseModel):
    customer_id: Optional[str] = None
    customer_name: str
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    items: List[InvoiceItem]
    subtotal: float
    discount: float = 0
    discount_percentage: float = 0
    tax_rate: float = 0
    tax_amount: float
    total: float
    payment_method: Optional[str] = "Cash"
    notes: Optional[str] = None
    status: str = "pending"
    down_payment: float = 0
    amount_paid: float = 0
    balance_due: float = 0
    save_customer: bool = False  # Flag to auto-save new customer

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: str = "Admin"
    created_by_id: Optional[str] = None
    created_by_name: Optional[str] = None
    checked_off: bool = False  # For Sales Journal check-off feature
    checked_off_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    refund_reason: Optional[str] = None

class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    down_payment: Optional[float] = None
    amount_paid: Optional[float] = None
    balance_due: Optional[float] = None
    checked_off: Optional[bool] = None
    refund_reason: Optional[str] = None

class CompanySettings(BaseModel):
    company_name: str = "Timeless Parts and Accessories"
    address: str = "Lot 36 Bustamante Highway, May Pen, Clarendon"
    phone: str = "876-403-8436"
    email: str = "timelessautoimportslimited@gmail.com"
    logo_url: str = "https://customer-assets.emergentagent.com/job_c8ea836d-f376-4793-85ac-d42fefdf5d7d/artifacts/mxjzjbvw_WhatsApp%20Image%202026-03-05%20at%204.13.42%20PM.jpeg"
    tax_rate: float = 0
    tax_name: str = "GCT"
    currency: str = "JMD"
    invoice_prefix: str = "TA"

class PolicySettings(BaseModel):
    sales_return_policy: List[str] = [
        "Acceptance of proposed return solely at the discretion of Timeless Parts and Accessories.",
        "Items being returned must be accompanied by invoice.",
        "Items must be returned within 30 days of invoice date.",
        "Items must be returned in original packaging, unaltered/undamaged and in re-saleable condition.",
        "All returns will attract a 10% handling charge.",
        "No refund or exchange on electrical parts.",
        "No returns on special order items."
    ]
    privacy_policy: List[str] = [
        "Timeless Parts and Accessories (\"Company\", \"We\", \"Us\") is committed to protecting the privacy and security of your personal information. We collect, use, and disclose your personal information in accordance with the Data Protection Act of Jamaica.",
        "This privacy clause applies to the personal information that we collect from you on our invoices. This personal information may include your name, address, phone number, email address, and payment information.",
        "We use your personal information to process your invoice and provide you with our services. We may also use your personal information to communicate with you about your invoice, to improve our services, and to comply with legal obligations.",
        "We will not disclose your personal information to any third party without your consent, except as required by law. We will take all reasonable steps to protect your personal information from unauthorized access, use, or disclosure.",
        "You have the right to access, correct, or erase your personal information. You also have the right to object to the processing of your personal information. To exercise any of these rights, please contact us at Lot 36 Bustamante Highway, May Pen, Clarendon or 876-403-8436.",
        "By providing us with your personal information on our invoices, you consent to the collection, use, and disclosure of your personal information in accordance with this privacy clause."
    ]

class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "settings"
    company: CompanySettings = CompanySettings()
    policies: PolicySettings = PolicySettings()
    invoice_counter: int = 1

class Vehicle(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    make: str
    model: str
    years: List[int] = []

class VehicleCreate(BaseModel):
    make: str
    model: str
    years: List[int] = []

class PasswordVerify(BaseModel):
    password: str

# ==================== HELPER FUNCTIONS ====================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """Get current user from token, returns None if not authenticated"""
    if not credentials:
        return None
    
    token = credentials.credentials
    session = await db.sessions.find_one({
        "token": token,
        "is_active": True,
        "expires_at": {"$gt": datetime.now(timezone.utc).isoformat()}
    }, {"_id": 0})
    
    if not session:
        return None
    
    user = await db.users.find_one({"id": session["user_id"]}, {"_id": 0})
    if not user:
        return None
    
    # Update last seen
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_seen": datetime.now(timezone.utc).isoformat(), "is_online": True}}
    )
    
    return user

async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Require authentication, raises 401 if not authenticated"""
    user = await get_current_user(credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

async def log_activity(user_id: str, username: str, action: str, details: str = None, entity_type: str = None, entity_id: str = None):
    """Log user activity"""
    log = ActivityLog(
        user_id=user_id,
        username=username,
        action=action,
        details=details,
        entity_type=entity_type,
        entity_id=entity_id
    )
    doc = log.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.activity_logs.insert_one(doc)

async def get_next_invoice_number():
    settings = await db.settings.find_one({"id": "settings"}, {"_id": 0})
    if not settings:
        settings = Settings().model_dump()
        settings['company'] = dict(settings['company'])
        settings['policies'] = dict(settings['policies'])
        await db.settings.insert_one(settings)
    
    counter = settings.get('invoice_counter', 1)
    prefix = settings.get('company', {}).get('invoice_prefix', 'TA')
    # Use shorter format: TA-01, TA-02, etc.
    invoice_number = f"{prefix}-{counter:02d}"
    
    await db.settings.update_one(
        {"id": "settings"},
        {"$inc": {"invoice_counter": 1}}
    )
    
    return invoice_number

async def init_settings():
    settings = await db.settings.find_one({"id": "settings"}, {"_id": 0})
    if not settings:
        default_settings = Settings()
        doc = default_settings.model_dump()
        doc['company'] = dict(doc['company'])
        doc['policies'] = dict(doc['policies'])
        await db.settings.insert_one(doc)
        return default_settings
    return settings

# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "Timeless Parts and Accessories API"}

# ==================== USER AUTH ROUTES ====================

@api_router.post("/auth/register")
async def register_user(user_data: UserCreate):
    """Register a new user (admin only in production)"""
    # Check if username exists
    existing = await db.users.find_one({"username": user_data.username}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    user = User(
        username=user_data.username,
        full_name=user_data.full_name,
        role=user_data.role
    )
    doc = user.model_dump()
    doc['password_hash'] = hash_password(user_data.password)
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('last_seen'):
        doc['last_seen'] = doc['last_seen'].isoformat()
    
    await db.users.insert_one(doc)
    
    # Log activity
    await log_activity(user.id, user.username, "user_registered", f"New user registered: {user.full_name}")
    
    return {"message": "User registered successfully", "user_id": user.id}

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    """Login and get session token"""
    user = await db.users.find_one({"username": credentials.username}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not check_password(credentials.password, user.get('password_hash', '')):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not user.get('is_active', True):
        raise HTTPException(status_code=401, detail="Account is disabled")
    
    # Create session
    token = secrets.token_urlsafe(32)
    session = UserSession(
        user_id=user['id'],
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
    )
    session_doc = session.model_dump()
    session_doc['created_at'] = session_doc['created_at'].isoformat()
    session_doc['expires_at'] = session_doc['expires_at'].isoformat()
    
    await db.sessions.insert_one(session_doc)
    
    # Update user online status
    await db.users.update_one(
        {"id": user['id']},
        {"$set": {"is_online": True, "last_seen": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Log activity
    await log_activity(user['id'], user['username'], "login", "User logged in")
    
    return {
        "token": token,
        "user": {
            "id": user['id'],
            "username": user['username'],
            "full_name": user['full_name'],
            "role": user['role']
        }
    }

@api_router.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout and invalidate session"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = credentials.credentials
    session = await db.sessions.find_one({"token": token}, {"_id": 0})
    
    if session:
        # Invalidate session
        await db.sessions.update_one({"token": token}, {"$set": {"is_active": False}})
        
        # Update user online status
        await db.users.update_one(
            {"id": session['user_id']},
            {"$set": {"is_online": False, "last_seen": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Get user for logging
        user = await db.users.find_one({"id": session['user_id']}, {"_id": 0})
        if user:
            await log_activity(user['id'], user['username'], "logout", "User logged out")
    
    return {"message": "Logged out successfully"}

@api_router.get("/auth/me")
async def get_current_user_info(user: dict = Depends(require_auth)):
    """Get current logged in user info"""
    return {
        "id": user['id'],
        "username": user['username'],
        "full_name": user['full_name'],
        "role": user['role'],
        "is_online": user.get('is_online', False)
    }

@api_router.get("/auth/users")
async def get_all_users(user: dict = Depends(require_auth)):
    """Get all users with online status"""
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(100)
    
    for u in users:
        if isinstance(u.get('created_at'), str):
            u['created_at'] = datetime.fromisoformat(u['created_at'])
        if isinstance(u.get('last_seen'), str):
            u['last_seen'] = datetime.fromisoformat(u['last_seen'])
        
        # Check if session is still valid (consider offline if last seen > 5 min ago)
        if u.get('last_seen'):
            last_seen = u['last_seen'] if isinstance(u['last_seen'], datetime) else datetime.fromisoformat(str(u['last_seen']))
            if datetime.now(timezone.utc) - last_seen > timedelta(minutes=5):
                u['is_online'] = False
    
    return users

@api_router.get("/auth/activity")
async def get_activity_logs(
    user: dict = Depends(require_auth),
    limit: int = 50,
    user_id: Optional[str] = None
):
    """Get activity logs"""
    query = {}
    if user_id:
        query["user_id"] = user_id
    
    logs = await db.activity_logs.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    
    for log in logs:
        if isinstance(log.get('timestamp'), str):
            log['timestamp'] = datetime.fromisoformat(log['timestamp'])
    
    return logs

@api_router.put("/auth/users/{user_id}/toggle-active")
async def toggle_user_active(user_id: str, user: dict = Depends(require_auth)):
    """Enable/disable a user account"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    target_user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_status = not target_user.get('is_active', True)
    await db.users.update_one({"id": user_id}, {"$set": {"is_active": new_status}})
    
    await log_activity(user['id'], user['username'], "toggle_user", f"{'Enabled' if new_status else 'Disabled'} user: {target_user['username']}")
    
    return {"message": f"User {'enabled' if new_status else 'disabled'}", "is_active": new_status}

@api_router.post("/verify-password")
async def verify_admin_password(data: PasswordVerify):
    if verify_password(data.password):
        return {"verified": True}
    raise HTTPException(status_code=401, detail="Invalid password")

@api_router.post("/verify-invoice-password")
async def verify_invoice_admin_password(data: PasswordVerify):
    """Verify password for invoice operations (delete/cancel)"""
    if verify_invoice_password(data.password):
        return {"verified": True}
    raise HTTPException(status_code=401, detail="Invalid password")

# ---- Parts Routes ----

@api_router.get("/parts", response_model=List[Part])
async def get_parts(
    search: Optional[str] = None,
    category: Optional[str] = None,
    low_stock: Optional[bool] = None,
    vehicle_make: Optional[str] = None,
    vehicle_model: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    # Cap limit to prevent memory issues
    limit = min(limit, 500)
    
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"part_number": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    if category:
        query["category"] = category
    
    if vehicle_make:
        query["compatible_vehicles.make"] = {"$regex": vehicle_make, "$options": "i"}
    
    if vehicle_model:
        query["compatible_vehicles.model"] = {"$regex": vehicle_model, "$options": "i"}
    
    # Use aggregation for low_stock filter
    if low_stock:
        pipeline = [
            {"$match": query} if query else {"$match": {}},
            {
                "$match": {
                    "$expr": {
                        "$lte": [
                            {"$ifNull": ["$quantity", 0]},
                            {"$ifNull": ["$min_stock_level", 5]}
                        ]
                    }
                }
            },
            {"$skip": skip},
            {"$limit": limit},
            {"$project": {"_id": 0}}
        ]
        parts = await db.parts.aggregate(pipeline).to_list(limit)
    else:
        parts = await db.parts.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    
    for part in parts:
        if isinstance(part.get('created_at'), str):
            part['created_at'] = datetime.fromisoformat(part['created_at'])
        if isinstance(part.get('updated_at'), str):
            part['updated_at'] = datetime.fromisoformat(part['updated_at'])
    
    return parts

@api_router.get("/parts/categories/list")
async def get_categories():
    categories = await db.parts.distinct("category")
    return [c for c in categories if c]

@api_router.get("/parts/frequently-used")
async def get_frequently_used_parts(limit: int = 6):
    """Get most frequently sold parts based on invoice history"""
    # Aggregate invoice items to count part sales
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.part_id",
            "total_sold": {"$sum": "$items.quantity"},
            "times_ordered": {"$sum": 1}
        }},
        {"$sort": {"total_sold": -1}},
        {"$limit": limit}
    ]
    
    sales_data = await db.invoices.aggregate(pipeline).to_list(limit)
    
    if not sales_data:
        # If no sales history, return parts with highest stock
        parts = await db.parts.find({}, {"_id": 0}).sort("quantity", -1).to_list(limit)
        return parts
    
    # Get full part details for the frequently sold parts
    part_ids = [s["_id"] for s in sales_data]
    parts = await db.parts.find({"id": {"$in": part_ids}}, {"_id": 0}).to_list(limit)
    
    # Create a lookup for sales data
    sales_lookup = {s["_id"]: s for s in sales_data}
    
    # Add sales info to parts and sort by total sold
    for part in parts:
        sale_info = sales_lookup.get(part["id"], {})
        part["total_sold"] = sale_info.get("total_sold", 0)
        part["times_ordered"] = sale_info.get("times_ordered", 0)
    
    # Sort by total sold
    parts.sort(key=lambda x: x.get("total_sold", 0), reverse=True)
    
    # Convert datetime fields
    for part in parts:
        if isinstance(part.get('created_at'), str):
            part['created_at'] = datetime.fromisoformat(part['created_at'])
        if isinstance(part.get('updated_at'), str):
            part['updated_at'] = datetime.fromisoformat(part['updated_at'])
    
    return parts

@api_router.get("/parts/{part_id}", response_model=Part)
async def get_part(part_id: str):
    part = await db.parts.find_one({"id": part_id}, {"_id": 0})
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    if isinstance(part.get('created_at'), str):
        part['created_at'] = datetime.fromisoformat(part['created_at'])
    if isinstance(part.get('updated_at'), str):
        part['updated_at'] = datetime.fromisoformat(part['updated_at'])
    
    return part

@api_router.post("/parts", response_model=Part)
async def create_part(part: PartCreate):
    part_obj = Part(**part.model_dump())
    doc = part_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    doc['compatible_vehicles'] = [dict(v) for v in doc['compatible_vehicles']]
    
    await db.parts.insert_one(doc)
    return part_obj

@api_router.put("/parts/{part_id}", response_model=Part)
async def update_part(part_id: str, part_update: PartUpdate):
    existing = await db.parts.find_one({"id": part_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Part not found")
    
    update_data = {k: v for k, v in part_update.model_dump().items() if v is not None}
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    if 'compatible_vehicles' in update_data:
        update_data['compatible_vehicles'] = [dict(v) for v in update_data['compatible_vehicles']]
    
    await db.parts.update_one({"id": part_id}, {"$set": update_data})
    
    updated = await db.parts.find_one({"id": part_id}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    if isinstance(updated.get('updated_at'), str):
        updated['updated_at'] = datetime.fromisoformat(updated['updated_at'])
    
    return updated

@api_router.delete("/parts/{part_id}")
async def delete_part(part_id: str):
    result = await db.parts.delete_one({"id": part_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Part not found")
    return {"message": "Part deleted successfully"}

@api_router.post("/parts/{part_id}/adjust-stock")
async def adjust_stock(part_id: str, adjustment: int):
    part = await db.parts.find_one({"id": part_id}, {"_id": 0})
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    new_quantity = part.get('quantity', 0) + adjustment
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative")
    
    await db.parts.update_one(
        {"id": part_id},
        {"$set": {"quantity": new_quantity, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Stock adjusted", "new_quantity": new_quantity}

# ---- Customer Routes ----

@api_router.get("/customers", response_model=List[Customer])
async def get_customers(search: Optional[str] = None, skip: int = 0, limit: int = 100):
    # Cap limit
    limit = min(limit, 500)
    
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    customers = await db.customers.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    
    for customer in customers:
        if isinstance(customer.get('created_at'), str):
            customer['created_at'] = datetime.fromisoformat(customer['created_at'])
        # Ensure discount_percentage has default value
        if 'discount_percentage' not in customer:
            customer['discount_percentage'] = 0
    
    return customers

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if isinstance(customer.get('created_at'), str):
        customer['created_at'] = datetime.fromisoformat(customer['created_at'])
    
    # Ensure discount_percentage has default value
    if 'discount_percentage' not in customer:
        customer['discount_percentage'] = 0
    
    return customer

@api_router.get("/customers/{customer_id}/invoices")
async def get_customer_invoices(customer_id: str, skip: int = 0, limit: int = 50):
    """Get all invoices for a specific customer"""
    # Verify customer exists
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get invoices by customer_id OR by customer name (for walk-in customers)
    customer_name = customer.get('name', '')
    query = {
        "$or": [
            {"customer_id": customer_id},
            {"customer_name": {"$regex": f"^{customer_name}$", "$options": "i"}}
        ]
    }
    
    invoices = await db.invoices.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    for invoice in invoices:
        if isinstance(invoice.get('created_at'), str):
            invoice['created_at'] = datetime.fromisoformat(invoice['created_at'])
    
    # Calculate totals
    total_purchases = sum(inv.get('total', 0) for inv in invoices)
    total_paid = sum(inv.get('amount_paid', inv.get('total', 0)) if inv.get('status') == 'paid' else inv.get('amount_paid', 0) for inv in invoices)
    total_balance = sum(inv.get('balance_due', 0) for inv in invoices)
    
    return {
        "customer": customer,
        "invoices": invoices,
        "summary": {
            "total_invoices": len(invoices),
            "total_purchases": total_purchases,
            "total_paid": total_paid,
            "total_balance": total_balance
        }
    }

@api_router.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    customer_obj = Customer(**customer.model_dump())
    doc = customer_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.customers.insert_one(doc)
    return customer_obj

@api_router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer_update: CustomerUpdate):
    existing = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = {k: v for k, v in customer_update.model_dump().items() if v is not None}
    
    await db.customers.update_one({"id": customer_id}, {"$set": update_data})
    
    updated = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    
    return updated

@api_router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str):
    result = await db.customers.delete_one({"id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}

# ---- Invoice Routes ----

@api_router.get("/invoices", response_model=List[Invoice])
async def get_invoices(
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    # Cap limit
    limit = min(limit, 500)
    
    query = {}
    
    if customer_id:
        query["customer_id"] = customer_id
    
    if status:
        query["status"] = status
    
    if start_date:
        query["created_at"] = {"$gte": start_date}
    
    if end_date:
        if "created_at" in query:
            query["created_at"]["$lte"] = end_date
        else:
            query["created_at"] = {"$lte": end_date}
    
    invoices = await db.invoices.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    for invoice in invoices:
        if isinstance(invoice.get('created_at'), str):
            invoice['created_at'] = datetime.fromisoformat(invoice['created_at'])
    
    return invoices

@api_router.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: str):
    invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if isinstance(invoice.get('created_at'), str):
        invoice['created_at'] = datetime.fromisoformat(invoice['created_at'])
    
    return invoice

@api_router.post("/invoices", response_model=Invoice)
async def create_invoice(invoice: InvoiceCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    invoice_number = await get_next_invoice_number()
    
    # Get current user if authenticated
    current_user = await get_current_user(credentials)
    created_by_id = current_user['id'] if current_user else None
    created_by_name = current_user['full_name'] if current_user else "Guest"
    
    # Calculate balance due based on down payment
    balance_due = invoice.total - (invoice.down_payment or 0) - (invoice.amount_paid or 0)
    
    # Auto-save customer if flag is set and no customer_id
    customer_id = invoice.customer_id
    if invoice.save_customer and not customer_id and invoice.customer_name:
        # Check if customer with this name already exists
        existing_customer = await db.customers.find_one(
            {"name": {"$regex": f"^{invoice.customer_name}$", "$options": "i"}},
            {"_id": 0}
        )
        if existing_customer:
            customer_id = existing_customer.get('id')
        else:
            # Create new customer
            new_customer = Customer(
                name=invoice.customer_name,
                phone=invoice.customer_phone,
                address=invoice.customer_address,
                discount_percentage=0
            )
            customer_doc = new_customer.model_dump()
            customer_doc['created_at'] = customer_doc['created_at'].isoformat()
            await db.customers.insert_one(customer_doc)
            customer_id = new_customer.id
    
    # Exclude fields we're setting explicitly to avoid duplicate kwargs
    exclude_fields = ('save_customer', 'customer_id', 'balance_due', 'amount_paid')
    invoice_data = {k: v for k, v in invoice.model_dump().items() if k not in exclude_fields}
    invoice_obj = Invoice(
        **invoice_data,
        invoice_number=invoice_number,
        customer_id=customer_id,
        balance_due=balance_due,
        amount_paid=invoice.down_payment or 0,
        created_by_id=created_by_id,
        created_by_name=created_by_name,
        user=created_by_name
    )
    doc = invoice_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['items'] = [dict(item) for item in doc['items']]
    if doc.get('checked_off_at'):
        doc['checked_off_at'] = doc['checked_off_at'].isoformat()
    if doc.get('refunded_at'):
        doc['refunded_at'] = doc['refunded_at'].isoformat()
    
    # Update stock for each item
    for item in invoice.items:
        await db.parts.update_one(
            {"id": item.part_id},
            {"$inc": {"quantity": -item.quantity}}
        )
    
    await db.invoices.insert_one(doc)
    
    # Log activity
    if current_user:
        await log_activity(
            current_user['id'], 
            current_user['username'], 
            "create_invoice", 
            f"Created invoice {invoice_number} for {invoice.customer_name}",
            "invoice",
            invoice_obj.id
        )
    
    return invoice_obj

@api_router.put("/invoices/{invoice_id}", response_model=Invoice)
async def update_invoice(invoice_id: str, invoice_update: InvoiceUpdate):
    existing = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    update_data = {k: v for k, v in invoice_update.model_dump().items() if v is not None}
    
    # Handle check_off timestamp
    if 'checked_off' in update_data:
        if update_data['checked_off']:
            update_data['checked_off_at'] = datetime.now(timezone.utc).isoformat()
        else:
            update_data['checked_off_at'] = None
    
    # Recalculate balance_due if payment amounts change
    if 'amount_paid' in update_data or 'down_payment' in update_data:
        total = existing.get('total', 0)
        down_payment = update_data.get('down_payment', existing.get('down_payment', 0))
        amount_paid = update_data.get('amount_paid', existing.get('amount_paid', 0))
        update_data['balance_due'] = total - down_payment - amount_paid
        
        # Auto-mark as paid if balance is 0 or less
        if update_data['balance_due'] <= 0:
            update_data['status'] = 'paid'
    
    await db.invoices.update_one({"id": invoice_id}, {"$set": update_data})
    
    updated = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    
    return updated

@api_router.put("/invoices/{invoice_id}/mark-paid")
async def mark_invoice_paid(invoice_id: str, amount: Optional[float] = None):
    """Mark an invoice as paid"""
    existing = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    total = existing.get('total', 0)
    update_data = {
        'status': 'paid',
        'amount_paid': amount if amount else total,
        'balance_due': 0
    }
    
    await db.invoices.update_one({"id": invoice_id}, {"$set": update_data})
    return {"message": "Invoice marked as paid"}

@api_router.put("/invoices/{invoice_id}/add-payment")
async def add_invoice_payment(invoice_id: str, amount: float):
    """Add a payment to an invoice"""
    existing = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    current_paid = existing.get('amount_paid', 0) + existing.get('down_payment', 0)
    new_paid = current_paid + amount
    total = existing.get('total', 0)
    new_balance = total - new_paid
    
    update_data = {
        'amount_paid': new_paid,
        'balance_due': max(0, new_balance)
    }
    
    # Auto-mark as paid if fully paid
    if new_balance <= 0:
        update_data['status'] = 'paid'
    
    await db.invoices.update_one({"id": invoice_id}, {"$set": update_data})
    return {"message": "Payment added", "new_balance": max(0, new_balance)}

@api_router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str, password: str = Query(...), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete an invoice (requires invoice password) - can delete cancelled invoices too"""
    if not verify_invoice_password(password):
        raise HTTPException(status_code=401, detail="Invalid invoice password")
    
    existing = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Only restore stock if not already cancelled (stock was already restored on cancel)
    if existing.get('status') != 'cancelled':
        for item in existing.get('items', []):
            await db.parts.update_one(
                {"id": item.get('part_id')},
                {"$inc": {"quantity": item.get('quantity', 0)}}
            )
    
    await db.invoices.delete_one({"id": invoice_id})
    
    # Log activity
    current_user = await get_current_user(credentials)
    if current_user:
        await log_activity(
            current_user['id'],
            current_user['username'],
            "delete_invoice",
            f"Deleted invoice {existing.get('invoice_number')}",
            "invoice",
            invoice_id
        )
    
    return {"message": "Invoice deleted successfully"}

@api_router.put("/invoices/{invoice_id}/cancel")
async def cancel_invoice(invoice_id: str, password: str = Query(...), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Cancel an invoice (requires invoice password) - keeps record but marks as cancelled"""
    if not verify_invoice_password(password):
        raise HTTPException(status_code=401, detail="Invalid invoice password")
    
    existing = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if existing.get('status') == 'cancelled':
        raise HTTPException(status_code=400, detail="Invoice is already cancelled")
    
    # Restore stock for each item
    for item in existing.get('items', []):
        await db.parts.update_one(
            {"id": item.get('part_id')},
            {"$inc": {"quantity": item.get('quantity', 0)}}
        )
    
    await db.invoices.update_one(
        {"id": invoice_id},
        {"$set": {"status": "cancelled"}}
    )
    
    # Log activity
    current_user = await get_current_user(credentials)
    if current_user:
        await log_activity(
            current_user['id'],
            current_user['username'],
            "cancel_invoice",
            f"Cancelled invoice {existing.get('invoice_number')}",
            "invoice",
            invoice_id
        )
    
    return {"message": "Invoice cancelled successfully"}

@api_router.put("/invoices/{invoice_id}/uncancel")
async def uncancel_invoice(invoice_id: str, password: str = Query(...), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Restore a cancelled invoice back to pending (requires invoice password)"""
    if not verify_invoice_password(password):
        raise HTTPException(status_code=401, detail="Invalid invoice password")
    
    existing = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if existing.get('status') != 'cancelled':
        raise HTTPException(status_code=400, detail="Invoice is not cancelled")
    
    # Deduct stock again for each item
    for item in existing.get('items', []):
        await db.parts.update_one(
            {"id": item.get('part_id')},
            {"$inc": {"quantity": -item.get('quantity', 0)}}
        )
    
    await db.invoices.update_one(
        {"id": invoice_id},
        {"$set": {"status": "pending"}}
    )
    
    # Log activity
    current_user = await get_current_user(credentials)
    if current_user:
        await log_activity(
            current_user['id'],
            current_user['username'],
            "uncancel_invoice",
            f"Restored invoice {existing.get('invoice_number')} from cancelled to pending",
            "invoice",
            invoice_id
        )
    
    return {"message": "Invoice restored to pending"}

@api_router.put("/invoices/{invoice_id}/refund")
async def refund_invoice(invoice_id: str, password: str = Query(...), reason: Optional[str] = None, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refund an invoice (requires invoice password)"""
    if not verify_invoice_password(password):
        raise HTTPException(status_code=401, detail="Invalid invoice password")
    
    existing = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if existing.get('status') == 'refunded':
        raise HTTPException(status_code=400, detail="Invoice is already refunded")
    
    if existing.get('status') == 'cancelled':
        raise HTTPException(status_code=400, detail="Cannot refund a cancelled invoice")
    
    # Restore stock for each item
    for item in existing.get('items', []):
        await db.parts.update_one(
            {"id": item.get('part_id')},
            {"$inc": {"quantity": item.get('quantity', 0)}}
        )
    
    await db.invoices.update_one(
        {"id": invoice_id},
        {"$set": {
            "status": "refunded",
            "refunded_at": datetime.now(timezone.utc).isoformat(),
            "refund_reason": reason
        }}
    )
    
    # Log activity
    current_user = await get_current_user(credentials)
    if current_user:
        await log_activity(
            current_user['id'],
            current_user['username'],
            "refund_invoice",
            f"Refunded invoice {existing.get('invoice_number')}" + (f": {reason}" if reason else ""),
            "invoice",
            invoice_id
        )
    
    return {"message": "Invoice refunded successfully"}

@api_router.delete("/invoices/clear-all")
async def clear_all_invoices():
    """Clear all invoices and reset counter"""
    await db.invoices.delete_many({})
    await db.settings.update_one(
        {"id": "settings"},
        {"$set": {"invoice_counter": 1}}
    )
    return {"message": "All invoices cleared and counter reset"}

# ---- Sales Journal Routes ----

@api_router.get("/sales-journal")
async def get_sales_journal(date: Optional[str] = None):
    """Get daily sales journal - all transactions for a specific day"""
    if not date:
        date = datetime.now(timezone.utc).date().isoformat()
    
    # Get all invoices for the specified date
    query = {"created_at": {"$regex": f"^{date}"}}
    invoices = await db.invoices.find(query, {"_id": 0}).sort("created_at", 1).to_list(1000)
    
    for invoice in invoices:
        if isinstance(invoice.get('created_at'), str):
            invoice['created_at'] = datetime.fromisoformat(invoice['created_at'])
    
    # Calculate summary
    total_sales = sum(inv.get('total', 0) for inv in invoices if inv.get('status') != 'cancelled')
    total_paid = sum(inv.get('amount_paid', 0) + inv.get('down_payment', 0) for inv in invoices if inv.get('status') != 'cancelled')
    total_pending = sum(inv.get('balance_due', 0) for inv in invoices if inv.get('status') == 'pending')
    total_items_sold = sum(sum(item.get('quantity', 0) for item in inv.get('items', [])) for inv in invoices if inv.get('status') != 'cancelled')
    checked_off_count = sum(1 for inv in invoices if inv.get('checked_off'))
    
    return {
        "date": date,
        "invoices": invoices,
        "summary": {
            "total_invoices": len(invoices),
            "checked_off_count": checked_off_count,
            "unchecked_count": len(invoices) - checked_off_count,
            "total_sales": total_sales,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "total_items_sold": total_items_sold
        }
    }

@api_router.put("/sales-journal/check-off/{invoice_id}")
async def toggle_invoice_check_off(invoice_id: str):
    """Toggle check-off status for an invoice in the sales journal"""
    existing = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    current_status = existing.get('checked_off', False)
    new_status = not current_status
    
    update_data = {
        'checked_off': new_status,
        'checked_off_at': datetime.now(timezone.utc).isoformat() if new_status else None
    }
    
    await db.invoices.update_one({"id": invoice_id}, {"$set": update_data})
    return {"message": f"Invoice {'checked off' if new_status else 'unchecked'}", "checked_off": new_status}

@api_router.get("/sales-journal/dates")
async def get_sales_journal_dates(limit: int = 30):
    """Get list of dates that have invoices"""
    pipeline = [
        {
            "$group": {
                "_id": {"$substr": ["$created_at", 0, 10]},
                "count": {"$sum": 1},
                "total": {"$sum": "$total"}
            }
        },
        {"$sort": {"_id": -1}},
        {"$limit": limit}
    ]
    
    dates = await db.invoices.aggregate(pipeline).to_list(limit)
    return [{"date": d["_id"], "invoice_count": d["count"], "total_sales": d["total"]} for d in dates]

# ---- Settings Routes ----

@api_router.get("/settings")
async def get_settings():
    settings = await db.settings.find_one({"id": "settings"}, {"_id": 0})
    if not settings:
        settings = await init_settings()
        if hasattr(settings, 'model_dump'):
            settings = settings.model_dump()
    return settings

@api_router.put("/settings/company")
async def update_company_settings(company: CompanySettings):
    await db.settings.update_one(
        {"id": "settings"},
        {"$set": {"company": company.model_dump()}},
        upsert=True
    )
    return {"message": "Company settings updated"}

@api_router.put("/settings/policies")
async def update_policy_settings(policies: PolicySettings):
    await db.settings.update_one(
        {"id": "settings"},
        {"$set": {"policies": policies.model_dump()}},
        upsert=True
    )
    return {"message": "Policy settings updated"}

@api_router.put("/settings/tax")
async def update_tax_settings(tax_rate: float, tax_name: str = "GCT"):
    await db.settings.update_one(
        {"id": "settings"},
        {"$set": {"company.tax_rate": tax_rate, "company.tax_name": tax_name}},
        upsert=True
    )
    return {"message": "Tax settings updated"}

# ---- Vehicle Routes ----

@api_router.get("/vehicles", response_model=List[Vehicle])
async def get_vehicles():
    vehicles = await db.vehicles.find({}, {"_id": 0}).to_list(1000)
    return vehicles

@api_router.post("/vehicles", response_model=Vehicle)
async def create_vehicle(vehicle: VehicleCreate):
    vehicle_obj = Vehicle(**vehicle.model_dump())
    doc = vehicle_obj.model_dump()
    await db.vehicles.insert_one(doc)
    return vehicle_obj

@api_router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: str):
    result = await db.vehicles.delete_one({"id": vehicle_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle deleted successfully"}

@api_router.get("/vehicles/makes")
async def get_vehicle_makes():
    makes = await db.vehicles.distinct("make")
    return makes

@api_router.get("/vehicles/models/{make}")
async def get_vehicle_models(make: str):
    vehicles = await db.vehicles.find({"make": {"$regex": make, "$options": "i"}}, {"_id": 0, "model": 1}).to_list(1000)
    return [v["model"] for v in vehicles]

# ---- Dashboard/Reports Routes ----

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    # Use MongoDB aggregation for inventory stats
    inventory_pipeline = [
        {
            "$group": {
                "_id": None,
                "total_inventory_value": {
                    "$sum": {"$multiply": [{"$ifNull": ["$price", 0]}, {"$ifNull": ["$quantity", 0]}]}
                },
                "total_cost_value": {
                    "$sum": {
                        "$multiply": [
                            {"$ifNull": ["$cost_price", {"$ifNull": ["$price", 0]}]},
                            {"$ifNull": ["$quantity", 0]}
                        ]
                    }
                },
                "total_parts": {"$sum": 1}
            }
        }
    ]
    
    inventory_result = await db.parts.aggregate(inventory_pipeline).to_list(1)
    inventory_data = inventory_result[0] if inventory_result else {
        "total_inventory_value": 0,
        "total_cost_value": 0,
        "total_parts": 0
    }
    
    # Low stock count using aggregation
    low_stock_pipeline = [
        {
            "$match": {
                "$expr": {
                    "$lte": [
                        {"$ifNull": ["$quantity", 0]},
                        {"$ifNull": ["$min_stock_level", 5]}
                    ]
                }
            }
        },
        {"$count": "count"}
    ]
    low_stock_result = await db.parts.aggregate(low_stock_pipeline).to_list(1)
    low_stock_count = low_stock_result[0]["count"] if low_stock_result else 0
    
    # Total customers
    total_customers = await db.customers.count_documents({})
    
    # Total invoices
    total_invoices = await db.invoices.count_documents({})
    
    # Today's and monthly sales using aggregation
    today = datetime.now(timezone.utc).date().isoformat()
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")
    
    sales_pipeline = [
        {
            "$facet": {
                "today": [
                    {"$match": {"created_at": {"$regex": f"^{today}"}}},
                    {"$group": {"_id": None, "total": {"$sum": "$total"}}}
                ],
                "month": [
                    {"$match": {"created_at": {"$regex": f"^{current_month}"}}},
                    {"$group": {"_id": None, "total": {"$sum": "$total"}}}
                ]
            }
        }
    ]
    
    sales_result = await db.invoices.aggregate(sales_pipeline).to_list(1)
    sales_data = sales_result[0] if sales_result else {"today": [], "month": []}
    
    today_sales = sales_data["today"][0]["total"] if sales_data["today"] else 0
    monthly_sales = sales_data["month"][0]["total"] if sales_data["month"] else 0
    
    return {
        "total_inventory_value": inventory_data.get("total_inventory_value", 0),
        "total_cost_value": inventory_data.get("total_cost_value", 0),
        "total_parts": inventory_data.get("total_parts", 0),
        "low_stock_count": low_stock_count,
        "total_customers": total_customers,
        "total_invoices": total_invoices,
        "today_sales": today_sales,
        "monthly_sales": monthly_sales
    }

@api_router.get("/dashboard/low-stock")
async def get_low_stock_parts():
    # Use MongoDB $expr to compare fields and limit results
    pipeline = [
        {
            "$match": {
                "$expr": {
                    "$lte": [
                        {"$ifNull": ["$quantity", 0]},
                        {"$ifNull": ["$min_stock_level", 5]}
                    ]
                }
            }
        },
        {"$limit": 50},  # Limit to 50 items
        {"$project": {"_id": 0}}
    ]
    
    low_stock = await db.parts.aggregate(pipeline).to_list(50)
    
    for part in low_stock:
        if isinstance(part.get('created_at'), str):
            part['created_at'] = datetime.fromisoformat(part['created_at'])
        if isinstance(part.get('updated_at'), str):
            part['updated_at'] = datetime.fromisoformat(part['updated_at'])
    
    return low_stock

@api_router.get("/dashboard/recent-invoices")
async def get_recent_invoices(limit: int = 10):
    invoices = await db.invoices.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    
    for invoice in invoices:
        if isinstance(invoice.get('created_at'), str):
            invoice['created_at'] = datetime.fromisoformat(invoice['created_at'])
    
    return invoices

@api_router.get("/reports/sales")
async def get_sales_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    group_by: str = "day"
):
    query = {}
    
    if start_date:
        query["created_at"] = {"$gte": start_date}
    if end_date:
        if "created_at" in query:
            query["created_at"]["$lte"] = end_date
        else:
            query["created_at"] = {"$lte": end_date}
    
    invoices = await db.invoices.find(query, {"_id": 0}).to_list(10000)
    
    # Group by date
    sales_by_date = {}
    for inv in invoices:
        date_str = inv.get('created_at', '')
        if isinstance(date_str, datetime):
            date_str = date_str.isoformat()
        
        if group_by == "day":
            key = date_str[:10]
        elif group_by == "month":
            key = date_str[:7]
        elif group_by == "year":
            key = date_str[:4]
        else:
            key = date_str[:10]
        
        if key not in sales_by_date:
            sales_by_date[key] = {"date": key, "total": 0, "count": 0}
        
        sales_by_date[key]["total"] += inv.get('total', 0)
        sales_by_date[key]["count"] += 1
    
    return list(sales_by_date.values())

@api_router.get("/reports/inventory")
async def get_inventory_report():
    parts = await db.parts.find({}, {"_id": 0}).to_list(10000)
    
    # Group by category
    by_category = {}
    for part in parts:
        cat = part.get('category', 'Uncategorized')
        if cat not in by_category:
            by_category[cat] = {"category": cat, "count": 0, "value": 0, "items": []}
        
        by_category[cat]["count"] += 1
        by_category[cat]["value"] += part.get('price', 0) * part.get('quantity', 0)
        by_category[cat]["items"].append({
            "name": part.get('name'),
            "quantity": part.get('quantity', 0),
            "value": part.get('price', 0) * part.get('quantity', 0)
        })
    
    return list(by_category.values())

# ---- Image Upload Route ----

@api_router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    base64_image = base64.b64encode(contents).decode('utf-8')
    content_type = file.content_type or 'image/jpeg'
    data_url = f"data:{content_type};base64,{base64_image}"
    return {"image_url": data_url}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await init_settings()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
