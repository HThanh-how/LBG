from sqlalchemy.orm import Session
from typing import List, Optional
from models import TeachingProgram
from core.logging_config import get_logger

logger = get_logger(__name__)


class TeachingProgramRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_user_id(self, user_id: int) -> List[TeachingProgram]:
        return (
            self.db.query(TeachingProgram)
            .filter(TeachingProgram.user_id == user_id)
            .all()
        )
    
    def get_by_subject_and_lesson(
        self, user_id: int, subject_name: str, lesson_index: int
    ) -> Optional[TeachingProgram]:
        return (
            self.db.query(TeachingProgram)
            .filter(
                TeachingProgram.user_id == user_id,
                TeachingProgram.subject_name == subject_name,
                TeachingProgram.lesson_index == lesson_index,
            )
            .first()
        )
    
    def delete_by_user_id(self, user_id: int) -> int:
        count = (
            self.db.query(TeachingProgram)
            .filter(TeachingProgram.user_id == user_id)
            .delete()
        )
        self.db.commit()
        logger.info("Teaching programs deleted", user_id=user_id, count=count)
        return count
    
    def bulk_create(self, programs: List[dict]) -> List[TeachingProgram]:
        db_programs = [TeachingProgram(**p) for p in programs]
        self.db.bulk_save_objects(db_programs)
        self.db.commit()
        logger.info("Teaching programs created", count=len(db_programs))
        return db_programs


