from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from database import db
from config import settings
import uuid
from datetime import datetime, timedelta
import httpx

router = APIRouter(prefix="/api/recall", tags=["recall"])

def months_between(date1: datetime, date2: datetime) -> int:
    return (date1.year - date2.year) * 12 + (date1.month - date2.month)

async def send_sms_async(phone: str, message: str, log_id: str):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.SMS_GATEWAY_URL}/sms/send",
                json={"phone": phone, "message": message}
            )
            if response.status_code == 200:
                log = db.get_by_id("recall_logs", log_id)
                if log:
                    log["sms_status"] = "sent"
                    log["sms_sent_at"] = datetime.now().isoformat()
                    db.update("recall_logs", log_id, log)
            else:
                raise Exception(f"HTTP {response.status_code}")
    except Exception as e:
        log = db.get_by_id("recall_logs", log_id)
        if log:
            log["sms_status"] = "send_fail"
            log["sms_error"] = str(e)
            db.update("recall_logs", log_id, log)

@router.get("/generate")
def generate_recall_list(background_tasks: BackgroundTasks, months: int = 6):
    now = datetime.now()
    cutoff_date = now - timedelta(days=months * 30)
    
    patients = db.get_all("patients")
    recall_list = []
    
    with db:
        for pid, patient in patients.items():
            last_visit = patient.get("last_visit_date")
            if not last_visit:
                continue
            
            last_visit_date = datetime.fromisoformat(last_visit)
            months_since = months_between(now, last_visit_date)
            
            if months_since >= months:
                reason = f"距上次就诊{months_since}个月未复诊"
                
                existing = db.find("recall_logs", 
                                   lambda r: r["patient_id"] == pid 
                                   and r.get("recall_month") == now.strftime("%Y-%m"))
                if existing:
                    continue
                
                log_id = str(uuid.uuid4())
                recall_log = {
                    "patient_id": pid,
                    "patient_name": patient["name"],
                    "patient_phone": patient["phone"],
                    "last_visit_date": last_visit,
                    "months_since_last_visit": months_since,
                    "reason": reason,
                    "recall_month": now.strftime("%Y-%m"),
                    "sms_status": "pending",
                    "created_at": now.isoformat(),
                }
                db.add("recall_logs", recall_log, log_id)
                
                background_tasks.add_task(send_sms_async, patient["phone"], 
                    f"【XX口腔诊所】尊敬的{patient['name']}患者，您好！距离您上次就诊已{months_since}个月，建议您定期进行口腔检查维护。预约电话：xxx-xxxxxxx",
                    log_id)
                
                recall_list.append({"id": log_id, **recall_log})
    
    return {"count": len(recall_list), "recall_list": recall_list}

@router.get("/logs")
def list_recall_logs(month: Optional[str] = None, sms_status: Optional[str] = None):
    logs = db.get_all("recall_logs")
    result = []
    for lid, log in logs.items():
        if month and log.get("recall_month") != month:
            continue
        if sms_status and log.get("sms_status") != sms_status:
            continue
        result.append({"id": lid, **log})
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return result

@router.get("/logs/{log_id}")
def get_recall_log(log_id: str):
    log = db.get_by_id("recall_logs", log_id)
    if not log:
        raise HTTPException(status_code=404, detail="召回记录不存在")
    return {"id": log_id, **log}

@router.post("/logs/{log_id}/resend")
def resend_sms(log_id: str, background_tasks: BackgroundTasks):
    log = db.get_by_id("recall_logs", log_id)
    if not log:
        raise HTTPException(status_code=404, detail="召回记录不存在")
    
    log["sms_status"] = "pending"
    log["sms_error"] = None
    db.update("recall_logs", log_id, log)
    
    background_tasks.add_task(send_sms_async, log["patient_phone"],
        f"【XX口腔诊所】尊敬的{log['patient_name']}患者，您好！距离您上次就诊已{log['months_since_last_visit']}个月，建议您定期进行口腔检查维护。预约电话：xxx-xxxxxxx",
        log_id)
    
    return {"status": "resending", "id": log_id}
