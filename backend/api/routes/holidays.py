from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from api.dependencies import get_current_user, get_db
from models import User, Holiday
from schemas import HolidayCreate, HolidayResponse
from core.logging_config import get_logger
from utils.holidays import create_default_holidays

logger = get_logger(__name__)

router = APIRouter(prefix="/holidays", tags=["Holidays"])


@router.get("", response_model=list[HolidayResponse])
def get_holidays(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    year: int = Query(None, description="Năm để tạo ngày nghỉ mặc định"),
):
    holidays = db.query(Holiday).filter(Holiday.user_id == current_user.id).all()
    
    # Nếu không có ngày nghỉ và có yêu cầu tạo mặc định
    if not holidays and year:
        create_default_holidays(db, current_user.id, year)
        holidays = db.query(Holiday).filter(Holiday.user_id == current_user.id).all()
    
    return holidays


@router.post("/create-default")
def create_default_holidays_for_user(
    year: int = Query(..., description="Năm để tạo ngày nghỉ mặc định"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = create_default_holidays(db, current_user.id, year)
    return {"message": f"Đã tạo {count} ngày nghỉ lễ mặc định", "count": count}


@router.post("", response_model=HolidayResponse, status_code=201)
def create_holiday(
    holiday_data: HolidayCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    holiday_date = datetime.strptime(holiday_data.holiday_date, "%Y-%m-%d").date()
    moved_to_date = None
    if holiday_data.moved_to_date:
        moved_to_date = datetime.strptime(holiday_data.moved_to_date, "%Y-%m-%d").date()
    
    new_holiday = Holiday(
        user_id=current_user.id,
        holiday_date=holiday_date,
        holiday_name=holiday_data.holiday_name,
        is_moved=holiday_data.is_moved,
        moved_to_date=moved_to_date,
    )
    db.add(new_holiday)
    db.commit()
    db.refresh(new_holiday)
    logger.info("Holiday created", holiday_id=new_holiday.id, user_id=current_user.id)
    return new_holiday


@router.delete("/{holiday_id}", status_code=204)
def delete_holiday(
    holiday_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    holiday = db.query(Holiday).filter(
        Holiday.id == holiday_id,
        Holiday.user_id == current_user.id,
    ).first()
    
    if holiday:
        db.delete(holiday)
        db.commit()
        logger.info("Holiday deleted", holiday_id=holiday_id, user_id=current_user.id)
    return None

