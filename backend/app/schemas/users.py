from pydantic import EmailStr, BaseModel

class UserCreate(BaseModel):
    username: str 
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    
    
class UserResponce(BaseModel):
    id: int 
    username : str
    email: EmailStr
    first_name: str
    last_name: str
    
    
    model_config = {
        "from_attributes": True
    }
    
 
    
class UserLogin(BaseModel):
    username: str
    password: str
    
    
    
class UserUpdate(BaseModel):
    
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    
    
    
    
    
class Token(BaseModel):
    access_token: str
    token_type: str
    