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
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise UnauthorizedException("Invalid token")
    except JWTError:
        raise UnauthorizedException("Could not validate credentials")
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(username)
    if user is None:
        raise UnauthorizedException("User not found")
    return user

