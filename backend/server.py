from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Timeless Parts and Accessories API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

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
    tax_rate: float = 15.0
    tax_amount: float
    total: float
    payment_method: Optional[str] = "Cash"
    notes: Optional[str] = None
    status: str = "pending"

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: str = "Admin"

class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class CompanySettings(BaseModel):
    company_name: str = "Timeless Parts and Accessories"
    address: str = "Lot 36 Bustamante Highway, May Pen, Clarendon"
    phone: str = "876-403-8436"
    email: str = "timelessautoimportslimited@gmail.com"
    logo_url: str = "https://customer-assets.emergentagent.com/job_c8ea836d-f376-4793-85ac-d42fefdf5d7d/artifacts/mxjzjbvw_WhatsApp%20Image%202026-03-05%20at%204.13.42%20PM.jpeg"
    tax_rate: float = 15.0
    tax_name: str = "GCT"
    currency: str = "JMD"
    invoice_prefix: str = "TPA"

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

# ==================== HELPER FUNCTIONS ====================

async def get_next_invoice_number():
    settings = await db.settings.find_one({"id": "settings"}, {"_id": 0})
    if not settings:
        settings = Settings().model_dump()
        settings['company'] = dict(settings['company'])
        settings['policies'] = dict(settings['policies'])
        await db.settings.insert_one(settings)
    
    counter = settings.get('invoice_counter', 1)
    prefix = settings.get('company', {}).get('invoice_prefix', 'TPA')
    invoice_number = f"{prefix}-{counter:05d}"
    
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

# ---- Parts Routes ----

@api_router.get("/parts", response_model=List[Part])
async def get_parts(
    search: Optional[str] = None,
    category: Optional[str] = None,
    low_stock: Optional[bool] = None,
    vehicle_make: Optional[str] = None,
    vehicle_model: Optional[str] = None
):
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
    
    parts = await db.parts.find(query, {"_id": 0}).to_list(1000)
    
    if low_stock:
        parts = [p for p in parts if p.get('quantity', 0) <= p.get('min_stock_level', 5)]
    
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
async def get_customers(search: Optional[str] = None):
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    customers = await db.customers.find(query, {"_id": 0}).to_list(1000)
    
    for customer in customers:
        if isinstance(customer.get('created_at'), str):
            customer['created_at'] = datetime.fromisoformat(customer['created_at'])
    
    return customers

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if isinstance(customer.get('created_at'), str):
        customer['created_at'] = datetime.fromisoformat(customer['created_at'])
    
    return customer

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
    end_date: Optional[str] = None
):
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
    
    invoices = await db.invoices.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
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
async def create_invoice(invoice: InvoiceCreate):
    invoice_number = await get_next_invoice_number()
    
    invoice_obj = Invoice(**invoice.model_dump(), invoice_number=invoice_number)
    doc = invoice_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['items'] = [dict(item) for item in doc['items']]
    
    # Update stock for each item
    for item in invoice.items:
        await db.parts.update_one(
            {"id": item.part_id},
            {"$inc": {"quantity": -item.quantity}}
        )
    
    await db.invoices.insert_one(doc)
    return invoice_obj

@api_router.put("/invoices/{invoice_id}", response_model=Invoice)
async def update_invoice(invoice_id: str, invoice_update: InvoiceUpdate):
    existing = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    update_data = {k: v for k, v in invoice_update.model_dump().items() if v is not None}
    
    await db.invoices.update_one({"id": invoice_id}, {"$set": update_data})
    
    updated = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    
    return updated

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
    # Total inventory value
    parts = await db.parts.find({}, {"_id": 0, "price": 1, "quantity": 1, "cost_price": 1}).to_list(10000)
    total_inventory_value = sum((p.get('price') or 0) * (p.get('quantity') or 0) for p in parts)
    total_cost_value = sum((p.get('cost_price') or p.get('price') or 0) * (p.get('quantity') or 0) for p in parts)
    
    # Total parts count
    total_parts = await db.parts.count_documents({})
    
    # Low stock count
    all_parts = await db.parts.find({}, {"_id": 0}).to_list(10000)
    low_stock_count = len([p for p in all_parts if p.get('quantity', 0) <= p.get('min_stock_level', 5)])
    
    # Total customers
    total_customers = await db.customers.count_documents({})
    
    # Total invoices
    total_invoices = await db.invoices.count_documents({})
    
    # Today's sales
    today = datetime.now(timezone.utc).date().isoformat()
    today_invoices = await db.invoices.find(
        {"created_at": {"$regex": f"^{today}"}},
        {"_id": 0, "total": 1}
    ).to_list(1000)
    today_sales = sum(inv.get('total', 0) for inv in today_invoices)
    
    # Monthly sales (current month)
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")
    month_invoices = await db.invoices.find(
        {"created_at": {"$regex": f"^{current_month}"}},
        {"_id": 0, "total": 1}
    ).to_list(10000)
    monthly_sales = sum(inv.get('total', 0) for inv in month_invoices)
    
    return {
        "total_inventory_value": total_inventory_value,
        "total_cost_value": total_cost_value,
        "total_parts": total_parts,
        "low_stock_count": low_stock_count,
        "total_customers": total_customers,
        "total_invoices": total_invoices,
        "today_sales": today_sales,
        "monthly_sales": monthly_sales
    }

@api_router.get("/dashboard/low-stock")
async def get_low_stock_parts():
    parts = await db.parts.find({}, {"_id": 0}).to_list(10000)
    low_stock = [p for p in parts if p.get('quantity', 0) <= p.get('min_stock_level', 5)]
    
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
