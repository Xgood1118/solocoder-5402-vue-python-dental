from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from database import db
import uuid
from datetime import datetime, date

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

class ShiftSwap(BaseModel):
    date: str
    doctor_id: str
    original_shift: str
    swap_with_doctor: str
    reason: Optional[str] = ""

class HolidayCreate(BaseModel):
    name: str
    start_date: str
    end_date: str

class SwapLog(BaseModel):
    id: str
    date: str
    doctor_id: str
    original_shift: str
    swap_with_doctor: str
    reason: str
    created_at: str

@router.get("/weekly")
def get_weekly_schedule():
    schedule = db.get_all("schedule")
    result = []
    for sid, sched in schedule.items():
        result.append({"id": sid, **sched})
    result.sort(key=lambda x: DAY_NAMES.index(x["day"]) if x["day"] in DAY_NAMES else 99)
    return result

@router.get("/day/{day}")
def get_day_schedule(day: str):
    scheds = db.find("schedule", lambda s: s["day"] == day)
    if not scheds:
        return {}
    return {"id": scheds[0][0], **scheds[0][1]}

@router.post("/swap")
def create_swap(data: ShiftSwap):
    year_month = data.date[:7]
    
    doctor_swaps = db.find("swap_logs", 
                           lambda s: s["doctor_id"] == data.doctor_id 
                           and s["date"].startswith(year_month)
                           and s["status"] != "cancelled")
    
    swap_count = len(doctor_swaps)
    
    if swap_count >= 2 and not data.reason:
        raise HTTPException(status_code=400, detail="本月换班已超过2次，请填写换班原因")
    
    swap_id = str(uuid.uuid4())
    swap_log = {
        "date": data.date,
        "doctor_id": data.doctor_id,
        "original_shift": data.original_shift,
        "swap_with_doctor": data.swap_with_doctor,
        "reason": data.reason or "",
        "status": "pending",
        "performance_impacted": swap_count >= 2,
        "created_at": datetime.now().isoformat(),
    }
    db.add("swap_logs", swap_log, swap_id)
    
    return {"id": swap_id, **swap_log}

@router.get("/swaps")
def list_swaps(doctor_id: Optional[str] = None, month: Optional[str] = None):
    swaps = db.get_all("swap_logs")
    result = []
    for sid, swap in swaps.items():
        if doctor_id and swap["doctor_id"] != doctor_id:
            continue
        if month and not swap["date"].startswith(month):
            continue
        result.append({"id": sid, **swap})
    result.sort(key=lambda x: x["date"], reverse=True)
    return result

@router.get("/swaps/count/{doctor_id}/{month}")
def get_swap_count(doctor_id: str, month: str):
    swaps = db.find("swap_logs", 
                    lambda s: s["doctor_id"] == doctor_id 
                    and s["date"].startswith(month)
                    and s["status"] != "cancelled")
    return {
        "doctor_id": doctor_id,
        "month": month,
        "swap_count": len(swaps),
        "max_allowed": 2,
        "performance_impacted": len(swaps) > 2,
    }

@router.get("/holidays")
def list_holidays():
    holidays = db.get_all("holidays")
    result = [{"id": hid, **hol} for hid, hol in holidays.items()]
    result.sort(key=lambda x: x["start_date"])
    return result

@router.post("/holidays")
def create_holiday(data: HolidayCreate):
    holiday_id = str(uuid.uuid4())
    holiday = {
        "name": data.name,
        "start_date": data.start_date,
        "end_date": data.end_date,
    }
    db.add("holidays", holiday, holiday_id)
    return {"id": holiday_id, **holiday}

@router.delete("/holidays/{holiday_id}")
def delete_holiday(holiday_id: str):
    if not db.get_by_id("holidays", holiday_id):
        raise HTTPException(status_code=404, detail="节假日不存在")
    db.delete("holidays", holiday_id)
    return {"status": "deleted"}

@router.get("/doctors")
def list_doctors():
    doctors = db.get_all("doctors")
    return [{"id": did, **doc} for did, doc in doctors.items()]

@router.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: str):
    doc = db.get_by_id("doctors", doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="医生不存在")
    return {"id": doctor_id, **doc}
