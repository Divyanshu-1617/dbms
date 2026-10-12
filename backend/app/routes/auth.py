from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from ..models import UserCreate, UserLogin, UserResponse, UserVerifyRequest
from ..services import create_user, get_all_users, get_user_by_id, get_user_by_email, update_user_verification

router = APIRouter(prefix="/api/users", tags=["Users & Authentication"])


@router.get("", response_model=List[UserResponse])
def list_users():
    return get_all_users()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    existing = get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")
    return create_user(user_data.model_dump())


@router.post("/login", response_model=UserResponse)
def login(creds: UserLogin):
    user = get_user_by_email(creds.email)
    if not user or user["password"] != creds.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user["account_status"] == "Suspended":
        raise HTTPException(status_code=403, detail="Account is suspended")
    return user


@router.put("/admin/{user_id}/verify", response_model=UserResponse)
def verify_user(user_id: str, req: UserVerifyRequest):
    """Admin endpoint to verify owner/tourist KYC (Scenario 9.10)"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return update_user_verification(user_id, req.verification_status, req.account_status)
