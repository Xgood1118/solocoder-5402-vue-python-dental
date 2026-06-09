from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from database import db
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/billing", tags=["billing"])

class BillingItem(BaseModel):
    item_code: str
    item_name: str
    quantity: int
    unit_price: float
    self_ratio: float
    category: str

class BillCreate(BaseModel):
    patient_id: str
    patient_name: str
    chart_id: Optional[str] = None
    appointment_id: Optional[str] = None
    items: List[BillingItem]
    doctor_id: str
    payment_method: str = "现金"

class Bill(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    items: List[dict]
    total_amount: float
    insurance_amount: float
    self_amount: float
    status: str
    created_at: str

def calculate_bill(items: List[dict]) -> dict:
    total = 0.0
    insurance_total = 0.0
    self_total = 0.0
    
    for item in items:
        item_total = item["unit_price"] * item["quantity"]
        item_self = item_total * item["self_ratio"]
        item_insurance = item_total - item_self
        
        total += item_total
        insurance_total += item_insurance
        self_total += item_self
        
        item["item_total"] = item_total
        item["insurance_part"] = item_insurance
        item["self_part"] = item_self
    
    return {
        "total_amount": round(total, 2),
        "insurance_amount": round(insurance_total, 2),
        "self_amount": round(self_total, 2),
    }

@router.get("")
def list_bills(patient_id: Optional[str] = None, doctor_id: Optional[str] = None, status: Optional[str] = None):
    bills = db.get_all("bills")
    result = []
    for bid, bill in bills.items():
        if patient_id and bill["patient_id"] != patient_id:
            continue
        if doctor_id and bill.get("doctor_id") != doctor_id:
            continue
        if status and bill["status"] != status:
            continue
        result.append({"id": bid, **bill})
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return result

@router.get("/{bill_id}")
def get_bill(bill_id: str):
    bill = db.get_by_id("bills", bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    return {"id": bill_id, **bill}

@router.post("")
def create_bill(data: BillCreate):
    patient = db.get_by_id("patients", data.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    items_data = [item.model_dump() for item in data.items]
    amounts = calculate_bill(items_data)
    
    bill_id = str(uuid.uuid4())
    bill = {
        "patient_id": data.patient_id,
        "patient_name": data.patient_name,
        "chart_id": data.chart_id,
        "appointment_id": data.appointment_id,
        "doctor_id": data.doctor_id,
        "items": items_data,
        "total_amount": amounts["total_amount"],
        "insurance_amount": amounts["insurance_amount"],
        "self_amount": amounts["self_amount"],
        "payment_method": data.payment_method,
        "status": "paid",
        "created_at": datetime.now().isoformat(),
    }
    db.add("bills", bill, bill_id)
    
    return {"id": bill_id, **bill}

@router.get("/insurance-catalog")
def get_insurance_catalog(category: Optional[str] = None):
    catalog = db.get_all("insurance_catalog")
    result = []
    for code, item in catalog.items():
        if category and item["category"] != category:
            continue
        result.append({"code": code, **item})
    return result

@router.get("/insurance-catalog/{code}")
def get_insurance_item(code: str):
    item = db.get_by_id("insurance_catalog", code)
    if not item:
        raise HTTPException(status_code=404, detail="项目不存在")
    return {"code": code, **item}

@router.put("/insurance-catalog/{code}")
def update_insurance_item(code: str, item_data: dict):
    item = db.get_by_id("insurance_catalog", code)
    if not item:
        raise HTTPException(status_code=404, detail="项目不存在")
    updated = {**item, **item_data}
    db.update("insurance_catalog", code, updated)
    return {"code": code, **updated}

@router.get("/print/{bill_id}/insurance")
def print_insurance_receipt(bill_id: str):
    bill = db.get_by_id("bills", bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    insurance_items = [item for item in bill["items"] if item["insurance_part"] > 0]
    
    return {
        "bill_id": bill_id,
        "receipt_type": "医保联",
        "patient_name": bill["patient_name"],
        "date": bill["created_at"],
        "items": [
            {
                "name": item["item_name"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "self_ratio": item["self_ratio"],
                "insurance_part": item["insurance_part"],
                "self_part": item["self_part"],
            }
            for item in insurance_items
        ],
        "total": bill["total_amount"],
        "insurance_total": bill["insurance_amount"],
        "self_total": bill["self_amount"],
    }

@router.get("/print/{bill_id}/self")
def print_self_receipt(bill_id: str):
    bill = db.get_by_id("bills", bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    self_items = [item for item in bill["items"] if item["self_part"] > 0]
    
    return {
        "bill_id": bill_id,
        "receipt_type": "自费联",
        "patient_name": bill["patient_name"],
        "date": bill["created_at"],
        "items": [
            {
                "name": item["item_name"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "self_ratio": item["self_ratio"],
                "self_part": item["self_part"],
            }
            for item in self_items
        ],
        "self_total": bill["self_amount"],
    }
