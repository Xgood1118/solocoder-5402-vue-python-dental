from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from database import db
from config import settings
import uuid
import os
from datetime import datetime
import shutil

router = APIRouter(prefix="/api/images", tags=["images"])

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

class Annotation(BaseModel):
    id: str
    type: str
    x: float
    y: float
    text: Optional[str] = ""
    color: str = "#ff0000"

class ImageUpdate(BaseModel):
    description: Optional[str] = None
    annotations: Optional[List[dict]] = None

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".dcm"}

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

@router.get("")
def list_images(patient_id: Optional[str] = None, chart_id: Optional[str] = None, tooth_id: Optional[str] = None):
    images = db.get_all("images")
    result = []
    for iid, img in images.items():
        if patient_id and img["patient_id"] != patient_id:
            continue
        if chart_id and img["chart_id"] != chart_id:
            continue
        if tooth_id and img.get("tooth_id") != tooth_id:
            continue
        result.append({"id": iid, **img})
    result.sort(key=lambda x: x["uploaded_at"], reverse=True)
    return result

@router.get("/{image_id}")
def get_image(image_id: str):
    img = db.get_by_id("images", image_id)
    if not img:
        raise HTTPException(status_code=404, detail="影像不存在")
    return {"id": image_id, **img}

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    chart_id: str = Form(...),
    tooth_id: Optional[str] = Form(None),
    description: Optional[str] = Form(""),
    image_type: str = Form("xray"),
):
    ext = get_file_extension(file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}")
    
    content = await file.read()
    if len(content) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过10MB限制")
    
    image_id = str(uuid.uuid4())
    filename = f"{image_id}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    image = {
        "patient_id": patient_id,
        "chart_id": chart_id,
        "tooth_id": tooth_id,
        "filename": filename,
        "original_filename": file.filename,
        "file_path": filepath,
        "file_size": len(content),
        "file_type": ext,
        "description": description,
        "image_type": image_type,
        "annotations": [],
        "uploaded_at": datetime.now().isoformat(),
    }
    db.add("images", image, image_id)
    
    return {"id": image_id, **image}

@router.get("/{image_id}/file")
def get_image_file(image_id: str):
    img = db.get_by_id("images", image_id)
    if not img:
        raise HTTPException(status_code=404, detail="影像不存在")
    
    filepath = img["file_path"]
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    media_type = "image/png"
    if img["file_type"] == ".jpg" or img["file_type"] == ".jpeg":
        media_type = "image/jpeg"
    elif img["file_type"] == ".dcm":
        media_type = "application/dicom"
    
    return FileResponse(filepath, media_type=media_type, filename=img["original_filename"])

@router.put("/{image_id}")
def update_image(image_id: str, data: ImageUpdate):
    img = db.get_by_id("images", image_id)
    if not img:
        raise HTTPException(status_code=404, detail="影像不存在")
    
    update_data = data.model_dump(exclude_unset=True)
    updated = {**img, **update_data}
    db.update("images", image_id, updated)
    return {"id": image_id, **updated}

@router.post("/{image_id}/annotations")
def save_annotations(image_id: str, annotations: List[dict]):
    img = db.get_by_id("images", image_id)
    if not img:
        raise HTTPException(status_code=404, detail="影像不存在")
    
    img["annotations"] = annotations
    db.update("images", image_id, img)
    return {"id": image_id, "annotations": annotations}

@router.delete("/{image_id}")
def delete_image(image_id: str):
    img = db.get_by_id("images", image_id)
    if not img:
        raise HTTPException(status_code=404, detail="影像不存在")
    
    if os.path.exists(img["file_path"]):
        os.remove(img["file_path"])
    
    db.delete("images", image_id)
    return {"status": "deleted"}
