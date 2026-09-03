from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.services.users import create_user, login_user, update_user, delete_user
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.users import User
from app.schemas.users import UserCreate, UserResponce, UserLogin, Token, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])



@router.post("/register", response_model=UserResponce,status_code=status.HTTP_201_CREATED)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return create_user(db, user)
    

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    return login_user(db, form_data)
    
    
@router.get("/me", response_model=UserResponce)
def me(
    current_user:User = Depends(get_current_user),
):
    return current_user

@router.patch("/", response_model=UserResponce)
def update(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  
):
    return update_user(
        user_data=user_data,
        db=db,
        current_user=current_user,
    )
    
    
    
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_user(
        db=db,
        current_user=current_user,
    )