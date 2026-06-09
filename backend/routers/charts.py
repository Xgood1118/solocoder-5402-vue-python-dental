from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from database import db
import uuid
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/charts", tags=["charts"])

TOOTH_STATUSES = ["龋齿", "缺失", "修复", "种植", "牙周炎", "阻生"]

DISPLAY_PRIORITY = {
    "种植": 6,
    "修复": 5,
    "阻生": 4,
    "龋齿": 3,
    "牙周炎": 2,
    "缺失": 1,
}

def get_display_status(statuses: List[str]) -> str:
    if not statuses:
        return "健康"
    sorted_statuses = sorted(statuses, key=lambda s: DISPLAY_PRIORITY.get(s, 0), reverse=True)
    return sorted_statuses[0]

def check_chart_access(doctor_id: str, patient_id: str, chart_id: str = None) -> bool:
    if chart_id:
        chart = db.get_by_id("charts", chart_id)
        if chart and chart["doctor_id"] == doctor_id:
            return True
    
    charts = db.find("charts", lambda c: c["patient_id"] == patient_id and c["doctor_id"] == doctor_id)
    if charts:
        last_chart = max(charts, key=lambda x: x[1]["created_at"])
        last_date = datetime.fromisoformat(last_chart[1]["created_at"])
        if datetime.now() - last_date <= timedelta(days=30):
            return True
    
    grants = db.find("chart_access_grants", 
                     lambda g: g["patient_id"] == patient_id 
                     and g["granted_to_doctor"] == doctor_id
                     and g["status"] == "active")
    if grants:
        for gid, grant in grants:
            grant_time = datetime.fromisoformat(grant["granted_at"])
            if datetime.now() - grant_time <= timedelta(hours=24):
                return True
    return False

class ToothRecord(BaseModel):
    tooth_id: str
    statuses: List[str]
    notes: Optional[str] = ""

class ChartCreate(BaseModel):
    patient_id: str
    patient_name: str
    doctor_id: str
    doctor_name: str
    chief_complaint: str
    present_illness: str
    oral_examination: str
    diagnosis: str
    treatment_plan: str
    advice: str = ""
    teeth_records: List[Dict[str, Any]] = []
    transcriber: Optional[str] = None

class ChartUpdate(BaseModel):
    chief_complaint: Optional[str] = None
    present_illness: Optional[str] = None
    oral_examination: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    advice: Optional[str] = None
    teeth_records: Optional[List[Dict[str, Any]]] = None
    transcriber: Optional[str] = None

@router.get("")
def list_charts(patient_id: Optional[str] = None, doctor_id: Optional[str] = None):
    charts = db.get_all("charts")
    result = []
    for cid, chart in charts.items():
        if patient_id and chart["patient_id"] != patient_id:
            continue
        if doctor_id and chart["doctor_id"] != doctor_id:
            continue
        result.append({"id": cid, **chart})
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return result

@router.get("/{chart_id}")
def get_chart(chart_id: str, doctor_id: Optional[str] = None):
    chart = db.get_by_id("charts", chart_id)
    if not chart:
        raise HTTPException(status_code=404, detail="病历不存在")
    
    if doctor_id and chart["doctor_id"] != doctor_id:
        if not check_chart_access(doctor_id, chart["patient_id"], chart_id):
            raise HTTPException(status_code=403, detail="无权限查看此病历，请申请调阅授权")
    
    teeth_display = {}
    for tooth in chart.get("teeth_records", []):
        teeth_display[tooth["tooth_id"]] = {
            "statuses": tooth["statuses"],
            "display_status": get_display_status(tooth["statuses"]),
            "notes": tooth.get("notes", ""),
        }
    
    return {
        "id": chart_id, 
        **chart, 
        "teeth_display": teeth_display,
    }

@router.post("")
def create_chart(data: ChartCreate):
    patient = db.get_by_id("patients", data.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if not patient.get("allergy_history") or patient["allergy_history"].strip() == "":
        raise HTTPException(status_code=400, detail="过敏史未填写，无法创建病历")
    
    if not data.chief_complaint.strip():
        raise HTTPException(status_code=400, detail="主诉不能为空")
    
    chart_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    chart = {
        "patient_id": data.patient_id,
        "patient_name": data.patient_name,
        "doctor_id": data.doctor_id,
        "doctor_name": data.doctor_name,
        "chief_complaint": data.chief_complaint,
        "present_illness": data.present_illness,
        "oral_examination": data.oral_examination,
        "diagnosis": data.diagnosis,
        "treatment_plan": data.treatment_plan,
        "advice": data.advice,
        "teeth_records": data.teeth_records,
        "transcriber": data.transcriber,
        "created_at": now,
        "last_modified_by": data.doctor_id,
        "last_modified_at": now,
    }
    db.add("charts", chart, chart_id)
    
    return {"id": chart_id, **chart}

@router.put("/{chart_id}")
def update_chart(chart_id: str, data: ChartUpdate, modifier_id: str):
    chart = db.get_by_id("charts", chart_id)
    if not chart:
        raise HTTPException(status_code=404, detail="病历不存在")
    
    update_data = data.model_dump(exclude_unset=True)
    updated = {**chart, **update_data}
    updated["last_modified_by"] = modifier_id
    updated["last_modified_at"] = datetime.now().isoformat()
    
    db.update("charts", chart_id, updated)
    return {"id": chart_id, **updated}

@router.post("/access/request")
def request_chart_access(patient_id: str, requesting_doctor: str, reason: str):
    grant_id = str(uuid.uuid4())
    grant = {
        "patient_id": patient_id,
        "requested_by": requesting_doctor,
        "granted_to_doctor": requesting_doctor,
        "reason": reason,
        "status": "active",
        "granted_at": datetime.now().isoformat(),
    }
    db.add("chart_access_grants", grant, grant_id)
    return {"id": grant_id, **grant}

@router.get("/access/check")
def check_access(patient_id: str, doctor_id: str):
    has_access = check_chart_access(doctor_id, patient_id)
    return {"has_access": has_access}

@router.get("/teeth/status-map")
def get_teeth_status_map():
    return {
        "statuses": TOOTH_STATUSES,
        "display_priority": DISPLAY_PRIORITY,
    }
