#!/usr/bin/env python3
"""
Script để import TKB (Thời khóa biểu) từ file Word/Excel hoặc dữ liệu trực tiếp
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import User, Class, Timetable
from core.logging_config import get_logger
import re

logger = get_logger(__name__)


def create_or_get_class(db: Session, user_id: int, class_name: str, grade: str = None, school_year: str = None) -> Class:
    """
    Tạo hoặc lấy class từ database
    """
    class_obj = db.query(Class).filter(
        Class.user_id == user_id,
        Class.class_name == class_name
    ).first()
    
    if not class_obj:
        class_obj = Class(
            user_id=user_id,
            class_name=class_name,
            grade=grade,
            school_year=school_year
        )
        db.add(class_obj)
        db.commit()
        db.refresh(class_obj)
        logger.info(f"Đã tạo lớp: {class_name}")
    else:
        logger.info(f"Đã tìm thấy lớp: {class_name} (ID: {class_obj.id})")
    
    return class_obj


def parse_subject_code(subject_text: str) -> str:
    """
    Parse mã môn học từ text
    TOÁN -> TOÁN
    TV -> TIẾNG VIỆT
    AN -> ÂM NHẠC (hoặc AN TOÀN GIAO THÔNG nếu trong context)
    TD -> GIÁO DỤC THỂ CHẤT
    ĐĐ -> ĐẠO ĐỨC
    HĐTN -> HOẠT ĐỘNG TRẢI NGHIỆM
    MT -> MĨ THUẬT
    TNXH -> TỰ NHIÊN XÃ HỘI
    CC-HĐTN -> HOẠT ĐỘNG TRẢI NGHIỆM
    HĐTN-TĐT -> HOẠT ĐỘNG TRẢI NGHIỆM
    SHL -> SINH HOẠT LỚP
    """
    subject_text = subject_text.strip().upper()
    
    subject_mapping = {
        'TOÁN': 'TOÁN',
        'TV': 'TIẾNG VIỆT',  # Xác nhận: TV = Tiếng Việt
        'AN': 'ÂM NHẠC',  # Mặc định là Âm nhạc, nhưng có thể là An toàn giao thông trong context khác
        'TD': 'GIÁO DỤC THỂ CHẤT',
        'ĐĐ': 'ĐẠO ĐỨC',
        'HĐTN': 'HOẠT ĐỘNG TRẢI NGHIỆM',
        'MT': 'MĨ THUẬT',
        'TNXH': 'TỰ NHIÊN XÃ HỘI',
        'CC-HĐTN': 'HOẠT ĐỘNG TRẢI NGHIỆM',
        'HĐTN-TĐT': 'HOẠT ĐỘNG TRẢI NGHIỆM',
        'SHL': 'SINH HOẠT LỚP',
        'SHL-HĐTN': 'HOẠT ĐỘNG TRẢI NGHIỆM',
    }
    
    # Tìm mã môn trong text (tìm chính xác trước)
    for code, full_name in subject_mapping.items():
        # Tìm chính xác code hoặc code là phần của text
        if subject_text == code or subject_text.startswith(code) or code in subject_text:
            return full_name
    
    # Nếu không tìm thấy, trả về text gốc (đã viết hoa)
    return subject_text


def import_tkb_from_data(
    db: Session,
    user_id: int,
    class_name: str,
    tkb_data: list,
    grade: str = None,
    school_year: str = "2025-2026"
):
    """
    Import TKB từ dữ liệu
    tkb_data format:
    [
        {
            "day_of_week": 2,  # 2=Thứ 2, 3=Thứ 3, ..., 6=Thứ 6
            "period": 1,  # 1-5
            "subject": "TOÁN",  # hoặc mã môn như "TV", "AN"
            "lesson_name": "Ôn tập các số đến 100"
        },
        ...
    ]
    """
    # Tạo hoặc lấy class
    class_obj = create_or_get_class(db, user_id, class_name, grade, school_year)
    
    # Xóa TKB cũ của lớp này
    deleted_count = db.query(Timetable).filter(
        Timetable.user_id == user_id,
        Timetable.class_id == class_obj.id
    ).delete()
    logger.info(f"Đã xóa {deleted_count} TKB cũ của lớp {class_name}")
    
    # Import TKB mới
    timetables = []
    for item in tkb_data:
        subject_name = parse_subject_code(item.get("subject", ""))
        if not subject_name:
            continue
        
        timetable = Timetable(
            user_id=user_id,
            class_id=class_obj.id,
            day_of_week=item["day_of_week"],
            period_index=item["period"],
            subject_name=subject_name
        )
        timetables.append(timetable)
    
    if timetables:
        db.bulk_save_objects(timetables)
        db.commit()
        logger.info(f"Đã import {len(timetables)} tiết học cho lớp {class_name}")
    
    return len(timetables)


def import_tkb_from_image_data(user_id: int = None, db: Session = None):
    """
    Import TKB từ dữ liệu trong hình ảnh (Tuần 1, lớp 2-3 và 2-6)
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
        else:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"Không tìm thấy user với ID: {user_id}")
                return
        
        logger.info(f"Đang import TKB cho user: {user.username} (ID: {user_id})")
        
        # Dữ liệu TKB Tuần ôn tập học kỳ 1 (từ hình ảnh mới)
        # Lớp 2-3
        tkb_23 = [
            # Thứ 2
            {"day_of_week": 2, "period": 1, "subject": "TV", "lesson_name": "Luyện tập viết chữ hoa I, K, L, M, N, P, Ơ.."},
            {"day_of_week": 2, "period": 2, "subject": "TV", "lesson_name": "Luyện tập đọc lưu loát, đọc hiểu"},
            {"day_of_week": 2, "period": 3, "subject": "TOÁN", "lesson_name": "Ôn tập học kỳ 1 (tiết 8)"},
            {"day_of_week": 2, "period": 4, "subject": "AN", "lesson_name": "Kiểm tra, đánh giá học kì 1"},
            {"day_of_week": 2, "period": 5, "subject": "CC-HĐTN", "lesson_name": "CĐ5: Tìm hiểu phong tục đón năm mới....."},
            
            # Thứ 3 (sửa lại period - có vẻ như period 1,2 bị thiếu trong hình)
            {"day_of_week": 3, "period": 1, "subject": "TV", "lesson_name": "Luyện tập nói và đáp lời cảm ơn, lời khen ngợi"},
            {"day_of_week": 3, "period": 2, "subject": "TV", "lesson_name": "Luyện tập đọc lưu loát, đọc hiểu."},
            {"day_of_week": 3, "period": 3, "subject": "TOÁN", "lesson_name": "Ôn tập học kỳ 1 (tiết 9)"},
            {"day_of_week": 3, "period": 4, "subject": "ĐĐ", "lesson_name": "Kiểm tra, đánh giá học kì 1"},
            {"day_of_week": 3, "period": 5, "subject": "TNXH", "lesson_name": "Bài 17: TH: Tìm hiểu môi trường sống của thực vật ..."},
            
            # Thứ 4
            {"day_of_week": 4, "period": 1, "subject": "TV", "lesson_name": "Luyện tập nghe - viết: Cánh cửa nhớ bà"},
            {"day_of_week": 4, "period": 2, "subject": "TV", "lesson_name": "Luyện tập dấu chấm, dấu chấm hỏi, dấu chấm than"},
            {"day_of_week": 4, "period": 3, "subject": "TOÁN", "lesson_name": "Thực hành và trải nghiệm: Đi tàu trên sông(t1)"},
            {"day_of_week": 4, "period": 4, "subject": "HĐTN", "lesson_name": "Chủ đề 5: Hoạt động 3, 4"},
            # Period 5 trống
            
            # Thứ 5
            {"day_of_week": 5, "period": 1, "subject": "TV", "lesson_name": "Đọc thành tiếng Cá chuồn tập bay"},
            {"day_of_week": 5, "period": 2, "subject": "TV", "lesson_name": "Đọc hiểu Bữa tiệc ba mươi sáu món"},
            {"day_of_week": 5, "period": 3, "subject": "MT", "lesson_name": ""},
            {"day_of_week": 5, "period": 4, "subject": "TOÁN", "lesson_name": "Thực hành và trải nghiệm: Đi tàu trên sông(t2)"},
            {"day_of_week": 5, "period": 5, "subject": "TNXH", "lesson_name": "Bài 17: TH: Tìm hiểu môi trường sống của thực vật ..."},
            
            # Thứ 6
            {"day_of_week": 6, "period": 1, "subject": "TV", "lesson_name": "Nghe - viết Bữa tiệc ba mươi sáu món"},
            {"day_of_week": 6, "period": 2, "subject": "TV", "lesson_name": "Giới thiệu một đồ dùng học tập"},
            {"day_of_week": 6, "period": 3, "subject": "TOÁN", "lesson_name": "Kiểm tra cuối kì 1"},
            {"day_of_week": 6, "period": 4, "subject": "SHL-HĐTN", "lesson_name": "CĐ5: Làm sản phẩm chuẩn bị cho Hội chơi Xuân"},
            # Period 5 trống
        ]
        
        # Dữ liệu TKB Tuần 1 (từ hình ảnh đầu tiên) - giữ lại cho lớp 2-6
        tkb_26_week1 = [
            # Thứ 2
            {"day_of_week": 2, "period": 1, "subject": "TOÁN", "lesson_name": "Ôn tập các số đến 100"},
            {"day_of_week": 2, "period": 2, "subject": "AN", "lesson_name": ""},
            {"day_of_week": 2, "period": 3, "subject": "TV", "lesson_name": "Bé Mai đã lớn (tiết 1)"},
            {"day_of_week": 2, "period": 4, "subject": "TV", "lesson_name": "Bé Mai đã lớn (tiết 2)"},
            {"day_of_week": 2, "period": 5, "subject": "CC-HĐTN", "lesson_name": "Khai giảng năm học mới"},
            
            # Thứ 3
            {"day_of_week": 3, "period": 1, "subject": "TOÁN", "lesson_name": "Ôn tập các số đến 100 (tiết 2)"},
            {"day_of_week": 3, "period": 2, "subject": "TV", "lesson_name": "Từ và câu"},
            {"day_of_week": 3, "period": 3, "subject": "TV", "lesson_name": "Viết: Chữ hoa A"},
            {"day_of_week": 3, "period": 4, "subject": "TD", "lesson_name": ""},
            {"day_of_week": 3, "period": 5, "subject": "ĐĐ", "lesson_name": "Quý trọng thời gian"},
            
            # Thứ 4
            {"day_of_week": 4, "period": 1, "subject": "TV", "lesson_name": "Đọc: Thời gian biểu"},
            {"day_of_week": 4, "period": 2, "subject": "TV", "lesson_name": "Nghe- viết: Bé Mai đã lớn"},
            {"day_of_week": 4, "period": 3, "subject": "TOÁN", "lesson_name": "Ước lượng (tiết 1)"},
            {"day_of_week": 4, "period": 4, "subject": "HĐTN", "lesson_name": "Chủ đề 1: Hoạt động 1, 2"},
            {"day_of_week": 4, "period": 5, "subject": "MT", "lesson_name": ""},
            
            # Thứ 5
            {"day_of_week": 5, "period": 1, "subject": "TV", "lesson_name": "Mở rộng vốn từ trẻ em"},
            {"day_of_week": 5, "period": 2, "subject": "TV", "lesson_name": "Nói và đáp lời khen ngợi, lời bày tỏ .."},
            {"day_of_week": 5, "period": 3, "subject": "TD", "lesson_name": ""},
            {"day_of_week": 5, "period": 4, "subject": "TOÁN", "lesson_name": "Ước lượng (tiết 2)"},
            {"day_of_week": 5, "period": 5, "subject": "TNXH", "lesson_name": "Các thế hệ trong gia đình (tiết 1)"},
            
            # Thứ 6
            {"day_of_week": 6, "period": 1, "subject": "TOÁN", "lesson_name": "Số hạng- tổng (tiết 1)"},
            {"day_of_week": 6, "period": 2, "subject": "TV", "lesson_name": "Nói, viết lời tự giới thiệu"},
            {"day_of_week": 6, "period": 3, "subject": "TV", "lesson_name": "Đọc một truyện về trẻ em"},
            {"day_of_week": 6, "period": 4, "subject": "TNXH", "lesson_name": "Các thế hệ trong gia đình (tiết 2)"},
            {"day_of_week": 6, "period": 5, "subject": "HĐTN-TĐT", "lesson_name": "Sinh hoạt lớp tuần 1"},
        ]
        
        # Import cho lớp 2-3
        count_23 = import_tkb_from_data(db, user_id, "2-3", tkb_23, grade="2", school_year="2025-2026")
        
        # Import cho lớp 2-6 (giả sử cùng TKB, có thể điều chỉnh sau)
        count_26 = import_tkb_from_data(db, user_id, "2-6", tkb_23, grade="2", school_year="2025-2026")
        
        logger.info(f"\nTổng kết:")
        logger.info(f"  Lớp 2-3: {count_23} tiết học")
        logger.info(f"  Lớp 2-6: {count_26} tiết học")
        logger.info("Import TKB thành công!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi import TKB: {str(e)}", exc_info=True)
        raise
    finally:
        if should_close:
            db.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Import TKB vào database')
    parser.add_argument('--user-id', type=int, help='ID của user (mặc định: user đầu tiên)')
    parser.add_argument('--from-image', action='store_true', help='Import từ dữ liệu hình ảnh (Tuần 1)')
    
    args = parser.parse_args()
    
    if args.from_image:
        import_tkb_from_image_data(user_id=args.user_id)
    else:
        logger.info("Sử dụng --from-image để import từ dữ liệu hình ảnh")
        logger.info("Hoặc tạo file Excel/Word với format tương tự và sử dụng excel_service.process_tkb_file")


if __name__ == "__main__":
    main()

