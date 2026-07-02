"""Authentication API routes."""

from fastapi import APIRouter, HTTPException, status

from app.auth import authenticate_user, create_access_token, get_allowed_departments
from app.models.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    role = user["role"]
    token = create_access_token(user["username"], role)

    return LoginResponse(
        access_token=token,
        username=user["username"],
        role=role.value,
        display_name=user["display_name"],
        allowed_departments=get_allowed_departments(role),
    )
