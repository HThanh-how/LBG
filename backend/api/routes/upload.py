from fastapi import APIRouter, Depends, UploadFile, File, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from core.config import settings
from core.rate_limit import limiter
from core.database import get_db
from core.exceptions import BadRequestException
from services.excel_service import ExcelService
from api.dependencies import get_current_user
from models import User

router = APIRouter(prefix="/upload", tags=["File Upload"])


def get_excel_service(db=Depends(get_db)) -> ExcelService:
    return ExcelService(db)


@router.post("/tkb")
@limiter.limit("10/hour")
def upload_tkb(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    excel_service: ExcelService = Depends(get_excel_service),
):
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise BadRequestException("File must be Excel format (.xlsx or .xls)")
    
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise BadRequestException(
            f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    result = excel_service.process_tkb_file(file, current_user.id)
    return {"message": "TKB uploaded successfully", **result}


@router.post("/ctgd")
@limiter.limit("10/hour")
def upload_ctgd(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    excel_service: ExcelService = Depends(get_excel_service),
):
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise BadRequestException("File must be Excel format (.xlsx or .xls)")
    
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise BadRequestException(
            f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    result = excel_service.process_ctgd_file(file, current_user.id)
    return {"message": "CTGD uploaded successfully", **result}

