from sqlalchemy.orm import Session
from fastapi import UploadFile
from typing import Dict, List
import pandas as pd
from io import BytesIO

from repositories.timetable_repository import TimetableRepository
from repositories.teaching_program_repository import TeachingProgramRepository
from core.exceptions import BadRequestException, ValidationException
from core.logging_config import get_logger

logger = get_logger(__name__)


class ExcelService:
    def __init__(self, db: Session):
        self.db = db
        self.timetable_repo = TimetableRepository(db)
        self.teaching_program_repo = TeachingProgramRepository(db)
    
    def process_tkb_file(
        self, file: UploadFile, user_id: int
    ) -> Dict[str, int]:
        try:
            contents = file.file.read()
            df = pd.read_excel(BytesIO(contents))
            
            self.timetable_repo.delete_by_user_id(user_id)
            
            day_mapping = {
                "Thứ 2": 2,
                "Thứ 3": 3,
                "Thứ 4": 4,
                "Thứ 5": 5,
                "Thứ 6": 6,
            }
            
            timetables = []
            records_count = 0
            
            for _, row in df.iterrows():
                day_str = str(row.get("Thứ", "")).strip()
                day_of_week = day_mapping.get(day_str)
                
                if not day_of_week:
                    continue
                
                for period in range(1, 6):
                    period_col = f"Tiết {period}"
                    subject = str(row.get(period_col, "")).strip()
                    
                    if subject and subject.lower() not in ["", "nan", "none"]:
                        timetables.append({
                            "user_id": user_id,
                            "day_of_week": day_of_week,
                            "period_index": period,
                            "subject_name": subject,
                        })
                        records_count += 1
            
            if timetables:
                self.timetable_repo.bulk_create(timetables)
            
            logger.info(
                "TKB processed",
                user_id=user_id,
                records_count=records_count,
            )
            
            return {"records_processed": records_count}
        except Exception as e:
            logger.error("Error processing TKB file", error=str(e), exc_info=True)
            raise BadRequestException(f"Error processing TKB file: {str(e)}")
    
    def process_ctgd_file(
        self, file: UploadFile, user_id: int
    ) -> Dict[str, int]:
        try:
            contents = file.file.read()
            df = pd.read_excel(BytesIO(contents))
            
            required_columns = ["Môn học", "Tiết thứ", "Tên bài"]
            missing_columns = [
                col for col in required_columns if col not in df.columns
            ]
            
            if missing_columns:
                raise ValidationException(
                    f"Missing required columns: {', '.join(missing_columns)}"
                )
            
            self.teaching_program_repo.delete_by_user_id(user_id)
            
            programs = []
            records_count = 0
            
            for _, row in df.iterrows():
                subject = str(row.get("Môn học", "")).strip()
                lesson_index = row.get("Tiết thứ")
                lesson_name = str(row.get("Tên bài", "")).strip()
                
                if not subject or not lesson_name:
                    continue
                
                try:
                    lesson_index = int(lesson_index)
                except (ValueError, TypeError):
                    continue
                
                programs.append({
                    "user_id": user_id,
                    "subject_name": subject,
                    "lesson_index": lesson_index,
                    "lesson_name": lesson_name,
                })
                records_count += 1
            
            if programs:
                self.teaching_program_repo.bulk_create(programs)
            
            logger.info(
                "CTGD processed",
                user_id=user_id,
                records_count=records_count,
            )
            
            return {"records_processed": records_count}
        except ValidationException:
            raise
        except Exception as e:
            logger.error("Error processing CTGD file", error=str(e), exc_info=True)
            raise BadRequestException(f"Error processing CTGD file: {str(e)}")

