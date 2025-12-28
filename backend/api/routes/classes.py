from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_current_user, get_db
from models import User, Class
from schemas import ClassCreate, ClassResponse
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("", response_model=list[ClassResponse])
def get_classes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    classes = db.query(Class).filter(Class.user_id == current_user.id).all()
    return classes


@router.post("", response_model=ClassResponse, status_code=201)
def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_class = Class(
        user_id=current_user.id,
        class_name=class_data.class_name,
        grade=class_data.grade,
        school_year=class_data.school_year,
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    logger.info("Class created", class_id=new_class.id, user_id=current_user.id)
    return new_class


@router.delete("/{class_id}", status_code=204)
def delete_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    class_obj = db.query(Class).filter(
        Class.id == class_id,
        Class.user_id == current_user.id,
    ).first()
    
    if class_obj:
        db.delete(class_obj)
        db.commit()
        logger.info("Class deleted", class_id=class_id, user_id=current_user.id)
    return None

