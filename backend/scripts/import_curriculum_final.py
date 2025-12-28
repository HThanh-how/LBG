#!/usr/bin/env python3
"""
Script để import khung chương trình từ file Word vào database
Version Final: Xử lý đúng format của file Word
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from docx import Document
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import User, TeachingProgram
from core.logging_config import get_logger
import re

logger = get_logger(__name__)


def find_subjects_in_document(doc):
    """
    Tìm tất cả các môn học trong document và trả về list
    """
    subjects_found = []
    for para in doc.paragraphs:
        text = para.text.strip()
        # Tìm pattern: "MÔN TOÁN", "MÔN TIẾNG VIỆT", "2. MÔN TIẾNG VIỆT", etc.
        match = re.match(r'^(\d+\.\s*)?MÔN\s+(.+)$', text, re.IGNORECASE)
        if match:
            subject_name = match.group(2).strip()
            # Loại bỏ số đầu nếu có
            subject_name = re.sub(r'^\d+\.\s*', '', subject_name)
            subjects_found.append(subject_name)
    return subjects_found


def parse_lesson_name_and_tiets(lesson_text, tiets_text):
    """
    Parse tên bài và số tiết từ text
    Trả về list các bài: [(lesson_name, tiết_number), ...]
    """
    lessons = []
    
    # Làm sạch text
    lesson_text = lesson_text.strip()
    tiets_text = tiets_text.strip()
    
    # Parse số tiết từ cột "Tiết học"
    tiets_list = []
    if tiets_text:
        # Tìm các pattern: "Tiết 1, 2", "1 tiết", "2 tiết", "Tiết 1\nTiết 2"
        tiets_matches = re.findall(r'Tiết\s+(\d+)', tiets_text, re.IGNORECASE)
        if tiets_matches:
            tiets_list = [int(t) for t in tiets_matches]
        else:
            # Tìm pattern "1 tiết", "2 tiết"
            tiets_matches = re.findall(r'(\d+)\s+tiết', tiets_text, re.IGNORECASE)
            if tiets_matches:
                # Nếu có "1 tiết", "2 tiết" thì tạo các tiết liên tiếp
                total_tiets = sum(int(t) for t in tiets_matches)
                if total_tiets > 0:
                    # Tìm tiết bắt đầu từ lesson_text hoặc từ context
                    start_tiet_match = re.search(r'\(tiết\s+(\d+)', lesson_text, re.IGNORECASE)
                    if start_tiet_match:
                        start_tiet = int(start_tiet_match.group(1))
                        tiets_list = list(range(start_tiet, start_tiet + total_tiets))
                    else:
                        # Không tìm thấy, tạo từ 1
                        tiets_list = list(range(1, total_tiets + 1))
    
    # Parse tên bài từ lesson_text
    # Có thể có format:
    # "- Bài 1: Tên bài (tiết 1, 2)"
    # "- Đọc: Tên bài\n- Viết: ..."
    # "Bài 1: Tên bài\n- Đọc: ..."
    
    if not tiets_list:
        # Nếu không có số tiết, thử tìm trong lesson_text
        tiets_matches = re.findall(r'\(tiết\s+(\d+)', lesson_text, re.IGNORECASE)
        if tiets_matches:
            tiets_list = [int(t) for t in tiets_matches]
    
    # Tách các bài trong lesson_text (mỗi dòng bắt đầu bằng "-" hoặc "Bài")
    lines = lesson_text.split('\n')
    current_lesson = ""
    lesson_index = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Nếu dòng bắt đầu bằng "Bài X:" hoặc "- Bài X:"
        lesson_match = re.match(r'[-]?\s*Bài\s+(\d+)[:\s]+(.+)', line, re.IGNORECASE)
        if lesson_match:
            # Lưu bài trước nếu có
            if current_lesson and tiets_list:
                for tiet in tiets_list[lesson_index:lesson_index+1] if lesson_index < len(tiets_list) else [lesson_index + 1]:
                    lessons.append((current_lesson.strip(), tiet))
                lesson_index += 1
            
            # Bắt đầu bài mới
            current_lesson = lesson_match.group(2).strip()
        else:
            # Nối vào bài hiện tại
            if current_lesson:
                current_lesson += " " + line
            else:
                current_lesson = line
    
    # Thêm bài cuối
    if current_lesson:
        if tiets_list:
            # Nếu có số tiết, tạo bài cho mỗi tiết
            for tiet in tiets_list[lesson_index:]:
                # Lấy tên bài chính (trước dấu ngoặc hoặc dấu hai chấm)
                lesson_name = current_lesson
                # Loại bỏ phần "(tiết X, Y)"
                lesson_name = re.sub(r'\(tiết\s+\d+.*?\)', '', lesson_name, flags=re.IGNORECASE)
                lesson_name = lesson_name.strip()
                if lesson_name:
                    lessons.append((lesson_name, tiet))
        else:
            # Không có số tiết, tạo 1 bài với index tự động
            lesson_name = current_lesson
            lesson_name = re.sub(r'\(tiết\s+\d+.*?\)', '', lesson_name, flags=re.IGNORECASE)
            lesson_name = lesson_name.strip()
            if lesson_name:
                lessons.append((lesson_name, 1))
    
    # Nếu không parse được gì, trả về bài với tên gốc
    if not lessons and lesson_text:
        # Làm sạch tên bài
        lesson_name = re.sub(r'\(tiết\s+\d+.*?\)', '', lesson_text, flags=re.IGNORECASE)
        lesson_name = lesson_name.strip()
        if lesson_name:
            if tiets_list:
                for tiet in tiets_list:
                    lessons.append((lesson_name, tiet))
            else:
                lessons.append((lesson_name, 1))
    
    return lessons


def parse_curriculum_docx(file_path: str) -> list:
    """
    Đọc và parse file Word chứa khung chương trình
    """
    doc = Document(file_path)
    programs = []
    
    logger.info(f"Đang đọc file: {file_path}")
    logger.info(f"Tổng số bảng: {len(doc.tables)}")
    
    # Tìm tất cả môn học trong document
    subjects_list = find_subjects_in_document(doc)
    logger.info(f"Tìm thấy {len(subjects_list)} môn học trong document: {', '.join(subjects_list)}")
    
    # Xử lý từng bảng - map với môn học theo thứ tự
    # Bỏ qua bảng đầu tiên (thường là header)
    table_start_idx = 1 if len(doc.tables) > len(subjects_list) else 0
    
    for table_idx, table in enumerate(doc.tables):
        logger.info(f"\nĐang xử lý bảng {table_idx + 1}/{len(doc.tables)}...")
        
        # Map bảng với môn học (bỏ qua bảng đầu nếu có)
        subject_idx = table_idx - table_start_idx
        if subject_idx < 0 or subject_idx >= len(subjects_list):
            logger.warning(f"  Không có môn học tương ứng cho bảng {table_idx + 1}, bỏ qua")
            continue
        
        subject = subjects_list[subject_idx]
        if not subject:
            logger.warning(f"  Không tìm thấy tên môn học cho bảng {table_idx + 1}, bỏ qua")
            continue
        
        logger.info(f"  Môn học: {subject}")
        
        # Tìm header row (thường là hàng 1 hoặc 2)
        header_row_idx = None
        week_col = None
        topic_col = None
        lesson_col = None
        tiet_col = None
        
        for row_idx in range(min(3, len(table.rows))):
            row = table.rows[row_idx]
            cells = [cell.text.strip() for cell in row.cells]
            
            # Tìm các cột
            for col_idx, cell_text in enumerate(cells):
                cell_upper = cell_text.upper()
                if 'TUẦN' in cell_upper or 'THÁNG' in cell_upper:
                    week_col = col_idx
                if 'CHỦ ĐỀ' in cell_upper or 'MẠCH' in cell_upper:
                    topic_col = col_idx
                if 'TÊN BÀI' in cell_upper or 'BÀI HỌC' in cell_upper:
                    lesson_col = col_idx
                if 'TIẾT' in cell_upper and 'HỌC' in cell_upper:
                    tiet_col = col_idx
            
            if lesson_col is not None:
                header_row_idx = row_idx
                break
        
        if header_row_idx is None:
            logger.warning(f"  Không tìm thấy header row trong bảng {table_idx + 1}")
            continue
        
        # Đoán cột nếu chưa tìm thấy
        if lesson_col is None and len(table.rows) > header_row_idx:
            # Thường cột 2 hoặc 3 là tên bài
            if len(table.rows[header_row_idx + 1].cells) >= 3:
                lesson_col = 2
        
        if tiet_col is None and len(table.rows) > header_row_idx:
            # Thường cột 3 hoặc 4 là số tiết
            if len(table.rows[header_row_idx + 1].cells) >= 4:
                tiet_col = 3
        
        # Đọc dữ liệu từ các hàng sau header
        lesson_counter = {}  # Đếm số tiết cho mỗi môn để tự động tăng nếu thiếu
        
        for row_idx in range(header_row_idx + 1, len(table.rows)):
            row = table.rows[row_idx]
            cells = [cell.text.strip() for cell in row.cells]
            
            if not any(cells):
                continue
            
            # Lấy tên bài và số tiết
            lesson_text = ""
            tiets_text = ""
            
            if lesson_col is not None and lesson_col < len(cells):
                lesson_text = cells[lesson_col]
            
            if tiet_col is not None and tiet_col < len(cells):
                tiets_text = cells[tiet_col]
            
            if not lesson_text:
                continue
            
            # Parse bài học
            parsed_lessons = parse_lesson_name_and_tiets(lesson_text, tiets_text)
            
            for lesson_name, tiet_num in parsed_lessons:
                if not lesson_name:
                    continue
                
                # Đảm bảo số tiết tăng dần
                if subject not in lesson_counter:
                    lesson_counter[subject] = 0
                
                # Nếu số tiết không hợp lệ, tự động tăng
                if tiet_num <= 0 or tiet_num < lesson_counter[subject]:
                    lesson_counter[subject] += 1
                    tiet_num = lesson_counter[subject]
                else:
                    lesson_counter[subject] = max(lesson_counter[subject], tiet_num)
                
                programs.append({
                    "subject_name": subject,
                    "lesson_index": tiet_num,
                    "lesson_name": lesson_name
                })
        
        logger.info(f"  Đã parse được {len([p for p in programs if p['subject_name'] == subject])} bài học")
    
    # Sắp xếp và loại bỏ trùng lặp
    programs.sort(key=lambda x: (x["subject_name"], x["lesson_index"]))
    
    seen = set()
    unique_programs = []
    for prog in programs:
        key = (prog["subject_name"], prog["lesson_index"])
        if key not in seen:
            seen.add(key)
            unique_programs.append(prog)
        else:
            # Nếu trùng, giữ lại bản có tên bài dài hơn (thường đầy đủ hơn)
            existing = next(p for p in unique_programs if (p["subject_name"], p["lesson_index"]) == key)
            if len(prog["lesson_name"]) > len(existing["lesson_name"]):
                existing["lesson_name"] = prog["lesson_name"]
    
    logger.info(f"\nTổng kết: Đã parse được {len(unique_programs)} bài học từ {len(set(p['subject_name'] for p in unique_programs))} môn học")
    
    subjects = sorted(set(p['subject_name'] for p in unique_programs))
    logger.info(f"Các môn học: {', '.join(subjects)}")
    
    return unique_programs


def import_to_database(programs: list, user_id: int = None, db: Session = None):
    """Import danh sách bài học vào database"""
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
        
        logger.info(f"Đang import cho user: {user.username} (ID: {user_id})")
        
        # Xóa các chương trình cũ
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Import khung chương trình từ file Word')
    parser.add_argument('file_path', help='Đường dẫn đến file Word')
    parser.add_argument('--user-id', type=int, help='ID của user (mặc định: user đầu tiên)')
    parser.add_argument('--dry-run', action='store_true', help='Chỉ parse, không import vào database')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        logger.error(f"File không tồn tại: {args.file_path}")
        return
    
    programs = parse_curriculum_docx(args.file_path)
    
    if not programs:
        logger.warning("Không tìm thấy dữ liệu trong file")
        return
    
    # In mẫu
    logger.info("\n=== Mẫu dữ liệu (10 bài đầu) ===")
    for i, prog in enumerate(programs[:10]):
        logger.info(f"{i+1}. {prog['subject_name']} - Tiết {prog['lesson_index']}: {prog['lesson_name'][:80]}")
    
    if not args.dry_run:
        import_to_database(programs, user_id=args.user_id)
    else:
        logger.info("\n=== DRY RUN - Không import vào database ===")


if __name__ == "__main__":
    main()

