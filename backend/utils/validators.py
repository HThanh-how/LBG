from typing import Any
from fastapi import UploadFile
from core.config import settings
from core.exceptions import BadRequestException


def validate_file_upload(file: UploadFile) -> None:
    if not file.filename:
        raise BadRequestException("File name is required")
    
    if not file.filename.endswith((".xlsx", ".xls")):
        raise BadRequestException("File must be Excel format (.xlsx or .xls)")
    
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise BadRequestException(
            f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )


def validate_week_number(week_number: int) -> None:
    if week_number < 1 or week_number > 40:
        raise BadRequestException("Week number must be between 1 and 40")

