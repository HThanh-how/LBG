from datetime import datetime, timedelta


def get_week_dates(year: int, week_number: int, start_date: datetime = None) -> tuple:
    if start_date is None:
        start_date = datetime(year, 9, 1)
    
    first_monday = start_date
    while first_monday.weekday() != 0:
        first_monday += timedelta(days=1)
    
    week_start = first_monday + timedelta(weeks=week_number - 1)
    week_end = week_start + timedelta(days=4)
    
    return week_start, week_end


def format_vietnamese_date(date: datetime) -> str:
    return f"{date.day} / {date.month} / {date.year}"


