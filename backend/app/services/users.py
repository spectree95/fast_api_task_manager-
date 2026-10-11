from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from fastapi import HTTPException, status

from app.core.security import hash_password, create_access_token,verify_password
from app.models.users import User
from app.schemas.users import UserCreate, UserLogin, UserUpdate
from fastapi.security import OAuth2PasswordRequestForm
from app.repositories.users import UserRepository


class UserService:


    def __init__(self, db:Session, repository: UserRepository):
        self.db = db
        self.user_repository = repository


    def get_user(self,username,email):
        return self.user_repository.get_user(username=username, email=email)


    def create_user(self,user_data: UserCreate):
        existing_username = self.user_repository.get_user(username=user_data.username)

        if existing_username:
            raise ValueError("Username already exists.")

        existing_email = self.user_repository.get_user_by_email(email=user_data.email)

        if existing_email:
            raise ValueError("This email address is already in use.")
        
        return self.user_repository.create(user_data)
        


    def login_user(self,form_data: OAuth2PasswordRequestForm):
        
        db_user = self.user_repository.get_user(username=form_data.username)

            
        if not db_user:
            raise ValueError(status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
        
        
        if not verify_password(form_data.password, db_user.password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
        
        
        access_token = create_access_token(
            data={
                "sub": str(db_user.id)
            }
        )
        
        return {"access_token":access_token, "token_type": "bearer"}


    def update_user(
        self,
        user_data: UserUpdate,
        current_user: User
    ):
        user = self.user_repository.get_user(user_data.username)
        if user:
            raise ValueError("Username already exists.")
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return current_user
        
        
        return self.user_repository.update(user_data=update_data, current_user=current_user)



    def delete_user(self,current_user: User,):
        self.user_repository.delete(current_user)
        