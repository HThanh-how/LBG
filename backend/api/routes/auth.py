from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from services.auth_service import AuthService, get_auth_service
from schemas import UserCreate, UserResponse, Token
from api.dependencies import get_current_user
from models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    user: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.register(user)


@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.authenticate(form_data.username, form_data.password)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return current_user
