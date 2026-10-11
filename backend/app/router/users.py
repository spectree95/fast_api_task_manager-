from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from fastapi.security import OAuth2PasswordRequestForm

from app.services.users import UserService
from app.core.database import get_db
from app.dependencies.auth import get_current_user, get_user_service
from app.models.users import User
from app.schemas.users import UserCreate, UserResponce, UserLogin, Token, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])





@router.post("/", response_model=UserResponce,status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        return service.create_user(user_data)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
    


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    service: UserService = Depends(get_user_service)
): 
    return service.login_user(form_data)
    


    
@router.get("/me", response_model=UserResponce)
def me(
    current_user:User = Depends(get_current_user),
):
    return current_user




@router.patch("/", response_model=UserResponce)
def update(
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),  
):
        
    try:
        return service.update_user(user_data=user_data, current_user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        
    
    
    
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    service.delete_user(current_user)