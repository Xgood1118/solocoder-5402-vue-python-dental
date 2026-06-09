from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database import db
import uuid
from datetime import datetime, timedelta, date

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

APPOINTMENT_TYPES = {
    "初诊": 30,
    "复诊": 20,
    "洁牙": 40,
    "拔牙": 45,
    "种植": 90,
    "根管治疗": 60,
}

ROOMS = ["1号诊室", "2号诊室"]

class AppointmentCreate(BaseModel):
    patient_id: str
    patient_name: str
    doctor_id: str
    appointment_type: str
    appointment_date: str
    start_time: str
    room: str
    notes: Optional[str] = ""

class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

def parse_datetime(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

def is_holiday(appointment_date: str) -> bool:
    d = date.fromisoformat(appointment_date)
    if d.weekday() == 6:
        return True
    holidays = db.get_all("holidays")
    for hid, hol in holidays.items():
        start = date.fromisoformat(hol["start_date"])
        end = date.fromisoformat(hol["end_date"])
        if start <= d <= end:
            return True
    return False

def check_conflict(doctor_id: str, appointment_date: str, start_time: str, duration_minutes: int, exclude_id: str = None) -> bool:
    start_dt = parse_datetime(appointment_date, start_time)
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    
    appointments = db.get_all("appointments")
    for aid, apt in appointments.items():
        if exclude_id and aid == exclude_id:
            continue
        if apt["status"] == "cancelled":
            continue
        if apt["doctor_id"] != doctor_id:
            continue
        if apt["appointment_date"] != appointment_date:
            continue
        
        apt_start = parse_datetime(apt["appointment_date"], apt["start_time"])
        apt_end = apt_start + timedelta(minutes=apt["duration_minutes"])
        
        if start_dt < apt_end and end_dt > apt_start:
            return True
    return False

@router.get("")
def list_appointments(date: Optional[str] = None, doctor_id: Optional[str] = None, status: Optional[str] = None):
    appointments = db.get_all("appointments")
    result = []
    for aid, apt in appointments.items():
        if date and apt["appointment_date"] != date:
            continue
        if doctor_id and apt["doctor_id"] != doctor_id:
            continue
        if status and apt.get("status") != status:
            continue
        result.append({"id": aid, **apt})
    result.sort(key=lambda x: (x["appointment_date"], x["start_time"]))
    return result

@router.get("/{appointment_id}")
def get_appointment(appointment_id: str):
    apt = db.get_by_id("appointments", appointment_id)
    if not apt:
        raise HTTPException(status_code=404, detail="预约不存在")
    return {"id": appointment_id, **apt}

@router.post("")
def create_appointment(data: AppointmentCreate):
    with db:
        if data.appointment_type not in APPOINTMENT_TYPES:
            raise HTTPException(status_code=400, detail="无效的预约类型")
        
        duration = APPOINTMENT_TYPES[data.appointment_type]
        
        if is_holiday(data.appointment_date):
            raise HTTPException(status_code=400, detail="该日期为节假日，不接受预约")
        
        if data.room not in ROOMS:
            raise HTTPException(status_code=400, detail="无效的诊室")
        
        if check_conflict(data.doctor_id, data.appointment_date, data.start_time, duration):
            raise HTTPException(status_code=409, detail="该医生此时间段已有预约")
        
        appointment_id = str(uuid.uuid4())
        appointment = {
            "patient_id": data.patient_id,
            "patient_name": data.patient_name,
            "doctor_id": data.doctor_id,
            "appointment_type": data.appointment_type,
            "appointment_date": data.appointment_date,
            "start_time": data.start_time,
            "duration_minutes": duration,
            "room": data.room,
            "status": "scheduled",
            "notes": data.notes,
            "created_at": datetime.now().isoformat(),
        }
        db.add("appointments", appointment, appointment_id)
    
    return {"id": appointment_id, **appointment}

@router.put("/{appointment_id}")
def update_appointment(appointment_id: str, data: AppointmentUpdate):
    apt = db.get_by_id("appointments", appointment_id)
    if not apt:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    update_data = data.model_dump(exclude_unset=True)
    updated = {**apt, **update_data}
    db.update("appointments", appointment_id, updated)
    return {"id": appointment_id, **updated}

@router.put("/{appointment_id}/status")
def update_appointment_status(appointment_id: str, status: str):
    apt = db.get_by_id("appointments", appointment_id)
    if not apt:
        raise HTTPException(status_code=404, detail="预约不存在")
    apt["status"] = status
    if status == "completed":
        patient = db.get_by_id("patients", apt["patient_id"])
        if patient:
            patient["last_visit_date"] = apt["appointment_date"]
            db.update("patients", apt["patient_id"], patient)
    db.update("appointments", appointment_id, apt)
    return {"id": appointment_id, **apt}

@router.delete("/{appointment_id}")
def cancel_appointment(appointment_id: str):
    apt = db.get_by_id("appointments", appointment_id)
    if not apt:
        raise HTTPException(status_code=404, detail="预约不存在")
    apt["status"] = "cancelled"
    db.update("appointments", appointment_id, apt)
    return {"status": "cancelled"}

@router.get("/types/list")
def get_appointment_types():
    return [{"type": k, "duration_minutes": v} for k, v in APPOINTMENT_TYPES.items()]

@router.get("/rooms/list")
def get_rooms():
    return ROOMS
