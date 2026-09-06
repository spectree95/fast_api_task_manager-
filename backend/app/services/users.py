from sqlalchemy.orm import Session
from sqlalchemy import select

from fastapi import HTTPException, status

from app.core.security import hash_password, create_access_token,verify_password
from app.models.users import User
from app.schemas.users import UserCreate, UserLogin, UserUpdate






def create_user(
    db: Session,
    user: UserCreate
):
    existing_username = db.execute(
        select(User).where(User.username == user.username)
    ).scalar_one_or_none()
    
    
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists.")
    
    existing_email = db.execute(
        select(User).where(User.email == user.email)
    ).scalar_one_or_none()
    
    
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists.")
    
    hashed_password = hash_password(user.password)
    
    db_user = User(
        username = user.username,
        email = user.email,
        password = hashed_password,
        first_name = user.first_name,
        last_name = user.last_name,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def login_user(
    db: Session,
    user:UserLogin
):
    
    db_user = db.execute(
        select(User).where(User.username==user.username)
        ).scalar_one_or_none()

        
    if not db_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
    
    
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
    
    
    access_token = create_access_token(
        data={
            "sub": str(db_user.id)
        }
    )
    
    return {"access_token":access_token, "token_type": "bearer"}


def update_user(
    user_data: UserUpdate,
    db: Session,
    current_user: User
):
    existing_username = db.execute(select(User).where(
        User.username == user_data.username
    )).scalar_one_or_none()
    
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already exists.')
    
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)    
    
    db.commit()
    db.refresh(current_user)
    
    return current_user



def delete_user(
    db:Session,
    current_user: User,
):
    db.delete(current_user)
    db.commit()
    