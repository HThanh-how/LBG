from datetime import date
from typing import List, Dict
from models import Holiday


def get_vietnam_holidays(year: int) -> List[Dict[str, any]]:
    """
    Lấy danh sách ngày nghỉ lễ mặc định của Việt Nam
    """
    holidays = [
        {"date": date(year, 1, 1), "name": "Tết Dương lịch"},
        {"date": date(year, 4, 30), "name": "Ngày Giải phóng miền Nam"},
        {"date": date(year, 5, 1), "name": "Ngày Quốc tế Lao động"},
        {"date": date(year, 9, 2), "name": "Quốc khánh"},
    ]
    
    # Tết Nguyên Đán (âm lịch) - tính toán đơn giản
    # Năm 2024: 10-16/2, 2025: 29/1-4/2, 2026: 17-23/2
    tet_dates = {
        2024: [(date(2024, 2, 10), "Tết Nguyên Đán"), (date(2024, 2, 11), "Tết Nguyên Đán"), 
                (date(2024, 2, 12), "Tết Nguyên Đán"), (date(2024, 2, 13), "Tết Nguyên Đán"),
                (date(2024, 2, 14), "Tết Nguyên Đán"), (date(2024, 2, 15), "Tết Nguyên Đán"),
                (date(2024, 2, 16), "Tết Nguyên Đán")],
        2025: [(date(2025, 1, 29), "Tết Nguyên Đán"), (date(2025, 1, 30), "Tết Nguyên Đán"),
                (date(2025, 1, 31), "Tết Nguyên Đán"), (date(2025, 2, 1), "Tết Nguyên Đán"),
                (date(2025, 2, 2), "Tết Nguyên Đán"), (date(2025, 2, 3), "Tết Nguyên Đán"),
                (date(2025, 2, 4), "Tết Nguyên Đán")],
        2026: [(date(2026, 2, 17), "Tết Nguyên Đán"), (date(2026, 2, 18), "Tết Nguyên Đán"),
                (date(2026, 2, 19), "Tết Nguyên Đán"), (date(2026, 2, 20), "Tết Nguyên Đán"),
                (date(2026, 2, 21), "Tết Nguyên Đán"), (date(2026, 2, 22), "Tết Nguyên Đán"),
                (date(2026, 2, 23), "Tết Nguyên Đán")],
    }
    
    if year in tet_dates:
        for tet_date, name in tet_dates[year]:
            holidays.append({"date": tet_date, "name": name})
    
    return holidays


def create_default_holidays(db, user_id: int, year: int = None):
    """
    Tạo ngày nghỉ lễ mặc định cho user
    """
    from datetime import datetime
    if year is None:
        year = datetime.now().year
    
    existing_holidays = db.query(Holiday).filter(
        Holiday.user_id == user_id,
        Holiday.holiday_date >= date(year, 1, 1),
        Holiday.holiday_date <= date(year, 12, 31),
    ).all()
    
    existing_dates = {h.holiday_date for h in existing_holidays}
    
    default_holidays = get_vietnam_holidays(year)
    new_holidays = []
    
    for holiday_data in default_holidays:
        if holiday_data["date"] not in existing_dates:
            new_holiday = Holiday(
                user_id=user_id,
                holiday_date=holiday_data["date"],
                holiday_name=holiday_data["name"],
                is_moved=0,
            )
            new_holidays.append(new_holiday)
    
    if new_holidays:
        db.bulk_save_objects(new_holidays)
        db.commit()
    
    return len(new_holidays)


