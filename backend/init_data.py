from datetime import date, datetime, time
from database import db
import uuid

def init_doctors():
    doctors = [
        {"id": "doc-001", "name": "张医生", "phone": "13800138001", "title": "主治医师", "specialty": "口腔修复"},
        {"id": "doc-002", "name": "李医生", "phone": "13800138002", "title": "副主任医师", "specialty": "口腔种植"},
    ]
    for doc in doctors:
        db.add("doctors", doc, doc["id"])

def init_insurance_catalog():
    items = [
        {"code": "INS001", "name": "初诊检查", "price": 50.0, "self_ratio": 0.3, "category": "检查"},
        {"code": "INS002", "name": "复诊检查", "price": 30.0, "self_ratio": 0.3, "category": "检查"},
        {"code": "INS003", "name": "洁牙", "price": 200.0, "self_ratio": 0.5, "category": "洁牙"},
        {"code": "INS004", "name": "简单拔牙", "price": 150.0, "self_ratio": 0.3, "category": "拔牙"},
        {"code": "INS005", "name": "复杂拔牙", "price": 400.0, "self_ratio": 0.3, "category": "拔牙"},
        {"code": "INS006", "name": "阻生齿拔除", "price": 800.0, "self_ratio": 0.3, "category": "拔牙"},
        {"code": "INS007", "name": "根管治疗前牙", "price": 500.0, "self_ratio": 0.4, "category": "根管治疗"},
        {"code": "INS008", "name": "根管治疗后牙", "price": 800.0, "self_ratio": 0.4, "category": "根管治疗"},
        {"code": "INS009", "name": "树脂补牙浅龋", "price": 200.0, "self_ratio": 0.3, "category": "修复"},
        {"code": "INS010", "name": "树脂补牙中龋", "price": 300.0, "self_ratio": 0.3, "category": "修复"},
        {"code": "INS011", "name": "树脂补牙深龋", "price": 400.0, "self_ratio": 0.3, "category": "修复"},
        {"code": "INS012", "name": "烤瓷牙冠", "price": 1500.0, "self_ratio": 0.5, "category": "修复"},
        {"code": "INS013", "name": "全瓷牙冠", "price": 3000.0, "self_ratio": 0.7, "category": "修复"},
        {"code": "INS014", "name": "种植牙(韩系)", "price": 6000.0, "self_ratio": 1.0, "category": "种植"},
        {"code": "INS015", "name": "种植牙(欧美系)", "price": 12000.0, "self_ratio": 1.0, "category": "种植"},
        {"code": "INS016", "name": "X光片小牙片", "price": 30.0, "self_ratio": 0.3, "category": "影像"},
        {"code": "INS017", "name": "X光片全景片", "price": 150.0, "self_ratio": 0.3, "category": "影像"},
        {"code": "INS018", "name": "CBCT", "price": 300.0, "self_ratio": 0.5, "category": "影像"},
        {"code": "INS019", "name": "牙周基础治疗", "price": 500.0, "self_ratio": 0.4, "category": "牙周"},
        {"code": "INS020", "name": "牙周深刮", "price": 800.0, "self_ratio": 0.4, "category": "牙周"},
    ]
    for i in range(21, 61):
        items.append({
            "code": f"INS{i:03d}",
            "name": f"项目{i:03d}",
            "price": float(100 + (i % 20) * 50),
            "self_ratio": 0.3 if i % 3 == 0 else (0.5 if i % 3 == 1 else 0.7),
            "category": ["检查", "修复", "洁牙", "拔牙", "根管治疗", "影像"][i % 6],
        })
    for item in items:
        db.add("insurance_catalog", item, item["code"])

def init_holidays():
    holidays = [
        {"id": "hol-2026-spring", "name": "春节", "start_date": "2026-02-16", "end_date": "2026-02-22"},
        {"id": "hol-2026-qingming", "name": "清明节", "start_date": "2026-04-04", "end_date": "2026-04-06"},
        {"id": "hol-2026-labour", "name": "劳动节", "start_date": "2026-05-01", "end_date": "2026-05-05"},
        {"id": "hol-2026-dragon", "name": "端午节", "start_date": "2026-06-19", "end_date": "2026-06-21"},
        {"id": "hol-2026-midautumn", "name": "中秋节", "start_date": "2026-09-25", "end_date": "2026-09-27"},
        {"id": "hol-2026-national", "name": "国庆节", "start_date": "2026-10-01", "end_date": "2026-10-07"},
    ]
    for hol in holidays:
        db.add("holidays", hol, hol["id"])

def init_supplies():
    supplies = [
        {"code": "SP001", "name": "树脂材料A2", "unit": "支", "cost_price": 80.0, "supplier": "牙科材料商A"},
        {"code": "SP002", "name": "树脂材料A3", "unit": "支", "cost_price": 85.0, "supplier": "牙科材料商A"},
        {"code": "SP003", "name": "车针套装", "unit": "套", "cost_price": 120.0, "supplier": "牙科材料商B"},
        {"code": "SP004", "name": "麻药阿替卡因", "unit": "支", "cost_price": 15.0, "supplier": "药品供应商"},
        {"code": "SP005", "name": "种植体韩系", "unit": "颗", "cost_price": 2000.0, "supplier": "种植体厂商"},
    ]
    for sp in supplies:
        db.add("supplies", sp, sp["code"])

def init_schedule():
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    for day in days:
        schedule_id = f"sched-{day}"
        schedule = {
            "day": day,
            "doctor_shifts": {
                "doc-001": {"room": "1号诊室", "start_time": "08:30", "end_time": "12:00", "shift_type": "morning"},
                "doc-002": {"room": "2号诊室", "start_time": "08:30", "end_time": "12:00", "shift_type": "morning"},
            },
            "afternoon_shifts": {
                "doc-001": {"room": "1号诊室", "start_time": "14:00", "end_time": "17:30", "shift_type": "afternoon"},
                "doc-002": {"room": "2号诊室", "start_time": "14:00", "end_time": "17:30", "shift_type": "afternoon"},
            },
        }
        db.add("schedule", schedule, schedule_id)

def init_all():
    init_doctors()
    init_insurance_catalog()
    init_holidays()
    init_supplies()
    init_schedule()
