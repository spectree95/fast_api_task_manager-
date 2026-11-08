from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException, Depends

from app.models.users import User
from app.models.tasks import Task
from app.schemas.tasks import TaskCreate, TaskUpdate, TaskFilter, TaskListResponce, TaskResponse
from app.core.exceptions import TaskNotFoundExceptions
from app.repositories.task import TaskRepository
from app.core.config import settings
from app.cache.cache import RedisCacheBackend 
import json



class TaskService:
    
    def __init__(self, db: Session, repository: TaskRepository):
        self.db = db
        self.task_repository = repository
        self.redis = RedisCacheBackend(settings.REDIS_URL, settings.CACHE_TTL_SECONDS)
        self.cache_prefix = f"{settings.CACHE_TASKS_KEY}:user:{repository.current_user.id}:"
    
    def create_task(self, task:TaskCreate):
        
        created = self.task_repository.create(task)
        self.redis.delete_prefix(self.cache_prefix)
        return created
          

    def get_tasks(self,task_filter: TaskFilter):
        cache_key = self.cache_prefix + "list:" + task_filter.model_dump_json()
        cached_tasks = self.redis.get(cache_key)
        if cached_tasks is not None:
            return cached_tasks
        
        tasks = self.task_repository.get_tasks(task_filter)
        self.redis.set(cache_key, tasks.model_dump(mode="json"))
        
        return tasks


    def get_task(self,task_id: int,):
        
        cache_key = self.cache_prefix + f"task:{task_id}"
        cached_task = self.redis.get(cache_key)
        if cached_task is not None:
            return cached_task

        task = self.task_repository.get_by_id(task_id)
        
        if task is None:
            raise TaskNotFoundExceptions()
        
        self.redis.set(cache_key, TaskResponse.model_validate(task).model_dump(mode="json"))
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

        
        updated = self.task_repository.update(task_id, update_data)
        self.redis.delete_prefix(self.cache_prefix)
        return updated
        

    def delete_task(self,task_id: int,):
        task = self.task_repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundExceptions()
        else:
            self.task_repository.delete(task_id)
            self.redis.delete_prefix(self.cache_prefix)

        
        
