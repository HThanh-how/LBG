from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import xlsxwriter
from datetime import datetime
import os
from collections import defaultdict
from typing import List

from models import User, Timetable, TeachingProgram, WeeklyLog
from core.logging_config import get_logger
from utils.date_utils import get_week_dates, format_vietnamese_date

logger = get_logger(__name__)


class ExportService:
    def __init__(self):
        self.output_dir = "exports"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_pdf(
        self,
        user: User,
        timetables: List[Timetable],
        teaching_programs: List[TeachingProgram],
        weekly_logs: List[WeeklyLog],
        week_number: int,
    ) -> str:
        filename = f"{self.output_dir}/bao_giang_tuan_{week_number}_user_{user.id}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        
        styles = getSampleStyleSheet()
        
        week_start, week_end = get_week_dates(datetime.now().year, week_number)
        
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=14,
            textColor=colors.HexColor("#000000"),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        )
        
        header_style = ParagraphStyle(
            "Header",
            parent=styles["Normal"],
            fontSize=11,
            alignment=TA_LEFT,
        )
        
        cell_style = ParagraphStyle(
            "Cell",
            parent=styles["Normal"],
            fontSize=9,
            alignment=TA_LEFT,
        )
        
        title_row = [
            Paragraph(f"TUẦN : {week_number}", title_style),
            Paragraph(
                f"Từ ngày : {format_vietnamese_date(week_start)} đến ngày : {format_vietnamese_date(week_end)}",
                title_style
            ),
        ]
        
        title_table = Table([title_row], colWidths=[6*cm, 12*cm])
        title_table.setStyle(
            TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        story.append(title_table)
        story.append(Spacer(1, 0.3 * cm))
        
        data = self._build_report_data(
            timetables, teaching_programs, weekly_logs, week_number
        )
        
        table_data = []
        table_data.append(["THỨ / NGÀY", "TIẾT", "TÊN BÀI DẠY", "Lồng ghép"])
        
        current_day = None
        for row in data[1:]:
            day_name = row[0]
            if day_name and day_name != current_day:
                current_day = day_name
                day_date = week_start + timedelta(days=int(day_name.split()[1]) - 2)
                day_display = f"{day_name}<br/>{day_date.strftime('%d/%m')}"
            else:
                day_display = ""
            
            table_data.append([
                Paragraph(day_display, cell_style) if day_display else "",
                Paragraph(str(row[1]), cell_style),
                Paragraph(row[3] if len(row) > 3 else "", cell_style),
                Paragraph(row[4] if len(row) > 4 else "", cell_style),
            ])
        
        table = Table(table_data, colWidths=[3*cm, 1.5*cm, 8*cm, 4*cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("ALIGN", (2, 0), (2, -1), "LEFT"),
                    ("ALIGN", (3, 0), (3, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
                ]
            )
        )
        
        story.append(table)
        story.append(Spacer(1, 1 * cm))
        
        signature_style_left = ParagraphStyle(
            "SignatureLeft", parent=styles["Normal"], fontSize=10, alignment=TA_LEFT
        )
        signature_style_right = ParagraphStyle(
            "SignatureRight", parent=styles["Normal"], fontSize=10, alignment=TA_RIGHT
        )
        
        signature_data = [
            [
                Paragraph("Duyệt của Tổ trưởng CM", signature_style_left),
                Paragraph(f"Long Tiên ngày ... tháng ... năm {datetime.now().year}", signature_style_right),
            ],
            [
                Paragraph("", signature_style_left),
                Paragraph("GVPT", signature_style_right),
            ],
            [
                Paragraph("", signature_style_left),
                Paragraph(user.full_name, signature_style_right),
            ],
        ]
        
        signature_table = Table(signature_data, colWidths=[8*cm, 8*cm])
        signature_table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ])
        )
        story.append(signature_table)
        
        doc.build(story)
        logger.info("PDF exported", user_id=user.id, week_number=week_number)
        return filename
    
    def export_excel(
        self,
        user: User,
        timetables: List[Timetable],
        teaching_programs: List[TeachingProgram],
        weekly_logs: List[WeeklyLog],
        week_number: int,
    ) -> str:
        filename = f"{self.output_dir}/bao_giang_tuan_{week_number}_user_{user.id}.xlsx"
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        
        week_start, week_end = get_week_dates(datetime.now().year, week_number)
        
        title_format = workbook.add_format({
            "bold": True,
            "font_size": 12,
            "align": "center",
            "valign": "vcenter",
        })
        
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
        
        cell_format_left = workbook.add_format({
            "align": "left",
            "valign": "vcenter",
            "border": 1,
        })
        
        worksheet.set_column("A:A", 12)
        worksheet.set_column("B:B", 6)
        worksheet.set_column("C:C", 35)
        worksheet.set_column("D:D", 15)
        
        worksheet.merge_range("A1:B1", f"TUẦN : {week_number}", title_format)
        worksheet.merge_range(
            "C1:D1",
            f"Từ ngày : {format_vietnamese_date(week_start)} đến ngày : {format_vietnamese_date(week_end)}",
            title_format
        )
        
        headers = ["THỨ / NGÀY", "TIẾT", "TÊN BÀI DẠY", "Lồng ghép"]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)
        
        data = self._build_report_data(
            timetables, teaching_programs, weekly_logs, week_number
        )
        
        row_idx = 3
        current_day = None
        for row in data[1:]:
            day_name = row[0]
            if day_name and day_name != current_day:
                current_day = day_name
                day_date = week_start + timedelta(days=int(day_name.split()[1]) - 2)
                day_display = f"{day_name}\n{day_date.strftime('%d/%m')}"
            else:
                day_display = ""
            
            subject_code = row[2] if len(row) > 2 else ""
            lesson_name = row[3] if len(row) > 3 else ""
            lesson_display = f"{subject_code} - {lesson_name}" if subject_code else lesson_name
            
            worksheet.write(row_idx, 0, day_display, cell_format)
            worksheet.write(row_idx, 1, row[1], cell_format)
            worksheet.write(row_idx, 2, lesson_display, cell_format_left)
            worksheet.write(row_idx, 3, row[4] if len(row) > 4 else "", cell_format_left)
            row_idx += 1
        
        signature_row = row_idx + 2
        worksheet.write(signature_row, 0, "Duyệt của Tổ trưởng CM", cell_format_left)
        worksheet.write(
            signature_row, 2,
            f"Long Tiên ngày ... tháng ... năm {datetime.now().year}",
            cell_format_left
        )
        worksheet.write(signature_row + 1, 2, "GVPT", cell_format_left)
        worksheet.write(signature_row + 2, 2, user.full_name, cell_format_left)
        
        workbook.close()
        logger.info("Excel exported", user_id=user.id, week_number=week_number)
        return filename
    
    def _build_report_data(
        self,
        timetables: List[Timetable],
        teaching_programs: List[TeachingProgram],
        weekly_logs: List[WeeklyLog],
        week_number: int,
    ) -> List[List[str]]:
        days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6"]
        periods = [1, 2, 3, 4, 5]
        
        subject_lesson_map = {
            (tp.subject_name, tp.lesson_index): tp.lesson_name
            for tp in teaching_programs
        }
        
        log_map = {
            (log.day_of_week, log.period_index): {
                "subject_name": log.subject_name,
                "lesson_name": log.lesson_name,
                "notes": log.notes or "",
            }
            for log in weekly_logs
        }
        
        timetable_map = {
            (t.day_of_week, t.period_index): t for t in timetables
        }
        
        data = [["Thứ", "Tiết", "Môn học", "Tên bài dạy", "Lồng ghép"]]
        lesson_counter = defaultdict(lambda: defaultdict(int))
        
        for day_idx, day in enumerate(days, start=2):
            for period in periods:
                if (day_idx, period) in log_map:
                    log_entry = log_map[(day_idx, period)]
                    subject_display = log_entry["subject_name"]
                    lesson_display = log_entry["lesson_name"]
                    integration = log_entry.get("notes", "") or ""
                    data.append(
                        [
                            day if period == 1 else "",
                            str(period),
                            subject_display,
                            lesson_display,
                            integration,
                        ]
                    )
                elif (day_idx, period) in timetable_map:
                    timetable = timetable_map[(day_idx, period)]
                    subject = timetable.subject_name
                    lesson_counter[subject][week_number] += 1
                    lesson_index = lesson_counter[subject][week_number]
                    lesson_name = subject_lesson_map.get((subject, lesson_index), "")
                    data.append(
                        [
                            day if period == 1 else "",
                            str(period),
                            subject,
                            lesson_name,
                            "",
                        ]
                    )
                else:
                    data.append(
                        [
                            day if period == 1 else "",
                            str(period),
                            "",
                            "",
                            "",
                        ]
                    )
        
        return data
