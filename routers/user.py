from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user
from models.user_model import User

router = APIRouter()

@router.get("/users/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "name": current_user.name,
        "provider": current_user.provider
    }
