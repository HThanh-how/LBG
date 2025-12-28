from fastapi import APIRouter, Depends, Path, Request, Query
from fastapi.responses import FileResponse
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from core.rate_limit import limiter
from core.database import get_db
from core.exceptions import NotFoundException
from services.weekly_report_service import WeeklyReportService
from services.export_service import ExportService
from api.dependencies import get_current_user
from schemas import WeeklyLogCreate
from models import User

router = APIRouter(prefix="/weekly-report", tags=["Weekly Report"])


def get_weekly_report_service(db: Session = Depends(get_db)) -> WeeklyReportService:
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
    
    holidays = weekly_service.get_holidays_for_user(current_user.id)
    
    # Tự động tạo ngày nghỉ lễ mặc định nếu chưa có
    if not holidays:
        from utils.holidays import create_default_holidays
        from datetime import datetime
        create_default_holidays(weekly_service.db, current_user.id, datetime.now().year)
        holidays = weekly_service.get_holidays_for_user(current_user.id)
    
    pdf_path = export_service.export_pdf(
        current_user, timetables, teaching_programs, weekly_logs, week_number, holidays
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
    
    holidays = weekly_service.get_holidays_for_user(current_user.id)
    
    # Tự động tạo ngày nghỉ lễ mặc định nếu chưa có
    if not holidays:
        from utils.holidays import create_default_holidays
        from datetime import datetime
        create_default_holidays(weekly_service.db, current_user.id, datetime.now().year)
        holidays = weekly_service.get_holidays_for_user(current_user.id)
    
    excel_path = export_service.export_excel(
        current_user, timetables, teaching_programs, weekly_logs, week_number, holidays
    )
    
    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"bao_giang_tuan_{week_number}.xlsx",
    )


@router.get("/export/all")
@limiter.limit("10/hour")
def export_all_weeks(
    request: Request,
    start_week: int = Query(..., ge=1, le=40),
    end_week: int = Query(..., ge=1, le=40),
    current_user: User = Depends(get_current_user),
    weekly_service: WeeklyReportService = Depends(get_weekly_report_service),
    export_service: ExportService = Depends(get_export_service),
):
    if start_week < 1 or end_week > 40 or start_week > end_week:
        raise NotFoundException("Invalid week range")
    
    timetables = weekly_service.timetable_repo.get_by_user_id(current_user.id)
    teaching_programs = weekly_service.teaching_program_repo.get_by_user_id(current_user.id)
    all_weekly_logs = []
    for week in range(start_week, end_week + 1):
        logs = weekly_service.weekly_log_repo.get_by_user_and_week(current_user.id, week)
        all_weekly_logs.extend(logs)
    
    holidays = weekly_service.get_holidays_for_user(current_user.id)
    
    # Tự động tạo ngày nghỉ lễ mặc định nếu chưa có
    if not holidays:
        from utils.holidays import create_default_holidays
        from datetime import datetime
        create_default_holidays(weekly_service.db, current_user.id, datetime.now().year)
        holidays = weekly_service.get_holidays_for_user(current_user.id)
    
    excel_path = export_service.export_all_weeks_excel(
        current_user, timetables, teaching_programs, all_weekly_logs, start_week, end_week, holidays
    )
    
    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"bao_giang_tuan_{start_week}_{end_week}.xlsx",
    )

