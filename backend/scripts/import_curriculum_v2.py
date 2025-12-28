#!/usr/bin/env python3
"""
Script để import khung chương trình từ file Word vào database
Version 2: Cải thiện logic đọc file
"""
import sys
import os
from pathlib import Path

# Thêm thư mục backend vào path
sys.path.insert(0, str(Path(__file__).parent.parent))

from docx import Document
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import User, TeachingProgram
from core.logging_config import get_logger
import re

logger = get_logger(__name__)


def is_valid_subject_name(text: str) -> bool:
    """
    Kiểm tra xem text có phải là tên môn học hợp lệ không
    """
    # Loại bỏ các text không phải môn học
    invalid_patterns = [
        r'^Đội ngũ',
        r'^Tổ trưởng',
        r'^Duyệt',
        r'^Giáo viên',
        r'^Tổng phụ trách',
        r'^Số lượng',
        r'^Tình hình',
        r'^Nguồn học',
        r'^Các nội dung',
        r'^Chương trình và sách',
        r'^Ghi chú',
        r'^Tên bài học',
        r'^Số tiết học',
        r'^HỌC KÌ',
        r'^MÔN\s+(TIẾNG|ĐẠO|TỰ NHIÊN|ÂM|HOẠT|GIÁO DỤC)',  # Các môn con trong TOÁN
    ]
    
    for pattern in invalid_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return False
    
    # Tên môn học thường là chữ in hoa hoặc có chữ cái đầu viết hoa
    # Và không quá dài (thường < 50 ký tự)
    if len(text) > 50:
        return False
    
    # Các môn học phổ biến
    valid_subjects = [
        'TOÁN', 'TIẾNG VIỆT', 'ĐẠO ĐỨC', 'TỰ NHIÊN XÃ HỘI',
        'ÂM NHẠC', 'MĨ THUẬT', 'HOẠT ĐỘNG TRẢI NGHIỆM',
        'GIÁO DỤC THỂ CHẤT', 'TIẾNG ANH', 'TIN HỌC',
        'LỊCH SỬ', 'ĐỊA LÝ', 'KHOA HỌC', 'VẬT LÝ', 'HÓA HỌC',
        'SINH HỌC', 'NGỮ VĂN', 'GDCD'
    ]
    
    text_upper = text.upper().strip()
    for valid in valid_subjects:
        if valid in text_upper or text_upper in valid:
            return True
    
    # Nếu text là tất cả chữ in hoa và có độ dài hợp lý
    if text.isupper() and 3 <= len(text) <= 30:
        return True
    
    return False


def parse_curriculum_docx(file_path: str) -> list:
    """
    Đọc và parse file Word chứa khung chương trình
    Tập trung vào đọc dữ liệu từ bảng (tables)
    """
    doc = Document(file_path)
    programs = []
    current_subject = None
    
    logger.info(f"Đang đọc file: {file_path}")
    
    # Đọc từ các bảng trước (thường chứa dữ liệu chính)
    for table_idx, table in enumerate(doc.tables):
        logger.info(f"Đang xử lý bảng {table_idx + 1}...")
        
        # Tìm header row để xác định cột
        header_row = None
        stt_col = None
        lesson_name_col = None
        subject_col = None
        
        # Kiểm tra 3 hàng đầu để tìm header
        for row_idx in range(min(3, len(table.rows))):
            row = table.rows[row_idx]
            cells = [cell.text.strip() for cell in row.cells]
            
            # Tìm các cột quan trọng
            for col_idx, cell_text in enumerate(cells):
                cell_upper = cell_text.upper()
                if 'SỐ TIẾT' in cell_upper or 'TIẾT' in cell_upper or 'STT' in cell_upper:
                    stt_col = col_idx
                if 'TÊN BÀI' in cell_upper or 'NỘI DUNG' in cell_upper or 'BÀI' in cell_upper:
                    lesson_name_col = col_idx
                if 'MÔN' in cell_upper and 'HỌC' in cell_upper:
                    subject_col = col_idx
            
            # Nếu tìm thấy header, lưu lại
            if stt_col is not None or lesson_name_col is not None:
                header_row = row_idx
                break
        
        # Nếu không tìm thấy header rõ ràng, thử đoán từ hàng đầu
        if header_row is None:
            header_row = 0
            # Đoán cột: thường cột đầu là số, cột thứ 2 là tên bài
            if len(table.rows) > 0:
                first_row_cells = [cell.text.strip() for cell in table.rows[0].cells]
                if len(first_row_cells) >= 2:
                    # Nếu cột đầu là số, đó là số tiết
                    if re.match(r'^\d+$', first_row_cells[0]):
                        stt_col = 0
                        lesson_name_col = 1
                    # Nếu cột thứ 2 là số, cột đầu là tên bài
                    elif re.match(r'^\d+$', first_row_cells[1]):
                        lesson_name_col = 0
                        stt_col = 1
        
        # Đọc dữ liệu từ bảng
        for row_idx in range(header_row + 1, len(table.rows)):
            row = table.rows[row_idx]
            cells = [cell.text.strip() for cell in row.cells]
            
            if not any(cells):
                continue
            
            # Tìm môn học trong hàng (nếu có cột môn học)
            if subject_col is not None and subject_col < len(cells):
                subject_text = cells[subject_col]
                if subject_text and is_valid_subject_name(subject_text):
                    current_subject = subject_text.strip()
                    logger.info(f"Tìm thấy môn học trong bảng: {current_subject}")
                    continue
            
            # Nếu chưa có môn học, bỏ qua
            if not current_subject:
                # Thử tìm môn học từ các cell
                for cell_text in cells:
                    if cell_text and is_valid_subject_name(cell_text):
                        current_subject = cell_text.strip()
                        logger.info(f"Tìm thấy môn học: {current_subject}")
                        break
                if not current_subject:
                    continue
            
            # Tìm số tiết và tên bài
            lesson_index = None
            lesson_name = None
            
            # Tìm số tiết
            if stt_col is not None and stt_col < len(cells):
                stt_text = cells[stt_col]
                if re.match(r'^\d+$', stt_text):
                    try:
                        lesson_index = int(stt_text)
                    except ValueError:
                        pass
            
            # Nếu không tìm thấy ở cột chỉ định, tìm trong tất cả các cell
            if lesson_index is None:
                for cell_text in cells:
                    if re.match(r'^\d+$', cell_text):
                        try:
                            lesson_index = int(cell_text)
                            break
                        except ValueError:
                            continue
            
            # Tìm tên bài
            if lesson_name_col is not None and lesson_name_col < len(cells):
                lesson_name = cells[lesson_name_col]
            
            # Nếu không tìm thấy ở cột chỉ định, tìm cell không phải số
            if not lesson_name:
                for cell_text in cells:
                    if cell_text and not re.match(r'^\d+$', cell_text):
                        # Bỏ qua các text không phải tên bài
                        if cell_text.upper() in ['GHI CHÚ', 'TÊN BÀI', 'NỘI DUNG', 'SỐ TIẾT']:
                            continue
                        lesson_name = cell_text
                        break
            
            # Nếu có đủ thông tin, thêm vào danh sách
            if lesson_index and lesson_name and current_subject:
                # Làm sạch tên bài
                lesson_name = lesson_name.strip()
                if len(lesson_name) > 200:  # Tên bài quá dài, có thể là lỗi
                    continue
                
                programs.append({
                    "subject_name": current_subject,
                    "lesson_index": lesson_index,
                    "lesson_name": lesson_name
                })
                logger.debug(f"  {current_subject} - Tiết {lesson_index}: {lesson_name}")
    
    # Đọc từ paragraphs (nếu cần)
    # Bỏ qua phần này vì dữ liệu chủ yếu ở trong bảng
    
    # Sắp xếp lại theo môn và số tiết
    programs.sort(key=lambda x: (x["subject_name"], x["lesson_index"]))
    
    # Loại bỏ trùng lặp (giữ lại bản đầu tiên)
    seen = set()
    unique_programs = []
    for prog in programs:
        key = (prog["subject_name"], prog["lesson_index"])
        if key not in seen:
            seen.add(key)
            unique_programs.append(prog)
    
    logger.info(f"Đã parse được {len(unique_programs)} bài học từ {len(set(p['subject_name'] for p in unique_programs))} môn học")
    
    # In danh sách môn học
    subjects = sorted(set(p['subject_name'] for p in unique_programs))
    logger.info(f"Các môn học: {', '.join(subjects)}")
    
    return unique_programs


def import_to_database(programs: list, user_id: int = None, db: Session = None):
    """
    Import danh sách bài học vào database
    """
    if db is None:
        db = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        # Lấy user đầu tiên nếu không chỉ định
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
        
        logger.info(f"Đang import cho user: {user.username} (ID: {user_id})")
        
        # Xóa các chương trình cũ của user
        existing_count = db.query(TeachingProgram).filter(TeachingProgram.user_id == user_id).delete()
        logger.info(f"Đã xóa {existing_count} chương trình cũ")
        
        # Tạo các chương trình mới
        db_programs = []
        for prog in programs:
            db_program = TeachingProgram(
                user_id=user_id,
                subject_name=prog["subject_name"],
                lesson_index=prog["lesson_index"],
                lesson_name=prog["lesson_name"]
            )
            db_programs.append(db_program)
        
        if db_programs:
            db.bulk_save_objects(db_programs)
            logger.info(f"Đã tạo {len(db_programs)} chương trình mới")
        
        db.commit()
        
        # Thống kê
        total_count = db.query(TeachingProgram).filter(TeachingProgram.user_id == user_id).count()
        subjects = db.query(TeachingProgram.subject_name).filter(
            TeachingProgram.user_id == user_id
        ).distinct().all()
        
        logger.info(f"Tổng số bài học trong database: {total_count}")
        logger.info(f"Số môn học: {len(subjects)}")
        logger.info("Import thành công!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi import: {str(e)}", exc_info=True)
        raise
    finally:
        if should_close:
            db.close()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import khung chương trình từ file Word')
    parser.add_argument('file_path', help='Đường dẫn đến file Word')
    parser.add_argument('--user-id', type=int, help='ID của user (mặc định: user đầu tiên)')
    parser.add_argument('--dry-run', action='store_true', help='Chỉ parse, không import vào database')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        logger.error(f"File không tồn tại: {args.file_path}")
        return
    
    # Parse file
    programs = parse_curriculum_docx(args.file_path)
    
    if not programs:
        logger.warning("Không tìm thấy dữ liệu trong file")
        return
    
    # In một số mẫu để kiểm tra
    logger.info("\n=== Mẫu dữ liệu (10 bài đầu) ===")
    for i, prog in enumerate(programs[:10]):
        logger.info(f"{i+1}. {prog['subject_name']} - Tiết {prog['lesson_index']}: {prog['lesson_name']}")
    
    if not args.dry_run:
        # Import vào database
        import_to_database(programs, user_id=args.user_id)
    else:
        logger.info("\n=== DRY RUN - Không import vào database ===")


if __name__ == "__main__":
    main()

