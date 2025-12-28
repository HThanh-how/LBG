from sqlalchemy.orm import Session
from typing import List, Optional
from models import WeeklyLog
from core.logging_config import get_logger

logger = get_logger(__name__)


class WeeklyLogRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_user_and_week(
        self, user_id: int, week_number: int
    ) -> List[WeeklyLog]:
        return (
            self.db.query(WeeklyLog)
            .filter(
                WeeklyLog.user_id == user_id,
                WeeklyLog.week_number == week_number,
            )
            .all()
        )
    
    def delete_by_user_and_week(self, user_id: int, week_number: int) -> int:
        count = (
            self.db.query(WeeklyLog)
            .filter(
                WeeklyLog.user_id == user_id,
                WeeklyLog.week_number == week_number,
            )
            .delete()
        )
        self.db.commit()
        logger.info(
            "Weekly logs deleted",
            user_id=user_id,
            week_number=week_number,
            count=count,
        )
        return count
    
    def bulk_create(self, logs: List[dict]) -> List[WeeklyLog]:
        db_logs = [WeeklyLog(**log) for log in logs]
        self.db.bulk_save_objects(db_logs)
        self.db.commit()
        logger.info("Weekly logs created", count=len(db_logs))
        return db_logs

