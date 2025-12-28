from sqlalchemy.orm import Session
from typing import List, Dict, Any
from collections import defaultdict

from repositories.timetable_repository import TimetableRepository
from repositories.teaching_program_repository import TeachingProgramRepository
from repositories.weekly_log_repository import WeeklyLogRepository
from models import User
from core.logging_config import get_logger

logger = get_logger(__name__)


class WeeklyReportService:
    def __init__(self, db: Session):
        self.db = db
        self.timetable_repo = TimetableRepository(db)
        self.teaching_program_repo = TeachingProgramRepository(db)
        self.weekly_log_repo = WeeklyLogRepository(db)
    
    def generate_weekly_report(
        self, user_id: int, week_number: int
    ) -> Dict[str, Any]:
        timetables = self.timetable_repo.get_by_user_id(user_id)
        teaching_programs = self.teaching_program_repo.get_by_user_id(user_id)
        weekly_logs = self.weekly_log_repo.get_by_user_and_week(
            user_id, week_number
        )
        
        days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6"]
        periods = [1, 2, 3, 4, 5]
        
        subject_lesson_map = self._build_lesson_map(teaching_programs)
        log_map = self._build_log_map(weekly_logs)
        
        report_data = []
        lesson_counter = defaultdict(lambda: defaultdict(int))
        
        for day_idx, day in enumerate(days, start=2):
            for period in periods:
                timetable = self._find_timetable(
                    timetables, day_idx, period
                )
                
                if (day_idx, period) in log_map:
                    log_entry = log_map[(day_idx, period)]
                    report_data.append({
                        "day_of_week": day,
                        "period_index": period,
                        "subject_name": log_entry["subject_name"],
                        "lesson_name": log_entry["lesson_name"],
                        "notes": log_entry.get("notes", ""),
                    })
                elif timetable:
                    subject = timetable.subject_name
                    lesson_counter[subject][week_number] += 1
                    lesson_index = lesson_counter[subject][week_number]
                    
                    lesson_name = subject_lesson_map.get(
                        (subject, lesson_index), ""
                    )
                    report_data.append({
                        "day_of_week": day,
                        "period_index": period,
                        "subject_name": subject,
                        "lesson_name": lesson_name,
                        "notes": "",
                    })
                else:
                    report_data.append({
                        "day_of_week": day,
                        "period_index": period,
                        "subject_name": "",
                        "lesson_name": "",
                        "notes": "",
                    })
        
        return {"week_number": week_number, "data": report_data}
    
    def save_weekly_report(
        self, user_id: int, week_number: int, logs: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        self.weekly_log_repo.delete_by_user_and_week(user_id, week_number)
        
        log_dicts = [
            {
                "user_id": user_id,
                "week_number": week_number,
                "day_of_week": log["day_of_week"],
                "period_index": log["period_index"],
                "subject_name": log["subject_name"],
                "lesson_name": log["lesson_name"],
                "notes": log.get("notes", ""),
            }
            for log in logs
        ]
        
        if log_dicts:
            self.weekly_log_repo.bulk_create(log_dicts)
        
        logger.info(
            "Weekly report saved",
            user_id=user_id,
            week_number=week_number,
            records_count=len(log_dicts),
        )
        
        return {"message": "Weekly report saved successfully"}
    
    def _build_lesson_map(self, teaching_programs) -> Dict[tuple, str]:
        return {
            (tp.subject_name, tp.lesson_index): tp.lesson_name
            for tp in teaching_programs
        }
    
    def _build_log_map(self, weekly_logs) -> Dict[tuple, Dict[str, str]]:
        return {
            (log.day_of_week, log.period_index): {
                "subject_name": log.subject_name,
                "lesson_name": log.lesson_name,
                "notes": log.notes or "",
            }
            for log in weekly_logs
        }
    
    def _find_timetable(self, timetables, day_of_week: int, period_index: int):
        return next(
            (
                t
                for t in timetables
                if t.day_of_week == day_of_week
                and t.period_index == period_index
            ),
            None,
        )
    
    def get_data_for_export(
        self, user: User, week_number: int
    ) -> tuple:
        timetables = self.timetable_repo.get_by_user_id(user.id)
        teaching_programs = self.teaching_program_repo.get_by_user_id(user.id)
        weekly_logs = self.weekly_log_repo.get_by_user_and_week(
            user.id, week_number
        )
        
        return timetables, teaching_programs, weekly_logs

