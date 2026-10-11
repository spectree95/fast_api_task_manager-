from fastapi import Depends
from sqlalchemy.orm import Session

from app.repositories.task import TaskRepository
from app.models.users import User
from app.services.tasks import TaskService
from .auth import get_current_user
from app.core.database import get_db

def get_task_repository(
    db:Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TaskRepository(db, current_user)


def get_task_service(db:Session = Depends(get_db), repository: TaskRepository = Depends(get_task_repository)):
    return TaskService(db,repository)