from datetime import datetime

from app.models.users import User 
from pydantic import BaseModel, Field
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
    
    
class TaskFilter(BaseModel):
    skip: int = Field(0, ge=0),
    limit: int = Field(10, ge=1, le=100),
    completed: bool | None = None,
    sort: SortField = SortField.created_at,
    order: OrderField = OrderField.desc,
    