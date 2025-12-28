#!/usr/bin/env python3
"""
Script để cập nhật cấu hình cho các lớp (Tổ trưởng chuyên môn và GVPT)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import User, Class
from core.logging_config import get_logger

logger = get_logger(__name__)


def update_class_config(
    class_name: str,
    reviewer_name: str = None,
    teacher_name: str = None,
    user_id: int = None,
    db: Session = None
):
    """
    Cập nhật cấu hình cho lớp
    """
    if db is None:
        db = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        if user_id is None:
            user = db.query(User).first()
            if not user:
                logger.error("Không tìm thấy user trong database")
                return
            user_id = user.id
        
        class_obj = db.query(Class).filter(
            Class.user_id == user_id,
            Class.class_name == class_name
        ).first()
        
        if not class_obj:
            logger.error(f"Không tìm thấy lớp: {class_name}")
            return
        
        if reviewer_name:
            class_obj.reviewer_name = reviewer_name
            logger.info(f"Đã cập nhật Tổ trưởng chuyên môn cho lớp {class_name}: {reviewer_name}")
        
        if teacher_name:
            class_obj.teacher_name = teacher_name
            logger.info(f"Đã cập nhật GVPT cho lớp {class_name}: {teacher_name}")
        
        db.commit()
        logger.info(f"Cập nhật thành công cho lớp {class_name}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi cập nhật: {str(e)}", exc_info=True)
        raise
    finally:
        if should_close:
            db.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cập nhật cấu hình lớp')
    parser.add_argument('--class-name', required=True, help='Tên lớp (ví dụ: 2-3)')
    parser.add_argument('--reviewer-name', help='Tên Tổ trưởng chuyên môn')
    parser.add_argument('--teacher-name', help='Tên Giáo viên phụ trách (GVPT)')
    parser.add_argument('--user-id', type=int, help='ID của user')
    
    args = parser.parse_args()
    
    update_class_config(
        args.class_name,
        reviewer_name=args.reviewer_name,
        teacher_name=args.teacher_name,
        user_id=args.user_id
    )


if __name__ == "__main__":
    main()

