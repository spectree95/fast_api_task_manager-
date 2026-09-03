from datetime import datetime

from app.models.users import User 
from pydantic import BaseModel
from enum import Enum

class TaskCreate(BaseModel):
    
    title: str 
    description: str
   
   
   
   
    
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    owner_id: int
    
    model_config = {
        "from_attributes": True
    }
   

class TaskListResponce(BaseModel):
    items: list[TaskResponse]
    total: int
    skip: int
    limit: int    
    
    
class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    
    
class SortField(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    title = "title"
    

class OrderField(str, Enum):
    asc = "asc"
    desc = "desc"
    
    