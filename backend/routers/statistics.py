from fastapi import APIRouter
from typing import Optional
from database import db
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/statistics", tags=["statistics"])

def months_between(date1: datetime, date2: datetime) -> int:
    return (date1.year - date2.year) * 12 + (date1.month - date2.month)

@router.get("/doctor/{doctor_id}/monthly")
def get_doctor_monthly_stats(doctor_id: str, year_month: Optional[str] = None):
    if not year_month:
        now = datetime.now()
        year_month = now.strftime("%Y-%m")
    
    appointments = db.find("appointments", 
                          lambda a: a["doctor_id"] == doctor_id 
                          and a["appointment_date"].startswith(year_month)
                          and a["status"] == "completed")
    
    total_visits = len(appointments)
    
    bills = db.find("bills", lambda b: b.get("doctor_id") == doctor_id 
                    and b["created_at"].startswith(year_month)
                    and b["status"] == "paid")
    
    total_revenue = sum(b[1]["total_amount"] for b in bills)
    avg_price = total_revenue / total_visits if total_visits > 0 else 0
    
    charts = db.find("charts", lambda c: c["doctor_id"] == doctor_id)
    all_patients = set(c[1]["patient_id"] for c in charts)
    
    six_months_ago = (datetime.strptime(year_month + "-01", "%Y-%m-%d") - timedelta(days=180)).isoformat()
    
    return_patients = set()
    for cid, chart in charts:
        if chart["created_at"] >= six_months_ago and chart["created_at"] < year_month:
            pass
    
    follow_up_patients = set()
    for cid, chart in charts:
        if chart["created_at"].startswith(year_month):
            patient_id = chart["patient_id"]
            earlier_charts = [c for c in charts if c[1]["patient_id"] == patient_id 
                             and c[1]["created_at"] < chart["created_at"]]
            if earlier_charts:
                follow_up_patients.add(patient_id)
    
    total_patients_seen = len(set(a[1]["patient_id"] for a in appointments))
    
    follow_up_rate = len(follow_up_patients) / total_patients_seen if total_patients_seen > 0 else 0
    
    return {
        "doctor_id": doctor_id,
        "year_month": year_month,
        "total_visits": total_visits,
        "total_patients": total_patients_seen,
        "total_revenue": round(total_revenue, 2),
        "avg_price": round(avg_price, 2),
        "follow_up_rate": round(follow_up_rate, 4),
        "follow_up_count": len(follow_up_patients),
    }

@router.get("/clinic/monthly")
def get_clinic_monthly_stats(year_month: Optional[str] = None):
    if not year_month:
        now = datetime.now()
        year_month = now.strftime("%Y-%m")
    
    doctors = db.get_all("doctors")
    doctor_stats = []
    
    for did in doctors.keys():
        stat = get_doctor_monthly_stats(did, year_month)
        doctor_stats.append(stat)
    
    total_visits = sum(s["total_visits"] for s in doctor_stats)
    total_revenue = sum(s["total_revenue"] for s in doctor_stats)
    
    return {
        "year_month": year_month,
        "total_visits": total_visits,
        "total_revenue": round(total_revenue, 2),
        "doctor_stats": doctor_stats,
    }

@router.get("/overview")
def get_overview_stats():
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    this_month = now.strftime("%Y-%m")
    
    today_appointments = db.find("appointments", 
                                lambda a: a["appointment_date"] == today)
    
    this_month_bills = db.find("bills", 
                              lambda b: b["created_at"].startswith(this_month)
                              and b["status"] == "paid")
    
    total_patients = len(db.get_all("patients"))
    total_bills = len(db.get_all("bills"))
    
    return {
        "today_appointments": len(today_appointments),
        "this_month_revenue": round(sum(b[1]["total_amount"] for b in this_month_bills), 2),
        "total_patients": total_patients,
        "total_bills": total_bills,
        "total_charts": len(db.get_all("charts")),
    }
