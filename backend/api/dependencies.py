from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from core.database import get_db
from core.security import decode_access_token
from core.exceptions import UnauthorizedException
from repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    db: Session = Depends(get_db),
    # token: str = Depends(oauth2_scheme),  # TẠM THỜI TẮT AUTHENTICATION
):
    # TẠM THỜI TẮT AUTHENTICATION - Bypass token check
    # try:
    #     payload = decode_access_token(token)
    #     username: str = payload.get("sub")
    #     if username is None:
    #         raise UnauthorizedException("Invalid token")
    # except JWTError:
    #     raise UnauthorizedException("Could not validate credentials")
    
    user_repo = UserRepository(db)
    # Lấy user đầu tiên hoặc tạo user mặc định
    user = user_repo.get_first_user()
    if user is None:
        # Tạo user mặc định nếu chưa có
        from models import User
        from core.security import get_password_hash
        default_user = User(
            username="default",
            password_hash=get_password_hash("default"),
            full_name="Default User",
            school_name="Default School"
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
        return default_user
    return user


