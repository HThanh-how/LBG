from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import xlsxwriter
from io import BytesIO

from api.dependencies import get_current_user, get_db
from models import User

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("/tkb")
def download_tkb_template():
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet("TKB")
    
    header_format = workbook.add_format({
        "bold": True,
        "bg_color": "#4472C4",
        "font_color": "white",
        "align": "center",
        "valign": "vcenter",
        "border": 1,
    })
    
    cell_format = workbook.add_format({
        "align": "center",
        "valign": "vcenter",
        "border": 1,
    })
    
    worksheet.set_column("A:A", 12)
    worksheet.set_column("B:F", 20)
    
    # Header row: Tiết, Thứ 2, Thứ 3, Thứ 4, Thứ 5, Thứ 6
    headers = ["Tiết", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Data rows: Tiết 1, Tiết 2, Tiết 3, Tiết 4, Tiết 5
    periods = ["Tiết 1", "Tiết 2", "Tiết 3", "Tiết 4", "Tiết 5"]
    for row, period in enumerate(periods, start=1):
        worksheet.write(row, 0, period, cell_format)
        for col in range(1, 6):
            worksheet.write(row, col, "", cell_format)
    
    workbook.close()
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Mau_TKB.xlsx"},
    )


@router.get("/ctgd/subjects")
def get_subjects_from_tkb(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from models import Timetable
    subjects = db.query(Timetable.subject_name).filter(
        Timetable.user_id == current_user.id
    ).distinct().all()
    return [s[0] for s in subjects if s[0]]


@router.get("/ctgd/{subject}")
def download_ctgd_template(subject: str):
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet("CTGD")
    
    header_format = workbook.add_format({
        "bold": True,
        "bg_color": "#4472C4",
        "font_color": "white",
        "align": "center",
        "valign": "vcenter",
        "border": 1,
    })
    
    cell_format = workbook.add_format({
        "align": "left",
        "valign": "vcenter",
        "border": 1,
    })
    
    worksheet.set_column("A:A", 15)
    worksheet.set_column("B:B", 10)
    worksheet.set_column("C:C", 40)
    
    headers = ["Môn học", "Tiết thứ", "Tên bài"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    worksheet.write(1, 0, subject, cell_format)
    worksheet.write(1, 1, 1, cell_format)
    worksheet.write(1, 2, "", cell_format)
    
    workbook.close()
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=Mau_CTGD_{subject}.xlsx"},
    )

