from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import timedelta

from core.database import get_db
from core.security import verify_password, get_password_hash, create_access_token
from core.config import settings
from core.exceptions import UnauthorizedException, ConflictException
from repositories.user_repository import UserRepository
from schemas import UserCreate, UserResponse
from core.logging_config import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register(self, user_data: UserCreate) -> UserResponse:
        hashed_password = get_password_hash(user_data.password)
        
        user_dict = {
            "username": user_data.username,
            "password_hash": hashed_password,
            "full_name": user_data.full_name,
            "school_name": user_data.school_name,
        }
        
        user = self.user_repo.create(user_dict)
        logger.info("User registered", username=user.username, user_id=user.id)
        return UserResponse.model_validate(user)
    
    def authenticate(self, username: str, password: str) -> dict:
        user = self.user_repo.get_by_username(username)
        
        if not user or not verify_password(password, user.password_hash):
            logger.warning("Authentication failed", username=username)
            raise UnauthorizedException("Incorrect username or password")
        
        access_token = create_access_token(data={"sub": user.username})
        logger.info("User authenticated", username=username, user_id=user.id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
    
    def get_current_user(self, username: str):
        user = self.user_repo.get_by_username(username)
        if not user:
            raise UnauthorizedException("User not found")
        return user


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

