from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from app.dependencies.task import get_task_service
from app.schemas.tasks import TaskCreate, TaskResponse, TaskListResponce, TaskUpdate, TaskFilter
from app.services.tasks import TaskService


router = APIRouter(prefix="/tasks", tags=["Tasks"],)


@router.post("/create", response_model=TaskResponse)
def create(
    task: TaskCreate,
    service: TaskService = Depends(get_task_service)
):
    return service.create_task(task)


@router.get("", response_model=TaskListResponce)
def tasks(
    task_filters: Annotated[TaskFilter, Query()],
    service: TaskService = Depends(get_task_service),
):
    return service.get_tasks(task_filters)



    
@router.get("/{task_id}", response_model=TaskResponse)
def get_one_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
):
    return service.get_task(task_id)
    
    
@router.patch("/{task_id}", response_model=TaskResponse)
def update(
    task_id: int,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service)
):
    return service.update_task(task_id=task_id, task_data=task_data,)
    
    
    
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    task_id: int,
    service: TaskService = Depends(get_task_service)
):
    service.delete_task(task_id)
