from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException, Depends

from app.models.users import User
from app.models.tasks import Task
from app.schemas.tasks import TaskCreate, TaskUpdate, TaskFilter, TaskListResponce
from app.core.exceptions import TaskNotFoundExceptions
from app.repositories.task import TaskRepository

class TaskService:
    
    def __init__(self, db: Session, repository: TaskRepository):
        self.db = db
        self.task_repository = repository
    
    def create_task(self, task:TaskCreate):
        
        return self.task_repository.create(task)
          

    def get_tasks(self,task_filter: TaskFilter,):
        tasks = self.task_repository.get_tasks(task_filter)
        return tasks


    def get_task(self,task_id: int,):
        task = self.task_repository.get_by_id(task_id)
        
        if task is None:
            raise TaskNotFoundExceptions()
        
        return task
        

    def update_task(
        self,
        task_id: int,
        task_data: TaskUpdate,
    ):
        task = self.task_repository.get_by_id(task_id)
        
        if task is None:
            raise TaskNotFoundExceptions()
        
        update_data = task_data.model_dump(exclude_unset=True)

        
        return self.task_repository.update(task_id, update_data)
        

    def delete_task(self,task_id: int,):
        task = self.task_repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundExceptions()
        else:
            self.task_repository.delete(task_id)

        
        