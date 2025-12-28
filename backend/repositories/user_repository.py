from sqlalchemy.orm import Session
from typing import Optional
from models import User
from core.exceptions import NotFoundException, ConflictException
from core.logging_config import get_logger

logger = get_logger(__name__)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_first_user(self) -> Optional[User]:
        return self.db.query(User).first()
    
    def create(self, user_data: dict) -> User:
        existing_user = self.get_by_username(user_data["username"])
        if existing_user:
            raise ConflictException(f"Username {user_data['username']} already exists")
        
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info("User created", user_id=user.id, username=user.username)
        return user
    
    def update(self, user_id: int, user_data: dict) -> User:
        user = self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        for key, value in user_data.items():
            setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        logger.info("User updated", user_id=user.id)
        return user
    
    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        self.db.delete(user)
        self.db.commit()
        logger.info("User deleted", user_id=user_id)
        return True


