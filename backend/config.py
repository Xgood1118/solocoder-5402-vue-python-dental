import os
from typing import Dict, Any

class Settings:
    def __init__(self):
        self.PORT = int(os.getenv("PORT", "8080"))
        self.SMS_GATEWAY_URL = os.getenv("SMS_GATEWAY_URL", "http://localhost:9090")
        self.SMS_GATEWAY_PORT = int(os.getenv("SMS_GATEWAY_PORT", "9090"))
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
        self.MAX_IMAGE_SIZE = 10 * 1024 * 1024
        self.ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "application/dicom"}
        self.ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".dcm"}

settings = Settings()
