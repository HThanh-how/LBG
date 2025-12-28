from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import FileResponse
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from core.rate_limit import limiter
from core.database import get_db
from core.exceptions import NotFoundException
from services.weekly_report_service import WeeklyReportService
from services.export_service import ExportService
from api.dependencies import get_current_user
from schemas import WeeklyLogCreate
from models import User

router = APIRouter(prefix="/weekly-report", tags=["Weekly Report"])


def get_weekly_report_service(db=Depends(get_db)) -> WeeklyReportService:
    return WeeklyReportService(db)


def get_export_service() -> ExportService:
    return ExportService()


@router.get("/{week_number}")
@limiter.limit("60/minute")
def get_weekly_report(
    request: Request,
    week_number: int = Path(..., ge=1, le=40),
    current_user: User = Depends(get_current_user),
    service: WeeklyReportService = Depends(get_weekly_report_service),
):
    if week_number < 1 or week_number > 40:
        raise NotFoundException("Week number must be between 1 and 40")
    
    return service.generate_weekly_report(current_user.id, week_number)


@router.post("/{week_number}/save")
@limiter.limit("30/hour")
def save_weekly_report(
    request: Request,
    week_number: int = Path(..., ge=1, le=40),
    logs: List[WeeklyLogCreate] = ...,
    current_user: User = Depends(get_current_user),
    service: WeeklyReportService = Depends(get_weekly_report_service),
):
    return service.save_weekly_report(current_user.id, week_number, [log.dict() for log in logs])


@router.get("/{week_number}/export/pdf")
@limiter.limit("20/hour")
def export_pdf(
    request: Request,
    week_number: int = Path(..., ge=1, le=40),
    current_user: User = Depends(get_current_user),
    weekly_service: WeeklyReportService = Depends(get_weekly_report_service),
    export_service: ExportService = Depends(get_export_service),
):
    timetables, teaching_programs, weekly_logs = weekly_service.get_data_for_export(
        current_user, week_number
    )
    
    pdf_path = export_service.export_pdf(
        current_user, timetables, teaching_programs, weekly_logs, week_number
    )
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"bao_giang_tuan_{week_number}.pdf",
    )


@router.get("/{week_number}/export/excel")
@limiter.limit("20/hour")
def export_excel(
    request: Request,
    week_number: int = Path(..., ge=1, le=40),
    current_user: User = Depends(get_current_user),
    weekly_service: WeeklyReportService = Depends(get_weekly_report_service),
    export_service: ExportService = Depends(get_export_service),
):
    timetables, teaching_programs, weekly_logs = weekly_service.get_data_for_export(
        current_user, week_number
    )
    
    excel_path = export_service.export_excel(
        current_user, timetables, teaching_programs, weekly_logs, week_number
    )
    
    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"bao_giang_tuan_{week_number}.xlsx",
    )

