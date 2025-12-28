from fastapi import APIRouter, Depends, Path, Request, Query
from fastapi.responses import FileResponse, HTMLResponse
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


@router.get("/lessons/{subject_name}")
@limiter.limit("30/minute")
def get_lessons_by_subject(
    request: Request,
    subject_name: str = Path(..., description="Tên môn học"),
    current_user: User = Depends(get_current_user),
    weekly_service: WeeklyReportService = Depends(get_weekly_report_service),
):
    """
    Lấy danh sách các tiết học của một môn học
    """
    teaching_programs = weekly_service.teaching_program_repo.get_by_user_id(current_user.id)
    lessons = [
        {
            "lesson_index": tp.lesson_index,
            "lesson_name": tp.lesson_name,
        }
        for tp in teaching_programs
        if tp.subject_name == subject_name
    ]
    # Sắp xếp theo lesson_index
    lessons.sort(key=lambda x: x["lesson_index"])
    return {"subject_name": subject_name, "lessons": lessons}


def get_export_service() -> ExportService:
    return ExportService()


@router.get("/preview")
@limiter.limit("10/hour")
def preview_all_weeks(
    request: Request,
    start_week: int = Query(..., ge=1, le=40),
    end_week: int = Query(..., ge=1, le=40),
    class_id: int = Query(None, description="ID của lớp"),
    current_user: User = Depends(get_current_user),
    weekly_service: WeeklyReportService = Depends(get_weekly_report_service),
    export_service: ExportService = Depends(get_export_service),
    db: Session = Depends(get_db),
):
    """
    Preview - Xem nhanh file Excel trong browser (không tải xuống)
    Trả về HTML để xem trong iframe hoặc tab mới
    """
    from fastapi.responses import HTMLResponse
    from datetime import datetime, timedelta
    from utils.date_utils import get_week_dates, format_vietnamese_date
    
    if start_week < 1 or end_week > 40 or start_week > end_week:
        raise NotFoundException("Invalid week range")
    
    timetables = weekly_service.timetable_repo.get_by_user_id(current_user.id)
    teaching_programs = weekly_service.teaching_program_repo.get_by_user_id(current_user.id)
    all_weekly_logs = []
    for week in range(start_week, end_week + 1):
        logs = weekly_service.weekly_log_repo.get_by_user_and_week(current_user.id, week)
        all_weekly_logs.extend(logs)
    
    holidays = weekly_service.get_holidays_for_user(current_user.id)
    
    # Lấy thông tin class nếu có
    reviewer_name = None
    teacher_name = current_user.full_name
    if class_id:
        from models import Class
        class_obj = db.query(Class).filter(Class.id == class_id).first()
        if class_obj:
            reviewer_name = class_obj.reviewer_name
            if class_obj.teacher_name:
                teacher_name = class_obj.teacher_name
    
    # Tạo HTML preview
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preview - Tuần {start_week} đến {end_week}</title>
        <style>
            * {{
                font-family: "Times New Roman", Times, serif;
            }}
            body {{
                font-family: "Times New Roman", Times, serif;
                margin: 0;
                padding: 20px;
                background: #fff;
            }}
            .container {{
                background: white;
                padding: 30px;
                margin-bottom: 40px;
                page-break-after: always;
            }}
            .container:last-child {{
                page-break-after: auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 25px;
            }}
            .header h1 {{
                font-size: 18px;
                font-weight: bold;
                margin: 0 0 10px 0;
                text-transform: uppercase;
            }}
            .header .week-info {{
                font-size: 14px;
                margin-top: 5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
                font-size: 13px;
            }}
            th, td {{
                border: 1px solid #000;
                padding: 8px 10px;
                text-align: left;
                vertical-align: top;
            }}
            th {{
                background-color: #f0f0f0;
                color: #000;
                font-weight: bold;
                text-align: center;
                font-size: 13px;
            }}
            td {{
                font-size: 12px;
                color: #000;
                background-color: #fff;
            }}
            tr:nth-child(even) td {{
                background-color: #fafafa;
            }}
            tr:hover td {{
                background-color: #f5f5f5;
            }}
            .day-cell {{
                text-align: center;
                font-weight: bold;
                vertical-align: middle;
            }}
            .period-cell {{
                text-align: center;
                width: 50px;
            }}
            .lesson-cell {{
                min-width: 300px;
            }}
            .integrated-cell {{
                width: 150px;
            }}
            .signature-section {{
                margin-top: 40px;
                display: flex;
                justify-content: space-between;
                font-size: 12px;
            }}
            .signature-left {{
                text-align: left;
            }}
            .signature-right {{
                text-align: right;
            }}
            .signature-line {{
                margin-top: 50px;
                border-top: 1px solid #000;
                padding-top: 5px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
    """
    
    # Tạo HTML cho mỗi tuần
    for week_number in range(start_week, end_week + 1):
        week_start, week_end = get_week_dates(datetime.now().year, week_number)
        week_logs = [log for log in all_weekly_logs if log.week_number == week_number]
        data = export_service._build_report_data(
            timetables, teaching_programs, week_logs, week_number, holidays
        )
        
        html_content += f"""
        <div class="container">
            <div class="header">
                <h1>LỊCH BÁO GIẢNG</h1>
                <div class="week-info">
                    <strong>TUẦN: {week_number}</strong><br/>
                    Từ ngày: {week_start.strftime('%d/%m/%Y')} đến ngày: {week_end.strftime('%d/%m/%Y')}
                </div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 150px;">THỨ/NGÀY</th>
                        <th style="width: 60px;">TIẾT</th>
                        <th>TÊN BÀI DẠY</th>
                        <th style="width: 120px;">Lồng ghép</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Tính toán rowspan cho mỗi ngày trước
        day_rowspans = {}
        current_day = None
        day_start_idx = None
        
        for idx, row in enumerate(data[1:], start=1):
            day_name = row[0] if row[0] else ""
            if day_name and day_name != current_day:
                if current_day is not None and day_start_idx is not None:
                    # Lưu rowspan cho ngày trước
                    periods_count = idx - day_start_idx
                    day_rowspans[day_start_idx] = periods_count
                current_day = day_name
                day_start_idx = idx
            elif not day_name and current_day:
                # Tiếp tục ngày hiện tại
                pass
        
        # Lưu rowspan cho ngày cuối
        if current_day is not None and day_start_idx is not None:
            periods_count = len(data) - day_start_idx
            day_rowspans[day_start_idx] = periods_count
        
        # Tạo HTML với rowspan đã tính
        current_day = None
        row_idx = 1
        
        for row in data[1:]:
            day_name = row[0] if row[0] else ""
            subject_code = row[2] if len(row) > 2 else ""
            lesson_name = row[3] if len(row) > 3 else ""
            lesson_display = f"{subject_code} - {lesson_name}" if subject_code else lesson_name
            notes = row[4] if len(row) > 4 else ""
            
            if day_name and day_name != current_day:
                current_day = day_name
                day_offset = int(day_name.split()[1]) - 2
                day_date = week_start + timedelta(days=day_offset)
                day_display = f"{day_name}<br/>{day_date.strftime('%d/%m/%Y')}"
                rowspan = day_rowspans.get(row_idx, 5)
                html_content += f"""
                    <tr>
                        <td rowspan="{rowspan}" class="day-cell">{day_display}</td>
                        <td class="period-cell">{row[1]}</td>
                        <td class="lesson-cell">{lesson_display}</td>
                        <td class="integrated-cell">{notes}</td>
                    </tr>
                """
            else:
                html_content += f"""
                    <tr>
                        <td class="period-cell">{row[1]}</td>
                        <td class="lesson-cell">{lesson_display}</td>
                        <td class="integrated-cell">{notes}</td>
                    </tr>
                """
            row_idx += 1
        
        html_content += """
                </tbody>
            </table>
            <div class="signature-section">
                <div class="signature-left">
                    <div><strong>Duyệt của Tổ trưởng chuyên môn</strong></div>
                    <div class="signature-line">""" + (reviewer_name or "") + """</div>
                </div>
                <div class="signature-right">
                    <div>Long Tiên, ngày """ + str(datetime.now().day) + """ tháng """ + str(datetime.now().month) + """ năm """ + str(datetime.now().year) + """</div>
                    <div style="margin-top: 10px;"><strong>GVPT</strong></div>
                    <div class="signature-line">""" + teacher_name + """</div>
                </div>
            </div>
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


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
    class_id: int = Query(None, description="ID của lớp"),
    current_user: User = Depends(get_current_user),
    weekly_service: WeeklyReportService = Depends(get_weekly_report_service),
    export_service: ExportService = Depends(get_export_service),
    db: Session = Depends(get_db),
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
        current_user, timetables, teaching_programs, weekly_logs, week_number, holidays, class_id, db
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
    class_id: int = Query(None, description="ID của lớp"),
    current_user: User = Depends(get_current_user),
    weekly_service: WeeklyReportService = Depends(get_weekly_report_service),
    export_service: ExportService = Depends(get_export_service),
    db: Session = Depends(get_db),
):
    """
    Export - Tải xuống file Excel
    """
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
        current_user, timetables, teaching_programs, all_weekly_logs, start_week, end_week, holidays, class_id, db
    )
    
    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"bao_giang_tuan_{start_week}_{end_week}.xlsx",
    )

