from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from database import db
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/patients", tags=["patients"])

class FamilyMember(BaseModel):
    id: str
    name: str
    id_card: str
    relation: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None

class PatientCreate(BaseModel):
    name: str
    phone: str
    id_card: str
    allergy_history: str = ""
    past_history: str = ""
    birth_date: Optional[str] = None
    gender: Optional[str] = None

class Patient(BaseModel):
    id: str
    name: str
    phone: str
    id_card: str
    allergy_history: str
    past_history: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    family_members: List[dict] = []
    created_at: str
    last_visit_date: Optional[str] = None

class FamilyMemberAdd(BaseModel):
    name: str
    id_card: str
    relation: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None

@router.get("")
def list_patients(phone: Optional[str] = None, name: Optional[str] = None):
    patients = db.get_all("patients")
    result = []
    for pid, patient in patients.items():
        p = {"id": pid, **patient}
        if phone and phone not in patient.get("phone", ""):
            continue
        if name and name not in patient.get("name", ""):
            continue
        result.append(p)
    return result

@router.get("/{patient_id}")
def get_patient(patient_id: str):
    patient = db.get_by_id("patients", patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    return {"id": patient_id, **patient}

@router.post("")
def create_patient(data: PatientCreate):
    with db:
        existing = db.find("patients", lambda p: p["phone"] == data.phone)
        if existing:
            raise HTTPException(status_code=400, detail="该手机号已建档，请使用手机号检索")
        
        existing_id = db.find("patients", lambda p: p["id_card"] == data.id_card)
        if existing_id:
            raise HTTPException(status_code=400, detail="该身份证号已存在")
        
        patient_id = str(uuid.uuid4())
        patient = {
            "name": data.name,
            "phone": data.phone,
            "id_card": data.id_card,
            "allergy_history": data.allergy_history,
            "past_history": data.past_history,
            "birth_date": data.birth_date,
            "gender": data.gender,
            "family_members": [],
            "created_at": datetime.now().isoformat(),
            "last_visit_date": None,
        }
        db.add("patients", patient, patient_id)
    return {"id": patient_id, **patient}

@router.put("/{patient_id}")
def update_patient(patient_id: str, data: PatientCreate):
    patient = db.get_by_id("patients", patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    updated = {**patient, **data.model_dump(exclude_unset=True)}
    db.update("patients", patient_id, updated)
    return {"id": patient_id, **updated}

@router.post("/{patient_id}/family")
def add_family_member(patient_id: str, data: FamilyMemberAdd):
    patient = db.get_by_id("patients", patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    with db:
        all_patients = db.get_all("patients")
        for pid, p in all_patients.items():
            if p["id_card"] == data.id_card:
                raise HTTPException(status_code=400, detail="该身份证号已存在，不能重复挂接")
            for fm in p.get("family_members", []):
                if fm["id_card"] == data.id_card:
                    raise HTTPException(status_code=400, detail="该身份证号已在其他家庭档案中")
        
        member_id = str(uuid.uuid4())
        member = {
            "id": member_id,
            "name": data.name,
            "id_card": data.id_card,
            "relation": data.relation,
            "birth_date": data.birth_date,
            "gender": data.gender,
        }
        patient["family_members"].append(member)
        db.update("patients", patient_id, patient)
    
    return {"id": patient_id, "family_member": member}

@router.delete("/{patient_id}/family/{member_id}")
def remove_family_member(patient_id: str, member_id: str):
    patient = db.get_by_id("patients", patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    patient["family_members"] = [fm for fm in patient["family_members"] if fm["id"] != member_id]
    db.update("patients", patient_id, patient)
    return {"status": "ok"}

@router.get("/search/by-phone/{phone}")
def search_by_phone(phone: str):
    results = db.find("patients", lambda p: p["phone"] == phone)
    if not results:
        return {"found": False, "patients": []}
    patients = []
    for pid, p in results:
        patients.append({"id": pid, **p})
    return {"found": True, "patients": patients}
