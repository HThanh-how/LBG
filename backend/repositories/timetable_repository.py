from sqlalchemy.orm import Session
from typing import List, Optional
from models import Timetable
from core.logging_config import get_logger

logger = get_logger(__name__)


class TimetableRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_user_id(self, user_id: int) -> List[Timetable]:
        return self.db.query(Timetable).filter(Timetable.user_id == user_id).all()
    
    def get_by_user_and_schedule(
        self, user_id: int, day_of_week: int, period_index: int
    ) -> Optional[Timetable]:
        return (
            self.db.query(Timetable)
            .filter(
                Timetable.user_id == user_id,
                Timetable.day_of_week == day_of_week,
                Timetable.period_index == period_index,
            )
            .first()
        )
    
    def delete_by_user_id(self, user_id: int) -> int:
        count = self.db.query(Timetable).filter(Timetable.user_id == user_id).delete()
        self.db.commit()
        logger.info("Timetables deleted", user_id=user_id, count=count)
        return count
    
    def bulk_create(self, timetables: List[dict]) -> List[Timetable]:
        db_timetables = [Timetable(**t) for t in timetables]
        self.db.bulk_save_objects(db_timetables)
        self.db.commit()
        logger.info("Timetables created", count=len(db_timetables))
        return db_timetables


