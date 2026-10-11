
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate

from sqlalchemy.orm import Session
from sqlalchemy import select,or_
from app.core.security import hash_password




class UserRepository:
    
    def __init__(self, db: Session):
        self.db = db
        
    
    
    def get_user(self, username: str):
        return (
            self.db.query(User)
            .filter(User.username == username)
            .first()
        )


    def get_user_by_email(self, email: str):
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )
    
        
    def create(self, user_create: UserCreate):
        user_data = user_create.model_dump(exclude={"password"})
        user_data["password"] = hash_password(user_create.password)
        db_user = User(**user_data)
            
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
        
    
    
    def update(self,user_data: UserUpdate, current_user: User):
        for field, value in user_data.items():
            setattr(current_user, field, value)    
            self.db.commit()
            self.db.refresh(current_user)
        return current_user                
    
    
    def delete(self,current_user):
        self.db.delete(current_user)
        self.db.commit()